from azure.cosmos import CosmosClient, PartitionKey, exceptions
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import logging
from config import settings

logger = logging.getLogger(__name__)

class CosmosDBClient:
    """
    Manages conversation history in Azure Cosmos DB.
    Uses hierarchical partition key: [userId, conversationId] for isolation and scale.
    """
    
    def __init__(self):
        self.client = CosmosClient(settings.cosmos_endpoint, settings.cosmos_key)
        self.database = self.client.get_database_client(settings.cosmos_database)
        self.container = self.database.get_container_client(settings.cosmos_container)
    
    async def create_conversation(self, user_id: str, title: str = "New Conversation") -> str:
        """Create a new conversation for a user."""
        conversation_id = str(uuid.uuid4())
        
        item = {
            "id": conversation_id,
            "userId": user_id,
            "conversationId": conversation_id,
            "title": title,
            "createdAt": datetime.utcnow().isoformat(),
            "messages": [],
            "type": "conversation"
        }
        
        try:
            self.container.create_item(body=item, enable_automatic_id_generation=False)
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            return conversation_id
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create conversation: {str(e)}")
            raise
    
    async def add_message(
        self,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        citations: Optional[List[Dict]] = None
    ):
        """Add a message to an existing conversation."""
        try:
            # Read existing conversation
            item = self.container.read_item(
                item=conversation_id,
                partition_key=[user_id, conversation_id]
            )
            
            # Add new message
            message = {
                "id": str(uuid.uuid4()),
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "citations": citations or []
            }
            
            item["messages"].append(message)
            item["updatedAt"] = datetime.utcnow().isoformat()
            
            # Update item
            self.container.replace_item(item=item["id"], body=item)
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to add message: {str(e)}")
            raise
    
    async def get_conversation(self, user_id: str, conversation_id: str) -> Optional[Dict]:
        """Retrieve a conversation with all messages."""
        try:
            item = self.container.read_item(
                item=conversation_id,
                partition_key=[user_id, conversation_id]
            )
            return item
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get conversation: {str(e)}")
            raise
    
    async def list_conversations(self, user_id: str, limit: int = 20) -> List[Dict]:
        """List all conversations for a user (most recent first)."""
        query = """
        SELECT c.id, c.conversationId, c.title, c.createdAt, c.updatedAt
        FROM c
        WHERE c.userId = @userId AND c.type = 'conversation'
        ORDER BY c.updatedAt DESC
        OFFSET 0 LIMIT @limit
        """
        
        try:
            items = list(self.container.query_items(
                query=query,
                parameters=[
                    {"name": "@userId", "value": user_id},
                    {"name": "@limit", "value": limit}
                ],
                partition_key=user_id,  # Scoped to user partition
                enable_cross_partition_query=False
            ))
            return items
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to list conversations: {str(e)}")
            return []

cosmos_client = CosmosDBClient()
