import json
import logging
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field
from qdrant_client import models

from mcp_server_qdrant.common.filters import make_indexes
from mcp_server_qdrant.common.func_tools import make_partial_function
from mcp_server_qdrant.common.wrap_filters import wrap_filters
from mcp_server_qdrant.embeddings.factory import create_embedding_provider
from mcp_server_qdrant.qdrant import ArbitraryFilter, Entry, Metadata, QdrantConnector
from mcp_server_qdrant.settings import (
    EmbeddingProviderSettings,
    QdrantSettings,
    ToolSettings,
)

logger = logging.getLogger(__name__)


# FastMCP is an alternative interface for declaring the capabilities
# of the server. Its API is based on FastAPI.
class QdrantMCPServer(FastMCP):
    """
    A MCP server for Qdrant.
    """

    def __init__(
        self,
        tool_settings: ToolSettings,
        qdrant_settings: QdrantSettings,
        embedding_provider_settings: EmbeddingProviderSettings,
        name: str = "mcp-server-qdrant",
        instructions: str | None = None,
        **settings: Any,
    ):
        self.tool_settings = tool_settings
        self.qdrant_settings = qdrant_settings
        self.embedding_provider_settings = embedding_provider_settings

        self.embedding_provider = create_embedding_provider(embedding_provider_settings)
        self.qdrant_connector = QdrantConnector(
            qdrant_settings.location,
            qdrant_settings.api_key,
            qdrant_settings.collection_name,
            self.embedding_provider,
            embedding_provider_settings,
            qdrant_settings.local_path,
            make_indexes(qdrant_settings.filterable_fields_dict()),
        )

        super().__init__(name=name, instructions=instructions, **settings)

        self.setup_tools()

    def format_entry(self, entry: Entry) -> str:
        """
        Feel free to override this method in your subclass to customize the format of the entry.
        """
        entry_metadata = json.dumps(entry.metadata) if entry.metadata else ""
        entry_id = f"<id>{entry.id}</id>" if entry.id else ""
        return f"<entry>{entry_id}<content>{entry.content}</content><metadata>{entry_metadata}</metadata></entry>"

    def setup_tools(self):
        """
        Register the tools in the server.
        """
        async def store(
            ctx: Context,
            id: Annotated[
                str | None,
                Field(description="Point ID. If omitted, a new point is created."),
            ],
            information: Annotated[str, Field(description="Text to store")],
            collection_name: Annotated[
                str, Field(description="The collection to store the information in")
            ],
            # The `metadata` parameter is defined as non-optional, but it can be None.
            # If we set it to be optional, some of the MCP clients, like Cursor, cannot
            # handle the optional parameter correctly.
            metadata: Annotated[
                Metadata | None,
                Field(
                    description="Extra metadata stored along with memorised information. Any json is accepted."
                ),
            ] = None,
        ) -> str:
            """
            Store some information in Qdrant.
            :param ctx: The context for the request.
            :param information: The information to store.
            :param metadata: JSON metadata to store with the information, optional.
            :param collection_name: The name of the collection to store the information in, optional. If not provided,
                                    the default collection is used.
            :return: A message indicating that the information was stored.
            """
            await ctx.debug(f"Storing information {information} in Qdrant")

            entry = Entry(content=information, metadata=metadata, id=id)

            await self.qdrant_connector.store(entry, collection_name=collection_name)
            if collection_name:
                return f"Remembered: {information} in collection {collection_name}"
            return f"Remembered: {information}"

        async def find(
            ctx: Context,
            query: Annotated[str, Field(description="What to search for")],
            collection_name: Annotated[
                str, Field(description="The collection to search in")
            ],
            limit: Annotated[
                int, Field(description="Maximum number of results to return")
            ] = 5,
            offset: Annotated[
                int, Field(description="Number of results to skip for pagination")
            ] = 0,
            score_threshold: Annotated[
                str | float | None, Field(description="Minimum similarity score threshold (0.0 to 1.0). Results below this score will be filtered out.")
            ] = 0.6,
            query_filter: ArbitraryFilter | None = None,
        ) -> list[str]:
            """
            Find memories in Qdrant.
            :param ctx: The context for the request.
            :param query: The query to use for the search.
            :param collection_name: The name of the collection to search in.
            :param limit: The maximum number of results to return (default: 10).
            :param offset: The number of results to skip for pagination (default: 0).
            :param score_threshold: Minimum similarity score threshold. Results below this score will be filtered out.
            :param query_filter: The filter to apply to the query.
            :return: A list of entries found.
            """

            # Log query_filter
            await ctx.debug(f"Query filter: {query_filter}")

            # Convert score_threshold from string to float if needed
            parsed_score_threshold = None
            if score_threshold is not None:
                try:
                    parsed_score_threshold = float(score_threshold)
                except (ValueError, TypeError):
                    return [f"Invalid score_threshold: {score_threshold}. Must be a number between 0.0 and 1.0."]

            parsed_query_filter = (
                models.Filter(**query_filter) if query_filter else None
            )

            await ctx.debug(f"Finding results for query {query}")

            entries = await self.qdrant_connector.search(
                query,
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                score_threshold=parsed_score_threshold,
                query_filter=parsed_query_filter,
            )
            if not entries:
                return [f"No information found for the query '{query}'"]
            content = [
                f"Results for the query '{query}'",
            ]
            for entry in entries:
                content.append(self.format_entry(entry))
            return content

        find_foo = find

        filterable_conditions = (
            self.qdrant_settings.filterable_fields_dict_with_conditions()
        )

        if len(filterable_conditions) > 0:
            find_foo = wrap_filters(find_foo, filterable_conditions)
        elif not self.qdrant_settings.allow_arbitrary_filter:
            find_foo = make_partial_function(find_foo, {"query_filter": None})


        # Add new tools for point operations
        async def get_point(
            ctx: Context,
            point_id: Annotated[
                str, Field(description="The ID of the point to retrieve")
            ],
            collection_name: Annotated[
                str, Field(description="The collection to get the point from")
            ],
        ) -> str:
            """
            Get a specific point by its ID.
            :param ctx: The context for the request.
            :param point_id: The ID of the point to retrieve.
            :param collection_name: The name of the collection to get the point from.
            :return: The point information or error message.
            """
            await ctx.debug(
                f"Getting point {point_id} from collection {collection_name}"
            )

            entry = await self.qdrant_connector.get_point_by_id(
                point_id, collection_name=collection_name
            )

            if entry:
                return self.format_entry(entry)
            else:
                return f"Point with ID {point_id} not found in collection {collection_name}"

        async def delete_point(
            ctx: Context,
            point_id: Annotated[
                str, Field(description="The ID of the point to delete")
            ],
            collection_name: Annotated[
                str, Field(description="The collection to delete the point from")
            ],
        ) -> str:
            """
            Delete a specific point by its ID.
            :param ctx: The context for the request.
            :param point_id: The ID of the point to delete.
            :param collection_name: The name of the collection to delete the point from.
            :return: Success or error message.
            """
            await ctx.debug(
                f"Deleting point {point_id} from collection {collection_name}"
            )

            success = await self.qdrant_connector.delete_point_by_id(
                point_id, collection_name=collection_name
            )

            if success:
                return f"Successfully deleted point {point_id} from collection {collection_name}"
            else:
                return f"Failed to delete point {point_id} - point not found or collection doesn't exist"

        async def update_point_payload(
            ctx: Context,
            point_id: Annotated[
                str, Field(description="The ID of the point to update")
            ],
            collection_name: Annotated[
                str, Field(description="The collection containing the point")
            ],
            metadata: Annotated[
                Metadata,
                Field(
                    description="New metadata to set for the point. Any json is accepted."
                ),
            ],
        ) -> str:
            """
            Update the payload (metadata) of a specific point by its ID.
            :param ctx: The context for the request.
            :param point_id: The ID of the point to update.
            :param collection_name: The name of the collection containing the point.
            :param metadata: New metadata to set for the point.
            :return: Success or error message.
            """
            await ctx.debug(
                f"Updating payload for point {point_id} in collection {collection_name}"
            )

            success = await self.qdrant_connector.update_point_payload(
                point_id, metadata, collection_name=collection_name
            )

            if success:
                return f"Successfully updated payload for point {point_id} in collection {collection_name}"
            else:
                return f"Failed to update payload for point {point_id} - point not found or collection doesn't exist"

        # Add collection management tools
        async def get_collections(ctx: Context) -> list[str]:
            """
            Get a list of all collections in the Qdrant server.
            :param ctx: The context for the request.
            :return: A list of collection names.
            """
            await ctx.debug("Getting list of collections")
            collection_names = await self.qdrant_connector.get_collection_names()
            return collection_names

        async def get_collection_details(
            ctx: Context,
            collection_name: Annotated[
                str, Field(description="The name of the collection to get details for")
            ],
        ) -> str:
            """
            Get detailed information about a specific collection.
            :param ctx: The context for the request.
            :param collection_name: The name of the collection to get details for.
            :return: Detailed information about the collection.
            """
            await ctx.debug(f"Getting details for collection {collection_name}")
            try:
                details = await self.qdrant_connector.get_collection_details(
                    collection_name
                )
                return json.dumps(details, indent=2)
            except Exception as e:
                return f"Error getting collection details: {str(e)}"

        async def create_collection(
            ctx: Context,
            collection_name: Annotated[
                str, Field(description="The name of the collection to create")
            ],
            vector_size: Annotated[
                int | None, Field(description="Vector size. If omitted, uses embedding provider's default.")
            ] = None,
        ) -> str:
            """
            Create a new collection with vector configuration.
            :param ctx: The context for the request.
            :param collection_name: The name of the collection to create.
            :param vector_size: The size of the vectors. If not provided, uses embedding provider's size.
            :return: Success or error message.
            """
            await ctx.debug(f"Creating collection {collection_name}")
            success = await self.qdrant_connector.create_collection(
                collection_name, vector_size=vector_size
            )
            
            if success:
                return f"Successfully created collection {collection_name}"
            else:
                return f"Failed to create collection {collection_name} - it may already exist"

        async def delete_collection(
            ctx: Context,
            collection_name: Annotated[
                str, Field(description="The name of the collection to delete")
            ],
        ) -> str:
            """
            Delete a collection entirely.
            :param ctx: The context for the request.
            :param collection_name: The name of the collection to delete.
            :return: Success or error message.
            """
            await ctx.debug(f"Deleting collection {collection_name}")
            success = await self.qdrant_connector.delete_collection(collection_name)
            
            if success:
                return f"Successfully deleted collection {collection_name}"
            else:
                return f"Failed to delete collection {collection_name} - it may not exist"

        async def get_collection_count(
            ctx: Context,
            collection_name: Annotated[
                str, Field(description="The name of the collection to count")
            ],
        ) -> str:
            """
            Get the number of points in a collection.
            :param ctx: The context for the request.
            :param collection_name: The name of the collection.
            :return: The count or error message.
            """
            await ctx.debug(f"Getting count for collection {collection_name}")
            count = await self.qdrant_connector.get_collection_count(collection_name)
            
            if count is not None:
                return f"Collection {collection_name} contains {count} points"
            else:
                return f"Collection {collection_name} not found"

        async def peek_collection(
            ctx: Context,
            collection_name: Annotated[
                str, Field(description="The name of the collection to peek")
            ],
            limit: Annotated[
                int, Field(description="Maximum number of points to return")
            ] = 5,
        ) -> list[str]:
            """
            Preview sample points from a collection.
            :param ctx: The context for the request.
            :param collection_name: The name of the collection.
            :param limit: The maximum number of points to return.
            :return: A list of formatted entries or error message.
            """
            await ctx.debug(f"Peeking collection {collection_name}")
            entries = await self.qdrant_connector.peek_collection(collection_name, limit=limit)
            
            if not entries:
                return [f"No points found in collection {collection_name} or collection doesn't exist"]
            
            content = [f"Sample points from collection {collection_name}:"]
            for entry in entries:
                content.append(self.format_entry(entry))
            return content

        async def get_documents(
            ctx: Context,
            point_ids: Annotated[
                list[str], Field(description="List of point IDs to retrieve")
            ],
            collection_name: Annotated[
                str, Field(description="The collection to get documents from")
            ],
        ) -> list[str]:
            """
            Retrieve multiple documents by their IDs.
            :param ctx: The context for the request.
            :param point_ids: List of point IDs to retrieve.
            :param collection_name: The name of the collection.
            :return: A list of formatted entries or error message.
            """
            await ctx.debug(f"Getting documents {point_ids} from collection {collection_name}")
            entries = await self.qdrant_connector.get_documents(
                point_ids, collection_name=collection_name
            )
            
            if not entries:
                return [f"No documents found with IDs {point_ids} in collection {collection_name}"]
            
            content = [f"Found {len(entries)} documents:"]
            for entry in entries:
                content.append(self.format_entry(entry))
            return content

        async def add_documents(
            ctx: Context,
            documents: Annotated[
                list[dict[str, Any]], Field(description="List of documents to add. Each document should have 'content' and optionally 'id' and 'metadata'.")
            ],
            collection_name: Annotated[
                str, Field(description="The collection to add documents to")
            ],
        ) -> str:
            """
            Add multiple documents in batch.
            :param ctx: The context for the request.
            :param documents: List of documents to add.
            :param collection_name: The name of the collection.
            :return: Success or error message.
            """
            await ctx.debug(f"Adding {len(documents)} documents to collection {collection_name}")
            
            # Convert dict documents to Entry objects
            entries = []
            for doc in documents:
                if "content" not in doc:
                    return "Error: All documents must have a 'content' field"
                entries.append(Entry(
                    content=doc["content"],
                    id=doc.get("id"),
                    metadata=doc.get("metadata")
                ))
            
            success = await self.qdrant_connector.add_documents(
                entries, collection_name=collection_name
            )
            
            if success:
                return f"Successfully added {len(documents)} documents to collection {collection_name}"
            else:
                return f"Failed to add documents to collection {collection_name}"

        async def delete_documents(
            ctx: Context,
            point_ids: Annotated[
                list[str], Field(description="List of point IDs to delete")
            ],
            collection_name: Annotated[
                str, Field(description="The collection to delete documents from")
            ],
        ) -> str:
            """
            Delete multiple documents by their IDs.
            :param ctx: The context for the request.
            :param point_ids: List of point IDs to delete.
            :param collection_name: The name of the collection.
            :return: Success message with count of deleted documents.
            """
            await ctx.debug(f"Deleting documents {point_ids} from collection {collection_name}")
            deleted_count = await self.qdrant_connector.delete_documents(
                point_ids, collection_name=collection_name
            )
            
            return f"Successfully deleted {deleted_count} out of {len(point_ids)} documents from collection {collection_name}"

        async def search_by_vector(
            ctx: Context,
            vector: Annotated[
                list[float], Field(description="The query vector to search with")
            ],
            collection_name: Annotated[
                str, Field(description="The collection to search in")
            ],
            limit: Annotated[
                int, Field(description="Maximum number of results to return")
            ] = 5,
            query_filter: ArbitraryFilter | None = None,
        ) -> list[str]:
            """
            Search using a raw vector instead of text query.
            :param ctx: The context for the request.
            :param vector: The query vector.
            :param collection_name: The name of the collection to search in.
            :param limit: The maximum number of results to return.
            :param query_filter: The filter to apply to the query.
            :return: A list of entries found.
            """
            await ctx.debug(f"Searching by vector in collection {collection_name}")
            
            parsed_query_filter = (
                models.Filter(**query_filter) if query_filter else None
            )
            
            entries = await self.qdrant_connector.search_by_vector(
                vector,
                collection_name=collection_name,
                limit=limit,
                query_filter=parsed_query_filter,
            )
            
            if not entries:
                return [f"No documents found for vector search in collection '{collection_name}'"]
            
            content = [f"Vector search results in collection '{collection_name}':"]
            for entry in entries:
                content.append(self.format_entry(entry))
            return content

        async def list_document_ids(
            ctx: Context,
            collection_name: Annotated[
                str, Field(description="The collection to list document IDs from")
            ],
            limit: Annotated[
                int, Field(description="Maximum number of IDs to return")
            ] = 100,
            offset: Annotated[
                int, Field(description="Number of IDs to skip for pagination")
            ] = 0,
        ) -> list[str]:
            """
            List document IDs with pagination.
            :param ctx: The context for the request.
            :param collection_name: The name of the collection.
            :param limit: The maximum number of IDs to return.
            :param offset: The number of IDs to skip.
            :return: List of document IDs.
            """
            await ctx.debug(f"Listing document IDs from collection {collection_name}")
            ids = await self.qdrant_connector.list_document_ids(
                collection_name=collection_name,
                limit=limit,
                offset=offset
            )
            
            return ids

        async def scroll_points(
            ctx: Context,
            collection_name: Annotated[
                str, Field(description="The collection to scroll through")
            ],
            limit: Annotated[
                int, Field(description="Maximum number of points to return")
            ] = 5,
            offset: Annotated[
                int | None, Field(description="Offset for pagination")
            ] = None,
        ) -> dict[str, Any]:
            """
            Paginated retrieval of points using scroll.
            :param ctx: The context for the request.
            :param collection_name: The name of the collection.
            :param limit: The maximum number of points to return.
            :param offset: The offset for pagination.
            :return: Dictionary with entries and next_offset.
            """
            await ctx.debug(f"Scrolling points from collection {collection_name}")
            entries, next_offset = await self.qdrant_connector.scroll_points(
                collection_name=collection_name,
                limit=limit,
                offset=offset
            )
            
            formatted_entries = []
            for entry in entries:
                formatted_entries.append(self.format_entry(entry))
            
            return {
                "entries": formatted_entries,
                "next_offset": next_offset,
                "has_more": next_offset is not None
            }

        # Apply collection name defaults and filters to new tools
        get_point_foo = get_point
        delete_point_foo = delete_point
        update_point_payload_foo = update_point_payload
        get_documents_foo = get_documents
        add_documents_foo = add_documents
        delete_documents_foo = delete_documents
        search_by_vector_foo = search_by_vector
        list_document_ids_foo = list_document_ids
        scroll_points_foo = scroll_points

        # Apply filters to search_by_vector like we do for find
        if len(filterable_conditions) > 0:
            search_by_vector_foo = wrap_filters(search_by_vector_foo, filterable_conditions)
        elif not self.qdrant_settings.allow_arbitrary_filter:
            search_by_vector_foo = make_partial_function(search_by_vector_foo, {"query_filter": None})


        self.tool(
            find_foo,
            name="qdrant-find",
            description=self.tool_settings.tool_find_description,
        )

        self.tool(
            get_point,
            name="qdrant-get-point",
            description="Get a specific point by its ID from a Qdrant collection.",
        )

        self.tool(
            get_collections,
            name="qdrant-get-collections",
            description="Get a list of all collections in the Qdrant server.",
        )

        self.tool(
            get_collection_details,
            name="qdrant-get-collection-details",
            description="Get detailed information about a specific collection including status, configuration, and statistics.",
        )

        self.tool(
            get_collection_count,
            name="qdrant-get-collection-count",
            description="Get the number of points in a collection.",
        )

        self.tool(
            peek_collection,
            name="qdrant-peek-collection",
            description="Preview sample points from a collection.",
        )

        self.tool(
            get_documents,
            name="qdrant-get-documents",
            description="Retrieve multiple documents by their IDs.",
        )

        self.tool(
            search_by_vector_foo,
            name="qdrant-search-by-vector",
            description="Search using a raw vector instead of text query.",
        )

        self.tool(
            list_document_ids,
            name="qdrant-list-document-ids",
            description="List document IDs with pagination support.",
        )

        self.tool(
            scroll_points,
            name="qdrant-scroll-points",
            description="Paginated retrieval of points using scroll.",
        )

        if not self.qdrant_settings.read_only:
            # Those methods can modify the database
            self.tool(
                store,
                name="qdrant-store",
                description=self.tool_settings.tool_store_description,
            )

            self.tool(
                delete_point,
                name="qdrant-delete-point",
                description="Delete a specific point by its ID from a Qdrant collection.",
            )

            self.tool(
                update_point_payload,
                name="qdrant-update-point-payload",
                description="Update the payload (metadata) of a specific point by its ID.",
            )

            self.tool(
                create_collection,
                name="qdrant-create-collection",
                description="Create a new collection with vector configuration.",
            )

            self.tool(
                delete_collection,
                name="qdrant-delete-collection",
                description="Delete a collection entirely.",
            )

            self.tool(
                add_documents,
                name="qdrant-add-documents",
                description="Add multiple documents in batch.",
            )

            self.tool(
                delete_documents,
                name="qdrant-delete-documents",
                description="Delete multiple documents by their IDs.",
            )
