#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_qdrant.qdrant import QdrantConnector
from mcp_server_qdrant.embeddings.factory import create_embedding_provider
from mcp_server_qdrant.settings import EmbeddingProviderSettings


async def test_dynamic_embedding_detection():
    """Test that dynamic embedding detection works for deribit_docs collection"""
    
    # Create default embedding provider
    embedding_settings = EmbeddingProviderSettings()
    default_provider = create_embedding_provider(embedding_settings)
    
    print(f"Default provider model: {default_provider.get_vector_name()}")
    
    # Create QdrantConnector using your cloud Qdrant instance
    connector = QdrantConnector(
        qdrant_url="https://0d253f79-80d9-4821-a53f-b2d6e153b331.eu-central-1-0.aws.cloud.qdrant.io:6333",
        qdrant_api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.fwC7i06ABZHtmAc4LFhVNizWLHFnVwIEpB958CNry9I",
        collection_name=None,
        embedding_provider=default_provider,
        embedding_provider_settings=embedding_settings
    )
    
    # Test the dynamic detection for deribit_docs
    try:
        # First, let's check if the collection exists and get its details
        collection_exists = await connector._client.collection_exists("deribit_docs")
        print(f"Collection 'deribit_docs' exists: {collection_exists}")
        
        if collection_exists:
            # Get collection details to see the vector configuration
            collection_info = await connector._client.get_collection("deribit_docs")
            collection_dict = collection_info.model_dump()
            print(f"Collection config: {collection_dict.get('config', {})}")
            
            vectors_config = collection_dict.get("config", {}).get("params", {}).get("vectors", {})
            print(f"Vectors config: {vectors_config}")
            
            if vectors_config:
                vector_names = list(vectors_config.keys())
                print(f"Vector names found: {vector_names}")
        
        # Test the allowed models validation
        print(f"Allowed models: {embedding_settings.allowed_models}")
        model_name = "BAAI/bge-small-en-v1.5"
        is_allowed = connector._is_model_allowed(model_name)
        print(f"Is '{model_name}' allowed? {is_allowed}")
        
        dynamic_provider = await connector._get_embedding_provider_for_collection("deribit_docs")
        print(f"Dynamic provider for deribit_docs: {dynamic_provider.get_vector_name()}")
        
        if dynamic_provider.get_vector_name() != default_provider.get_vector_name():
            print("✅ Dynamic detection is working!")
        else:
            print("❌ Dynamic detection failed - using default model")
            
    except Exception as e:
        print(f"❌ Error during dynamic detection: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_dynamic_embedding_detection())