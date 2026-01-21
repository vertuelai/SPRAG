#!/bin/bash

# Azure Container Apps Deployment Script
# Prerequisites: Azure CLI, Docker, logged in to Azure

# Configuration
RESOURCE_GROUP="rg-adic-sharepoint-rag"
LOCATION="eastus"
ENVIRONMENT_NAME="adic-rag-env"
ACR_NAME="adicragacr"
BACKEND_APP="adic-rag-backend"
FRONTEND_APP="adic-rag-frontend"

echo "🚀 Starting Azure Container Apps Deployment..."

# Create Resource Group
echo "📦 Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create Azure Container Registry
echo "🐳 Creating Azure Container Registry..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials
ACR_USERNAME=$(az acr credential show -n $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv)
ACR_LOGIN_SERVER=$(az acr show -n $ACR_NAME --query loginServer -o tsv)

# Login to ACR
echo "🔐 Logging into ACR..."
az acr login --name $ACR_NAME

# Build and push backend image
echo "🏗️  Building backend image..."
docker build -f Dockerfile.backend -t $ACR_LOGIN_SERVER/adic-rag-backend:latest .
docker push $ACR_LOGIN_SERVER/adic-rag-backend:latest

# Build and push frontend image
echo "🏗️  Building frontend image..."
docker build -f Dockerfile.frontend -t $ACR_LOGIN_SERVER/adic-rag-frontend:latest .
docker push $ACR_LOGIN_SERVER/adic-rag-frontend:latest

# Create Container Apps Environment
echo "🌍 Creating Container Apps Environment..."
az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy Backend Container App (Internal)
echo "🔧 Deploying backend container app..."
az containerapp create \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $ACR_LOGIN_SERVER/adic-rag-backend:latest \
  --target-port 8000 \
  --ingress internal \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 5 \
  --env-vars \
    DEMO_MODE=true \
    OPENAI_API_KEY=secretref:openai-key

# Get backend FQDN
BACKEND_FQDN=$(az containerapp show -n $BACKEND_APP -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

# Deploy Frontend Container App (External)
echo "🎨 Deploying frontend container app..."
az containerapp create \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $ACR_LOGIN_SERVER/adic-rag-frontend:latest \
  --target-port 8501 \
  --ingress external \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 10 \
  --env-vars \
    BACKEND_URL=https://$BACKEND_FQDN

# Get frontend URL
FRONTEND_URL=$(az containerapp show -n $FRONTEND_APP -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

echo "✅ Deployment complete!"
echo "🌐 Frontend URL: https://$FRONTEND_URL"
echo "🔧 Backend URL (internal): https://$BACKEND_FQDN"
