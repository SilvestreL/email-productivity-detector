#!/bin/bash

# Script para build da imagem Docker - Email Productivity Classifier
# AutoU

echo "🐳 Build da imagem Docker - Email Productivity Classifier"
echo "=================================================="

# Verifica se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Nome da imagem
IMAGE_NAME="email-productivity-classifier"
TAG="latest"

echo "📦 Construindo imagem Docker..."
echo "🖼️  Nome: $IMAGE_NAME:$TAG"

# Build da imagem
docker build -t $IMAGE_NAME:$TAG .

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso!"
    echo "📊 Informações da imagem:"
    docker images $IMAGE_NAME:$TAG
    
    echo ""
    echo "🚀 Para executar a aplicação:"
    echo "   docker run -p 8501:8501 $IMAGE_NAME:$TAG"
    echo ""
    echo "🌐 Ou use docker-compose:"
    echo "   docker-compose up -d"
else
    echo "❌ Erro no build da imagem Docker"
    exit 1
fi
