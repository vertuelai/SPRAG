from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from backend.auth import auth_client
from backend.retrieval import M365RetrievalClient
from backend.llm import LLMClient
from backend.cosmos import cosmos_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ADIC SharePoint RAG API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_client = LLMClient()

class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_id: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    citations: List[dict]
    conversation_id: str

@app.post("/api/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    """Main RAG endpoint: retrieval + generation."""
    try:
        # Step 1: Authenticate with M365
        access_token = auth_client.get_access_token()
        if not access_token:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Step 2: Retrieve relevant content
        retrieval_client = M365RetrievalClient(access_token)
        chunks = await retrieval_client.search_content(
            query=request.query,
            top=min(request.top_k, 10),  # Cap at 10
            site_filter=request.site_f  # Cap at 10
        
        if not chunks:
            return QueryResponse(
                answer="I couldn't find relevant information in the available documents.",
                citations=[],
                conversation_id=request.conversation_id or "none"
            )
        
        # Step 3: Get conversation history
        conversation_history = None
        if request.conversation_id:
            conv = await cosmos_client.get_conversation(request.user_id, request.conversation_id)
            if conv:
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in conv.get("messages", [])
                ]
        
        # Step 4: Generate grounded response
        result = llm_client.generate_grounded_response(
            query=request.query,
            retrieved_chunks=chunks,
            conversation_history=conversation_history
        )
        
        # Step 5: Save to Cosmos DB
        if not request.conversation_id:
            request.conversation_id = await cosmos_client.create_conversation(
                user_id=request.user_id,
                title=request.query[:50]
            )
        
        # Save user message
        await cosmos_client.add_message(
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            role="user",
            content=request.query
        )
        
        # Save assistant message
        await cosmos_client.add_message(
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            role="assistant",
            content=result["answer"],
            citations=result["citations"]
        )
        
        return QueryResponse(
            answer=result["answer"],
            citations=result["citations"],
            conversation_id=request.conversation_id
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{user_id}")
async def list_conversations(user_id: str):
    """List all conversations for a user."""
    try:
        conversations = await cosmos_client.list_conversations(user_id)
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Failed to list conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{user_id}/{conversation_id}")
async def get_conversation(user_id: str, conversation_id: str):
    """Get a specific conversation with all messages."""
    try:
        conversation = await cosmos_client.get_conversation(user_id, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
