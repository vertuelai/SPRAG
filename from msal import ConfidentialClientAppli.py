from msal import ConfidentialClientApplication
from typing import Optional
import logging
from config import settings

logger = logging.getLogger(__name__)

class M365AuthClient:
    """Handles Microsoft 365 authentication using app-only (client credentials) flow."""
    
    def __init__(self):
        self.authority = f"https://login.microsoftonline.com/{settings.azure_tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        
        self.app = ConfidentialClientApplication(
            client_id=settings.azure_client_id,
            client_credential=settings.azure_client_secret,
            authority=self.authority
        )
    
    def get_access_token(self) -> Optional[str]:
        """Get access token for Microsoft Graph API."""
        try:
            result = self.app.acquire_token_silent(self.scopes, account=None)
            
            if not result:
                result = self.app.acquire_token_for_client(scopes=self.scopes)
            
            if "access_token" in result:
                return result["access_token"]
            else:
                logger.error(f"Token acquisition failed: {result.get('error_description')}")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None

auth_client = M365AuthClient()
