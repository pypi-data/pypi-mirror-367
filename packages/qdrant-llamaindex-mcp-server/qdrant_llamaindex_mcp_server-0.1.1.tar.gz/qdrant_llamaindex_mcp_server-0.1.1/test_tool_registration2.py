#!/usr/bin/env python3

# Test to check registered tools
import sys
import os
sys.path.insert(0, 'src')

# Set environment variables to test with read-only mode
os.environ['QDRANT_READ_ONLY'] = 'true'
os.environ['QDRANT_URL'] = 'http://localhost:6333'
os.environ['COLLECTION_NAME'] = 'test'

try:
    from mcp_server_qdrant.mcp_server import QdrantMCPServer
    from mcp_server_qdrant.settings import (
        EmbeddingProviderSettings,
        QdrantSettings,
        ToolSettings,
    )
    
    print("Creating server instance...")
    server = QdrantMCPServer(
        tool_settings=ToolSettings(),
        qdrant_settings=QdrantSettings(),
        embedding_provider_settings=EmbeddingProviderSettings(),
    )
    
    print("Server created successfully!")
    
    # Try to get tools using the get_tools method
    tools = server.get_tools()
    print(f"Number of tools registered: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
except Exception as e:
    import traceback
    print(f"ERROR during server creation: {type(e).__name__}: {e}")
    print(f"Traceback:\n{traceback.format_exc()}")