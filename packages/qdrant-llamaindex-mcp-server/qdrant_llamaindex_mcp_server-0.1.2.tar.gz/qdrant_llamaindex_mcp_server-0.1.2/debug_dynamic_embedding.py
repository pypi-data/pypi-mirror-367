#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_qdrant.qdrant import QdrantConnector
from mcp_server_qdrant.embeddings.factory import create_embedding_provider
from mcp_server_qdrant.settings import EmbeddingProviderSettings


async def debug_dynamic_embedding_detection():
    """Debug the _get_embedding_provider_for_collection method step by step"""
    
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
    
    collection_name = "deribit_docs"
    
    try:
        print(f"\n=== Debugging dynamic embedding detection for '{collection_name}' ===")
        
        # Step 1: Check if collection exists
        collection_exists = await connector._client.collection_exists(collection_name)
        print(f"Step 1 - Collection exists: {collection_exists}")
        if not collection_exists:
            print("❌ Collection doesn't exist, would use default provider")
            return
        
        # Step 2: Get collection details
        print("Step 2 - Getting collection details...")
        collection_info = await connector._client.get_collection(collection_name)
        collection_dict = collection_info.model_dump()
        print("Step 2 - Collection info retrieved successfully")
        
        # Step 3: Extract vector configuration
        print("Step 3 - Extracting vector configuration...")
        vectors_config = collection_dict.get("config", {}).get("params", {}).get("vectors", {})
        print(f"Step 3 - Vectors config: {vectors_config}")
        if not vectors_config:
            print("❌ No vector config found, would use default provider")
            return
        
        # Step 4: Get vector names
        print("Step 4 - Getting vector names...")
        vector_names = list(vectors_config.keys())
        print(f"Step 4 - Vector names: {vector_names}")
        if not vector_names:
            print("❌ No vector names found, would use default provider")
            return
        
        # Step 5: Get model name
        model_name = vector_names[0]
        print(f"Step 5 - Selected model name: '{model_name}'")
        
        # Step 6: Check if model is allowed
        print("Step 6 - Checking if model is allowed...")
        is_allowed = connector._is_model_allowed(model_name)
        print(f"Step 6 - Is model '{model_name}' allowed? {is_allowed}")
        if not is_allowed:
            print(f"❌ Model '{model_name}' not allowed, would use default provider")
            return
        
        # Step 7: Check cache
        print("Step 7 - Checking provider cache...")
        cached = model_name in connector._provider_cache
        print(f"Step 7 - Is model '{model_name}' in cache? {cached}")
        if cached:
            cached_provider = connector._provider_cache[model_name]
            print(f"Step 7 - Cached provider vector name: {cached_provider.get_vector_name()}")
            return cached_provider
        
        # Step 8: Create new provider
        print("Step 8 - Creating new embedding provider...")
        # Note: BaseSettings doesn't accept constructor args for fields with validation_alias
        # so we need to create and then modify the settings
        provider_settings = EmbeddingProviderSettings()
        provider_settings.provider_type = embedding_settings.provider_type
        provider_settings.model_name = model_name
        print(f"Step 8 - Provider settings: provider_type={provider_settings.provider_type}, model_name={provider_settings.model_name}")
        
        provider = create_embedding_provider(provider_settings)
        print(f"Step 8 - Created provider with vector name: {provider.get_vector_name()}")
        
        # Step 9: Cache the provider
        print("Step 9 - Caching the provider...")
        connector._provider_cache[model_name] = provider
        print(f"Step 9 - Provider cached for model '{model_name}'")
        
        print(f"✅ Successfully created dynamic provider for model: {provider.get_vector_name()}")
        return provider
        
    except Exception as e:
        print(f"❌ Exception during dynamic detection: {e}")
        import traceback
        traceback.print_exc()
        print("Would use default provider due to exception")
        return connector._embedding_provider


if __name__ == "__main__":
    asyncio.run(debug_dynamic_embedding_detection())