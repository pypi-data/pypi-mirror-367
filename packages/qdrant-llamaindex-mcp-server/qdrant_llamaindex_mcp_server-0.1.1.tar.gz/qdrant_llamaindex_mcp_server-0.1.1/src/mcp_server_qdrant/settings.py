from typing import Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings

from mcp_server_qdrant.embeddings.types import EmbeddingProviderType

DEFAULT_TOOL_FIND_DESCRIPTION = (
    "Search for documents stored by LlamaIndex in Qdrant. Use this tool when you need to: \n"
    " - Find relevant documents or text chunks by semantic similarity \n"
    " - Access stored knowledge base content \n"
    " - Retrieve context from previously indexed documents"
)

DEFAULT_TOOL_STORE_DESCRIPTION = (
    "Store information in Qdrant vector database. Use this tool when you need to: \n"
    " - Save new documents or text chunks \n"
    " - Add information to the knowledge base \n"
    " - Store content for later retrieval"
)


class ToolSettings(BaseSettings):
    """
    Configuration for the MCP tools.
    """

    tool_find_description: str = Field(
        default=DEFAULT_TOOL_FIND_DESCRIPTION,
        validation_alias="TOOL_FIND_DESCRIPTION",
    )
    tool_store_description: str = Field(
        default=DEFAULT_TOOL_STORE_DESCRIPTION,
        validation_alias="TOOL_STORE_DESCRIPTION",
    )


class EmbeddingProviderSettings(BaseSettings):
    """
    Configuration for the embedding provider.
    """
    
    model_config = {"extra": "ignore"}

    provider_type: EmbeddingProviderType = Field(
        default=EmbeddingProviderType.FASTEMBED,
        validation_alias="EMBEDDING_PROVIDER",
    )
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL",
    )
    allowed_models: list[str] | None = Field(
        default=[
            "sentence-transformers/all-MiniLM-L6-v2",
            "BAAI/bge-small-en-v1.5", 
            "snowflake/snowflake-arctic-embed-xs",
            "jinaai/jina-embeddings-v2-small-en"
        ],
        validation_alias="EMBEDDING_ALLOWED_MODELS",
        description="Whitelist of allowed embedding models. Only these models can be loaded dynamically. Set to null to allow all models.",
    )


class FilterableField(BaseModel):
    name: str = Field(description="The name of the field payload field to filter on")
    description: str = Field(
        description="A description for the field used in the tool description"
    )
    field_type: Literal["keyword", "integer", "float", "boolean"] = Field(
        description="The type of the field"
    )
    condition: Literal["==", "!=", ">", ">=", "<", "<=", "any", "except"] | None = (
        Field(
            default=None,
            description=(
                "The condition to use for the filter. If not provided, the field will be indexed, but no "
                "filter argument will be exposed to MCP tool."
            ),
        )
    )
    required: bool = Field(
        default=False,
        description="Whether the field is required for the filter.",
    )


class QdrantSettings(BaseSettings):
    """
    Configuration for the Qdrant connector.
    """
    
    model_config = {"extra": "ignore"}

    location: str | None = Field(default=None, validation_alias="QDRANT_URL")
    api_key: str | None = Field(default=None, validation_alias="QDRANT_API_KEY")
    collection_name: str | None = Field(
        default=None, validation_alias="COLLECTION_NAME"
    )
    local_path: str | None = Field(default=None, validation_alias="QDRANT_LOCAL_PATH")
    search_limit: int = Field(default=10, validation_alias="QDRANT_SEARCH_LIMIT")

    filterable_fields: list[FilterableField] | None = Field(default=None)

    allow_arbitrary_filter: bool = Field(
        default=False, validation_alias="QDRANT_ALLOW_ARBITRARY_FILTER"
    )
    read_only: bool = Field(
        default=False, validation_alias="QDRANT_READ_ONLY"
    )

    def filterable_fields_dict(self) -> dict[str, FilterableField]:
        if self.filterable_fields is None:
            return {}
        return {field.name: field for field in self.filterable_fields}

    def filterable_fields_dict_with_conditions(self) -> dict[str, FilterableField]:
        if self.filterable_fields is None:
            return {}
        return {
            field.name: field
            for field in self.filterable_fields
            if field.condition is not None
        }

    @model_validator(mode="after")
    def check_local_path_conflict(self) -> "QdrantSettings":
        if self.local_path:
            if self.location is not None or self.api_key is not None:
                raise ValueError(
                    "If 'local_path' is set, 'location' and 'api_key' must be None."
                )
        return self
