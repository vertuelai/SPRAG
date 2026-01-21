# ADIC SharePoint RAG

A modern, AI-powered knowledge retrieval system for SharePoint documents using RAG (Retrieval-Augmented Generation).

## 🚀 Features

- **Semantic Search**: Intelligent search across SharePoint documents
- **AI-Powered Answers**: Get accurate responses with source citations
- **Conversation Memory**: Context-aware multi-turn conversations
- **Modern UI**: Beautiful, animated interface with glassmorphism design
- **Azure Container Apps Ready**: Production-ready container deployment

## 📋 Architecture

```
┌─────────────────────────────────────────┐
│   Frontend (Streamlit)                  │
│   Port: 8501 / HTTPS                    │
│   - Modern UI with animations           │
│   - User interaction handling           │
└──────────────┬──────────────────────────┘
               │
               ▼ HTTP/HTTPS
┌──────────────────────────────────────────┐
│   Backend (FastAPI)                      │
│   Port: 8000 / HTTPS                     │
│   - API endpoints                        │
│   - Business logic                       │
└──────────┬───────────┬──────────┬────────┘
           │           │          │
           ▼           ▼          ▼
    ┌─────────┐ ┌──────────┐ ┌────────┐
    │ OpenAI  │ │ M365/    │ │ Cosmos │
    │ API     │ │ Graph    │ │ DB     │
    └─────────┘ └──────────┘ └────────┘
```

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- Docker (for containerization)
- Azure CLI (for deployment)

### Setup

1. **Clone and navigate**
   ```bash
   cd "D:\RAG SP"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r constraints.txt
   ```

4. **Configure environment**
   
   Copy `.env` template and fill in your values:
   ```env
   # Microsoft Entra ID
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-secret
   
   # OpenAI
   OPENAI_API_KEY=your-openai-key
   OPENAI_MODEL=gpt-4o
   
   # Cosmos DB
   COSMOS_ENDPOINT=your-cosmos-endpoint
   COSMOS_KEY=your-cosmos-key
   
   # Demo Mode (set to false for production)
   DEMO_MODE=true
   ```

5. **Run locally**

   **Backend:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   **Frontend:**
   ```bash
   streamlit run app.py
   ```

   Access at: http://localhost:8501

## 🐳 Docker Development

### Build and run with Docker Compose

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:8501
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ☁️ Azure Container Apps Deployment

### Option 1: Using the deployment script

```bash
chmod +x deploy-container-apps.sh
./deploy-container-apps.sh
```

### Option 2: Manual deployment

1. **Create Resource Group**
   ```bash
   az group create --name rg-adic-sharepoint-rag --location eastus
   ```

2. **Create Container Registry**
   ```bash
   az acr create --resource-group rg-adic-sharepoint-rag \
                 --name adicragacr --sku Basic --admin-enabled true
   ```

3. **Build and push images**
   ```bash
   az acr login --name adicragacr
   
   docker build -f Dockerfile.backend -t adicragacr.azurecr.io/adic-rag-backend:latest .
   docker push adicragacr.azurecr.io/adic-rag-backend:latest
   
   docker build -f Dockerfile.frontend -t adicragacr.azurecr.io/adic-rag-frontend:latest .
   docker push adicragacr.azurecr.io/adic-rag-frontend:latest
   ```

4. **Create Container Apps Environment**
   ```bash
   az containerapp env create \
     --name adic-rag-env \
     --resource-group rg-adic-sharepoint-rag \
     --location eastus
   ```

5. **Deploy containers**
   
   See `deploy-container-apps.sh` for full deployment commands.

## 🎨 UI Features

- **Animated Gradient Background**: Dynamic, shifting colors
- **Glassmorphism Design**: Modern frosted glass effects
- **Smooth Animations**: Hover effects, transitions, and glow effects
- **Quick Action Buttons**: Pre-defined prompts for common queries
- **Citation Cards**: Beautiful, interactive source references
- **Responsive Layout**: Works on all screen sizes

## 📊 Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: Check Streamlit metrics

### Logs
```bash
# Container Apps logs
az containerapp logs show \
  --name adic-rag-backend \
  --resource-group rg-adic-sharepoint-rag

az containerapp logs show \
  --name adic-rag-frontend \
  --resource-group rg-adic-sharepoint-rag
```

## 🔒 Security

- All secrets stored in Azure Key Vault or Container Apps secrets
- Internal backend communication (not exposed publicly)
- HTTPS enforced on all external endpoints
- OAuth 2.0 authentication with Microsoft Entra ID

## 📝 License

Proprietary - ADIC Internal Use Only

## 👥 Support

For issues or questions, contact the ADIC Development Team.
