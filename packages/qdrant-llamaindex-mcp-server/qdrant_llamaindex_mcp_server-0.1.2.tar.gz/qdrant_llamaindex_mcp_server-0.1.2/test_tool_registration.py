#!/usr/bin/env python3

# Test to check if tool registration can fail silently
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
    
    # Check the registered tools
    if hasattr(server, '_tools'):
        print(f"Number of tools registered: {len(server._tools)}")
        for tool_name in server._tools:
            print(f"  - {tool_name}")
    else:
        print("No _tools attribute found on server")
    
    # Try accessing the tools differently
    print("\nTrying different approaches to list tools...")
    print(f"Server attributes: {[attr for attr in dir(server) if not attr.startswith('__')]}")
    
except Exception as e:
    import traceback
    print(f"ERROR during server creation: {type(e).__name__}: {e}")
    print(f"Traceback:\n{traceback.format_exc()}")