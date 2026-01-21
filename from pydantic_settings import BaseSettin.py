from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Entra ID
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Cosmos DB
    cosmos_endpoint: str
    cosmos_key: str
    cosmos_database: str = "m365rag"
    cosmos_container: str = "conversations"
    
    # App
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:8501"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
