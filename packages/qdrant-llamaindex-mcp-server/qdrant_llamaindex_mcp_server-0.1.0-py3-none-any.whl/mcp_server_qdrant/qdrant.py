import logging
import uuid
from typing import Any

from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient, models

from mcp_server_qdrant.embeddings.base import EmbeddingProvider
from mcp_server_qdrant.embeddings.factory import create_embedding_provider
from mcp_server_qdrant.settings import EmbeddingProviderSettings

logger = logging.getLogger(__name__)

Metadata = dict[str, Any]
ArbitraryFilter = dict[str, Any]


class Entry(BaseModel):
    """
    A single entry in the Qdrant collection.
    """

    id: str | None = None
    content: str
    metadata: Metadata | None = None


class QdrantConnector:
    """
    Encapsulates the connection to a Qdrant server and all the methods to interact with it.
    :param qdrant_url: The URL of the Qdrant server.
    :param qdrant_api_key: The API key to use for the Qdrant server.
    :param collection_name: The name of the default collection to use. If not provided, each tool will require
                            the collection name to be provided.
    :param embedding_provider: The embedding provider to use.
    :param qdrant_local_path: The path to the storage directory for the Qdrant client, if local mode is used.
    """

    def __init__(
        self,
        qdrant_url: str | None,
        qdrant_api_key: str | None,
        collection_name: str | None,
        embedding_provider: EmbeddingProvider,
        embedding_provider_settings: EmbeddingProviderSettings,
        qdrant_local_path: str | None = None,
        field_indexes: dict[str, models.PayloadSchemaType] | None = None,
    ):
        self._qdrant_url = qdrant_url.rstrip("/") if qdrant_url else None
        self._qdrant_api_key = qdrant_api_key
        self._default_collection_name = collection_name
        self._embedding_provider = embedding_provider  # Default provider
        self._embedding_provider_settings = embedding_provider_settings
        self._client = AsyncQdrantClient(
            location=qdrant_url, api_key=qdrant_api_key, path=qdrant_local_path
        )
        self._field_indexes = field_indexes
        # Cache for dynamic embedding providers
        self._provider_cache: dict[str, EmbeddingProvider] = {}

    def _is_model_allowed(self, model_name: str) -> bool:
        """
        Check if a model is allowed based on the whitelist configuration.
        :param model_name: The model name to check.
        :return: True if allowed, False otherwise.
        """
        # If no whitelist is configured, allow all models
        if self._embedding_provider_settings.allowed_models is None:
            return True
        
        # Check if model is in the allowed list
        return model_name in self._embedding_provider_settings.allowed_models

    async def _get_embedding_provider_for_collection(self, collection_name: str) -> EmbeddingProvider:
        """
        Get the appropriate embedding provider for a specific collection based on its vector configuration.
        :param collection_name: The name of the collection.
        :return: The embedding provider for the collection.
        """
        try:
            # Check if collection exists
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                # Collection doesn't exist, use default provider
                return self._embedding_provider

            # Get collection details to inspect vector configuration
            collection_info = await self._client.get_collection(collection_name)
            collection_dict = collection_info.model_dump()
            
            # Extract vector names from the configuration
            vectors_config = collection_dict.get("config", {}).get("params", {}).get("vectors", {})
            if not vectors_config:
                # No vector config found, use default provider
                return self._embedding_provider

            # Get the first vector name (assuming single vector per collection for now)
            vector_names = list(vectors_config.keys())
            if not vector_names:
                return self._embedding_provider

            model_name = vector_names[0]  # The vector name is the full model name
            
            # Check if model is allowed (whitelist validation)
            if not self._is_model_allowed(model_name):
                logger.warning(f"Model {model_name} not in allowed models list. Using default provider.")
                return self._embedding_provider
            
            # Check cache first
            if model_name in self._provider_cache:
                return self._provider_cache[model_name]

            # Create new provider for this model
            provider_settings = EmbeddingProviderSettings(
                provider_type=self._embedding_provider_settings.provider_type,
                model_name=model_name
            )
            provider = create_embedding_provider(provider_settings)
            
            # Cache the provider
            self._provider_cache[model_name] = provider
            return provider

        except Exception as e:
            logger.warning(f"Failed to detect model for collection {collection_name}: {e}. Using default provider.")
            return self._embedding_provider

    async def get_collection_names(self) -> list[str]:
        """
        Get the names of all collections in the Qdrant server.
        :return: A list of collection names.
        """
        response = await self._client.get_collections()
        return [collection.name for collection in response.collections]

    async def get_collection_details(self, collection_name: str) -> dict[str, Any]:
        """
        Get detailed information about a specific collection.
        :param collection_name: The name of the collection to get details for.
        :return: A dictionary containing collection details.
        """
        collection_info = await self._client.get_collection(collection_name)
        return collection_info.model_dump()

    async def store(self, entry: Entry, *, collection_name: str | None = None):
        """
        Store some information in the Qdrant collection, along with the specified metadata.
        :param entry: The entry to store in the Qdrant collection.
        :param collection_name: The name of the collection to store the information in, optional. If not provided,
                                the default collection is used.
        """
        collection_name = collection_name or self._default_collection_name
        assert collection_name is not None
        await self._ensure_collection_exists(collection_name)

        # Embed the document
        # ToDo: instead of embedding text explicitly, use `models.Document`,
        # it should unlock usage of server-side inference.
        embeddings = await self._embedding_provider.embed_documents([entry.content])

        point_id = uuid.uuid4().hex if entry.id is None else entry.id
        # Add to Qdrant
        vector_name = self._embedding_provider.get_vector_name()
        payload = {"document": entry.content, "metadata": entry.metadata}
        await self._client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector={vector_name: embeddings[0]},
                    payload=payload,
                )
            ],
        )

    async def search(
        self,
        query: str,
        *,
        collection_name: str | None = None,
        limit: int = 10,
        query_filter: models.Filter | None = None,
    ) -> list[Entry]:
        """
        Find points in the Qdrant collection. If there are no entries found, an empty list is returned.
        :param query: The query to use for the search.
        :param collection_name: The name of the collection to search in, optional. If not provided,
                                the default collection is used.
        :param limit: The maximum number of entries to return.
        :param query_filter: The filter to apply to the query, if any.

        :return: A list of entries found.
        """
        collection_name = collection_name or self._default_collection_name
        if collection_name is None:
            return []
        collection_exists = await self._client.collection_exists(collection_name)
        if not collection_exists:
            return []

        # Embed the query using the appropriate provider for this collection
        # ToDo: instead of embedding text explicitly, use `models.Document`,
        # it should unlock usage of server-side inference.
        
        provider = await self._get_embedding_provider_for_collection(collection_name)
        query_vector = await provider.embed_query(query)
        vector_name = provider.get_vector_name()

        # Search in Qdrant
        search_results = await self._client.query_points(
            collection_name=collection_name,
            query=query_vector,
            using=vector_name,
            limit=limit,
            query_filter=query_filter,
        )

        entries = []
        for result in search_results.points:
            # Try to extract content from common field names used by different systems
            content = None
            payload = result.payload
            
            # Try different content field names in order of preference
            content_fields = ["document", "text", "_node_content", "content"]
            for field in content_fields:
                if field in payload:
                    content = payload[field]
                    break
            
            # If no content field found, look for the largest string value as likely content
            if content is None:
                string_values = {k: v for k, v in payload.items() 
                               if isinstance(v, str) and len(v) > 50}
                if string_values:
                    # Get the field with the longest string value
                    content_field = max(string_values.keys(), key=lambda k: len(string_values[k]))
                    content = string_values[content_field]
            
            # Extract metadata (everything except the content field and system fields)
            system_fields = {"document", "text", "_node_content", "content", "metadata"}
            metadata = {k: v for k, v in payload.items() 
                       if k not in system_fields or (k == "metadata" and isinstance(v, dict))}
            
            # If there's a nested metadata field, merge it
            if "metadata" in payload and isinstance(payload["metadata"], dict):
                metadata.update(payload["metadata"])
                # Remove the nested metadata field from the flat metadata
                metadata.pop("metadata", None)
            
            if content is not None:
                entries.append(Entry(
                    id=str(result.id),
                    content=content if content else "",
                    metadata=metadata if metadata else None
                ))
        
        return entries

    async def _ensure_collection_exists(self, collection_name: str):
        """
        Ensure that the collection exists, creating it if necessary.
        :param collection_name: The name of the collection to ensure exists.
        """
        collection_exists = await self._client.collection_exists(collection_name)
        if not collection_exists:
            # Create the collection with the appropriate vector size
            vector_size = self._embedding_provider.get_vector_size()

            # Use the vector name as defined in the embedding provider
            vector_name = self._embedding_provider.get_vector_name()
            await self._client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    vector_name: models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    )
                },
            )

            # Create payload indexes if configured

            if self._field_indexes:
                for field_name, field_type in self._field_indexes.items():
                    await self._client.create_payload_index(
                        collection_name=collection_name,
                        field_name=field_name,
                        field_schema=field_type,
                    )

    async def get_point_by_id(
        self,
        point_id: str,
        *,
        collection_name: str | None = None,
    ) -> Entry | None:
        """
        Retrieve a specific point by its ID.
        :param point_id: The ID of the point to retrieve.
        :param collection_name: The name of the collection, optional.
        :return: The entry if found, None otherwise.
        """
        collection_name = collection_name or self._default_collection_name
        assert collection_name is not None

        point = await self._client.retrieve(
            collection_name=collection_name,
            ids=[point_id],
            with_payload=True,
            with_vectors=False,
        )

        if point and len(point) > 0:
            result = point[0]
            return Entry(
                id=str(result.id),
                content=result.payload["document"] if result.payload else "",
                metadata=result.payload.get("metadata") if result.payload else None,
            )
        return None

    async def delete_point_by_id(
        self,
        point_id: str,
        *,
        collection_name: str | None = None,
    ) -> bool:
        """
        Delete a specific point by its ID.
        :param point_id: The ID of the point to delete.
        :param collection_name: The name of the collection, optional.
        :return: True if the point was deleted, False if not found.
        """
        collection_name = collection_name or self._default_collection_name
        assert collection_name is not None

        collection_exists = await self._client.collection_exists(collection_name)
        if not collection_exists:
            return False

        # Check if point exists before trying to delete
        existing_point = await self.get_point_by_id(
            point_id, collection_name=collection_name
        )
        if existing_point is None:
            return False

        try:
            await self._client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=[point_id]),
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete point {point_id}: {e}")
            return False

    async def update_point_payload(
        self,
        point_id: str,
        metadata: Metadata,
        *,
        collection_name: str | None = None,
    ) -> bool:
        """
        Update the payload (metadata) of a specific point by its ID.
        :param point_id: The ID of the point to update.
        :param metadata: New metadata to set for the point.
        :param collection_name: The name of the collection, optional.
        :return: True if the point was updated, False if not found.
        """
        collection_name = collection_name or self._default_collection_name
        assert collection_name is not None

        collection_exists = await self._client.collection_exists(collection_name)
        if not collection_exists:
            return False

        # Check if point exists before trying to update
        existing_point = await self.get_point_by_id(
            point_id, collection_name=collection_name
        )
        if existing_point is None:
            return False

        try:
            await self._client.set_payload(
                collection_name=collection_name,
                payload={"metadata": metadata},
                points=[point_id],
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update payload for point {point_id}: {e}")
            return False

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int | None = None,
        distance: models.Distance = models.Distance.COSINE,
    ) -> bool:
        """
        Create a new collection with vector configuration.
        :param collection_name: The name of the collection to create.
        :param vector_size: The size of the vectors. If not provided, uses embedding provider's size.
        :param distance: The distance metric to use for vectors.
        :return: True if the collection was created, False if it already exists.
        """
        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if collection_exists:
                return False

            if vector_size is None:
                vector_size = self._embedding_provider.get_vector_size()

            vector_name = self._embedding_provider.get_vector_name()
            await self._client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    vector_name: models.VectorParams(
                        size=vector_size,
                        distance=distance,
                    )
                },
            )

            # Create payload indexes if configured
            if self._field_indexes:
                for field_name, field_type in self._field_indexes.items():
                    await self._client.create_payload_index(
                        collection_name=collection_name,
                        field_name=field_name,
                        field_schema=field_type,
                    )
            
            return True
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection entirely.
        :param collection_name: The name of the collection to delete.
        :return: True if the collection was deleted, False if it doesn't exist.
        """
        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                return False

            await self._client.delete_collection(collection_name)
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    async def get_collection_count(self, collection_name: str) -> int | None:
        """
        Get the number of points in a collection.
        :param collection_name: The name of the collection.
        :return: The number of points or None if collection doesn't exist.
        """
        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                return None

            collection_info = await self._client.get_collection(collection_name)
            return collection_info.points_count
        except Exception as e:
            logger.error(f"Failed to get collection count for {collection_name}: {e}")
            return None

    async def peek_collection(
        self,
        collection_name: str,
        limit: int = 10
    ) -> list[Entry]:
        """
        Preview sample points from a collection.
        :param collection_name: The name of the collection.
        :param limit: The maximum number of points to return.
        :return: A list of entries or empty list if collection doesn't exist.
        """
        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                return []

            # Use scroll to get random sample points
            points, _ = await self._client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )

            entries = []
            for point in points:
                # Use the same content extraction logic as search
                content = None
                payload = point.payload
                
                # Try different content field names in order of preference
                content_fields = ["document", "text", "_node_content", "content"]
                for field in content_fields:
                    if field in payload:
                        content = payload[field]
                        break
                
                # If no content field found, look for the largest string value as likely content
                if content is None:
                    string_values = {k: v for k, v in payload.items() 
                                   if isinstance(v, str) and len(v) > 50}
                    if string_values:
                        # Get the field with the longest string value
                        content_field = max(string_values.keys(), key=lambda k: len(string_values[k]))
                        content = string_values[content_field]
                
                # Extract metadata (everything except the content field and system fields)
                system_fields = {"document", "text", "_node_content", "content", "metadata"}
                metadata = {k: v for k, v in payload.items() 
                           if k not in system_fields or (k == "metadata" and isinstance(v, dict))}
                
                # If there's a nested metadata field, merge it
                if "metadata" in payload and isinstance(payload["metadata"], dict):
                    metadata.update(payload["metadata"])
                    # Remove the nested metadata field from the flat metadata
                    metadata.pop("metadata", None)
                
                if content is not None:
                    entries.append(Entry(
                        id=str(point.id),
                        content=content,
                        metadata=metadata if metadata else None
                    ))

            return entries
        except Exception as e:
            logger.error(f"Failed to peek collection {collection_name}: {e}")
            return []

    async def get_documents(
        self,
        point_ids: list[str],
        *,
        collection_name: str | None = None,
    ) -> list[Entry]:
        """
        Retrieve multiple documents by their IDs.
        :param point_ids: List of point IDs to retrieve.
        :param collection_name: The name of the collection, optional.
        :return: List of entries found.
        """
        collection_name = collection_name or self._default_collection_name
        if collection_name is None:
            return []

        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                return []

            points = await self._client.retrieve(
                collection_name=collection_name,
                ids=point_ids,
                with_payload=True,
                with_vectors=False,
            )

            entries = []
            for point in points:
                # Use the same content extraction logic as search
                content = None
                payload = point.payload
                
                # Try different content field names in order of preference
                content_fields = ["document", "text", "_node_content", "content"]
                for field in content_fields:
                    if field in payload:
                        content = payload[field]
                        break
                
                # If no content field found, look for the largest string value as likely content
                if content is None:
                    string_values = {k: v for k, v in payload.items() 
                                   if isinstance(v, str) and len(v) > 50}
                    if string_values:
                        # Get the field with the longest string value
                        content_field = max(string_values.keys(), key=lambda k: len(string_values[k]))
                        content = string_values[content_field]
                
                # Extract metadata (everything except the content field and system fields)
                system_fields = {"document", "text", "_node_content", "content", "metadata"}
                metadata = {k: v for k, v in payload.items() 
                           if k not in system_fields or (k == "metadata" and isinstance(v, dict))}
                
                # If there's a nested metadata field, merge it
                if "metadata" in payload and isinstance(payload["metadata"], dict):
                    metadata.update(payload["metadata"])
                    # Remove the nested metadata field from the flat metadata
                    metadata.pop("metadata", None)
                
                if content is not None:
                    entries.append(Entry(
                        id=str(point.id),
                        content=content,
                        metadata=metadata if metadata else None
                    ))

            return entries
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            return []

    async def add_documents(
        self,
        entries: list[Entry],
        *,
        collection_name: str | None = None,
    ) -> bool:
        """
        Add multiple documents in batch.
        :param entries: List of entries to add.
        :param collection_name: The name of the collection, optional.
        :return: True if all documents were added successfully.
        """
        collection_name = collection_name or self._default_collection_name
        if collection_name is None:
            return False

        try:
            await self._ensure_collection_exists(collection_name)

            # Embed all documents
            contents = [entry.content for entry in entries]
            embeddings = await self._embedding_provider.embed_documents(contents)

            # Create points
            vector_name = self._embedding_provider.get_vector_name()
            points = []
            for i, entry in enumerate(entries):
                point_id = uuid.uuid4().hex if entry.id is None else entry.id
                payload = {"document": entry.content, "metadata": entry.metadata}
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector={vector_name: embeddings[i]},
                        payload=payload,
                    )
                )

            await self._client.upsert(
                collection_name=collection_name,
                points=points,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    async def delete_documents(
        self,
        point_ids: list[str],
        *,
        collection_name: str | None = None,
    ) -> int:
        """
        Delete multiple documents by their IDs.
        :param point_ids: List of point IDs to delete.
        :param collection_name: The name of the collection, optional.
        :return: Number of documents successfully deleted.
        """
        collection_name = collection_name or self._default_collection_name
        if collection_name is None:
            return 0

        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                return 0

            # Check which points exist before deletion
            existing_points = await self._client.retrieve(
                collection_name=collection_name,
                ids=point_ids,
                with_payload=False,
                with_vectors=False,
            )
            existing_ids = [str(point.id) for point in existing_points]

            if not existing_ids:
                return 0

            await self._client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=existing_ids),
            )
            return len(existing_ids)
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return 0

    async def search_by_vector(
        self,
        vector: list[float],
        *,
        collection_name: str | None = None,
        limit: int = 10,
        query_filter: models.Filter | None = None,
    ) -> list[Entry]:
        """
        Search using a raw vector instead of text query.
        :param vector: The query vector.
        :param collection_name: The name of the collection, optional.
        :param limit: The maximum number of entries to return.
        :param query_filter: The filter to apply to the query, if any.
        :return: A list of entries found.
        """
        collection_name = collection_name or self._default_collection_name
        if collection_name is None:
            return []

        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                return []

            # Get the appropriate provider for vector name detection
            provider = await self._get_embedding_provider_for_collection(collection_name)
            vector_name = provider.get_vector_name()

            # Search in Qdrant
            search_results = await self._client.search(
                collection_name=collection_name,
                query_vector=(vector_name, vector),
                limit=limit,
                query_filter=query_filter,
                with_payload=True,
            )

            entries = []
            for result in search_results:
                # Use the same content extraction logic as search
                content = None
                payload = result.payload
                
                # Try different content field names in order of preference
                content_fields = ["document", "text", "_node_content", "content"]
                for field in content_fields:
                    if field in payload:
                        content = payload[field]
                        break
                
                # If no content field found, look for the largest string value as likely content
                if content is None:
                    string_values = {k: v for k, v in payload.items() 
                                   if isinstance(v, str) and len(v) > 50}
                    if string_values:
                        # Get the field with the longest string value
                        content_field = max(string_values.keys(), key=lambda k: len(string_values[k]))
                        content = string_values[content_field]
                
                # Extract metadata (everything except the content field and system fields)
                system_fields = {"document", "text", "_node_content", "content", "metadata"}
                metadata = {k: v for k, v in payload.items() 
                           if k not in system_fields or (k == "metadata" and isinstance(v, dict))}
                
                # If there's a nested metadata field, merge it
                if "metadata" in payload and isinstance(payload["metadata"], dict):
                    metadata.update(payload["metadata"])
                    # Remove the nested metadata field from the flat metadata
                    metadata.pop("metadata", None)
                
                if content is not None:
                    entries.append(Entry(
                        id=str(result.id),
                        content=content,
                        metadata=metadata if metadata else None
                    ))

            return entries
        except Exception as e:
            logger.error(f"Failed to search by vector: {e}")
            return []

    async def list_document_ids(
        self,
        *,
        collection_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[str]:
        """
        List document IDs with pagination.
        :param collection_name: The name of the collection, optional.
        :param limit: The maximum number of IDs to return.
        :param offset: The number of IDs to skip.
        :return: List of document IDs.
        """
        collection_name = collection_name or self._default_collection_name
        if collection_name is None:
            return []

        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                return []

            # Use scroll to get paginated document IDs
            points, _ = await self._client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=False,
                with_vectors=False,
            )

            return [str(point.id) for point in points]
        except Exception as e:
            logger.error(f"Failed to list document IDs: {e}")
            return []

    async def scroll_points(
        self,
        *,
        collection_name: str | None = None,
        limit: int = 10,
        offset: int | None = None,
    ) -> tuple[list[Entry], int | None]:
        """
        Paginated retrieval of points using scroll.
        :param collection_name: The name of the collection, optional.
        :param limit: The maximum number of points to return.
        :param offset: The offset for pagination.
        :return: Tuple of (entries, next_offset).
        """
        collection_name = collection_name or self._default_collection_name
        if collection_name is None:
            return [], None

        try:
            collection_exists = await self._client.collection_exists(collection_name)
            if not collection_exists:
                return [], None

            points, next_page_offset = await self._client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            entries = []
            for point in points:
                # Use the same content extraction logic as search
                content = None
                payload = point.payload
                
                # Try different content field names in order of preference
                content_fields = ["document", "text", "_node_content", "content"]
                for field in content_fields:
                    if field in payload:
                        content = payload[field]
                        break
                
                # If no content field found, look for the largest string value as likely content
                if content is None:
                    string_values = {k: v for k, v in payload.items() 
                                   if isinstance(v, str) and len(v) > 50}
                    if string_values:
                        # Get the field with the longest string value
                        content_field = max(string_values.keys(), key=lambda k: len(string_values[k]))
                        content = string_values[content_field]
                
                # Extract metadata (everything except the content field and system fields)
                system_fields = {"document", "text", "_node_content", "content", "metadata"}
                metadata = {k: v for k, v in payload.items() 
                           if k not in system_fields or (k == "metadata" and isinstance(v, dict))}
                
                # If there's a nested metadata field, merge it
                if "metadata" in payload and isinstance(payload["metadata"], dict):
                    metadata.update(payload["metadata"])
                    # Remove the nested metadata field from the flat metadata
                    metadata.pop("metadata", None)
                
                if content is not None:
                    entries.append(Entry(
                        id=str(point.id),
                        content=content,
                        metadata=metadata if metadata else None
                    ))

            return entries, next_page_offset
        except Exception as e:
            logger.error(f"Failed to scroll points: {e}")
            return [], None
