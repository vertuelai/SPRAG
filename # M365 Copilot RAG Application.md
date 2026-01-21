# M365 Copilot RAG Application

A production-ready RAG application using Microsoft 365 Copilot Retrieval API, Azure OpenAI, and Azure Cosmos DB.

## Architecture

- **Retrieval**: Microsoft 365 Copilot API (permission-aware, semantic search)
- **LLM**: Azure OpenAI (gpt-4o)
- **Storage**: Azure Cosmos DB (conversation history, hierarchical partition keys)
- **Backend**: FastAPI (async Python)
- **Frontend**: Streamlit (interactive UI)

## Prerequisites

1. **Azure App Registration** with permissions:
   - `Sites.Read.All`
   - `Files.Read.All`

2. **Azure OpenAI** deployment (gpt-4o recommended)

3. **Azure Cosmos DB** account with:
   - Database: `m365rag`
   - Container: `conversations`
   - Hierarchical partition key: `/userId, /conversationId`

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### 3. Create Cosmos DB Container

```bash
# Using Azure CLI
az cosmosdb sql container create \
  --account-name YOUR_ACCOUNT \
  --database-name m365rag \
  --name conversations \
  --partition-key-path "/userId" "/conversationId" \
  --partition-key-version 2
```

### 4. Run Backend

```bash
cd backend
uvicorn app:app --reload --port 8000
```

### 5. Run Frontend

```bash
streamlit run frontend/streamlit_app.py
```

## Usage

1. Open browser to `http://localhost:8501`
2. Ask questions about your M365 content
3. View grounded answers with citations
4. Filter by SharePoint site for precision

## Best Practices Implemented

✅ Permission-aware retrieval (ACL trimming)  
✅ Low-latency semantic search  
✅ Strict grounding (no hallucinations)  
✅ Citation tracking  
✅ Conversation history with user isolation  
✅ Hierarchical partition keys for scale  
✅ Diagnostic logging  
✅ Retry logic with exponential backoff  

## Security

- All data stays in M365 (no indexing)
- DLP and sensitivity labels honored
- User identity preserved
- Cosmos DB access controlled by partition key

## License

MIT
