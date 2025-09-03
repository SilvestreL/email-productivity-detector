#!/bin/bash

# Script de Deploy para Hugging Face Spaces
# Este script automatiza o processo de build e deploy

set -e  # Exit on any error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
SPACE_NAME="EmailProductivityClassifier"
USERNAME="silvestrel"  # Seu username do HF
REGISTRY="registry.hf.space"
IMAGE_NAME="email-classifier"
TAG="latest"

echo -e "${BLUE}🚀 Iniciando deploy para Hugging Face Spaces...${NC}"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando. Inicie o Docker e tente novamente.${NC}"
    exit 1
fi

# Verificar se está logado no Hugging Face
if ! docker login $REGISTRY > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Faça login no Hugging Face Container Registry:${NC}"
    echo "docker login $REGISTRY"
    echo "Use seu token de acesso do HF (Settings > Access Tokens)"
    exit 1
fi

echo -e "${GREEN}✅ Logado no Hugging Face Container Registry${NC}"

# Build da imagem
echo -e "${BLUE}🔨 Fazendo build da imagem Docker...${NC}"
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build concluído com sucesso${NC}"
else
    echo -e "${RED}❌ Erro no build da imagem${NC}"
    exit 1
fi

# Tag da imagem para o registry do HF
echo -e "${BLUE}🏷️  Tagging da imagem...${NC}"
docker tag $IMAGE_NAME $REGISTRY/$USERNAME/$SPACE_NAME:$TAG

# Push para o registry
echo -e "${BLUE}📤 Fazendo push para o Hugging Face...${NC}"
docker push $REGISTRY/$USERNAME/$SPACE_NAME:$TAG

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Push concluído com sucesso!${NC}"
    echo -e "${GREEN}🎉 Sua aplicação está sendo deployada no Hugging Face Spaces${NC}"
    echo -e "${BLUE}🔗 Acesse: https://huggingface.co/spaces/$USERNAME/$SPACE_NAME${NC}"
else
    echo -e "${RED}❌ Erro no push da imagem${NC}"
    exit 1
fi

# Limpeza
echo -e "${BLUE}🧹 Limpando imagens locais...${NC}"
docker rmi $IMAGE_NAME
docker rmi $REGISTRY/$USERNAME/$SPACE_NAME:$TAG

echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo -e "${YELLOW}💡 Dica: O deploy pode levar alguns minutos para ficar disponível${NC}"
