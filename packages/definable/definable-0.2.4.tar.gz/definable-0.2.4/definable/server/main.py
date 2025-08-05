"""Main server entry point for containerized agents"""
import uvicorn
import os
from definable.server.app import AgentServer

def create_app():
    """App factory for uvicorn with auto-reload support"""
    config_file = os.getenv("DEFINABLE_CONFIG_FILE", os.getenv("AGENT_CONFIG", "agent.yaml"))
    server = AgentServer(config_file)
    return server.app

def main() -> None:
    """Start the agent server"""
    config_file = os.getenv("AGENT_CONFIG", "agent.yaml")
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    server = AgentServer(config_file)
    uvicorn.run(server.app, host=host, port=port)

if __name__ == "__main__":
    main()