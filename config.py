from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Demo Mode
    demo_mode: bool = True
    
    # Entra ID
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    
    # Cosmos DB
    cosmos_endpoint: Optional[str] = None
    cosmos_key: Optional[str] = None
    cosmos_database: str = "m365rag"
    cosmos_container: str = "conversations"
    
    # App
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:8501"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()
