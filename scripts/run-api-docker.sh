#!/bin/bash

# Script para executar a API REST com Docker - Email Productivity Classifier
# AutoU

echo "🐳 Executando API REST com Docker - Email Productivity Classifier"
echo "=================================================="

# Verifica se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verifica se o docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Verifica se a imagem existe
IMAGE_NAME="email-productivity-classifier"
if ! docker images | grep -q $IMAGE_NAME; then
    echo "📦 Imagem não encontrada. Construindo..."
    ./docker-build.sh
fi

echo "🐳 Iniciando API com docker-compose..."

# Cria diretório de logs se não existir
mkdir -p logs

# Executa com docker-compose para API
docker-compose -f docker-compose.api.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ API iniciada com sucesso!"
    echo ""
    echo "🌐 URLs de acesso:"
    echo "   📄 Interface HTML: http://localhost"
    echo "   🔗 API REST: http://localhost:8000"
    echo "   📚 Documentação: http://localhost:8000/docs"
    echo "   🔍 Health Check: http://localhost:8000/health"
    echo "   🌐 Via Nginx: http://localhost/api/"
    echo ""
    echo "📊 Status dos containers:"
    docker-compose -f docker-compose.api.yml ps
    echo ""
    echo "📋 Logs da API:"
    echo "   docker-compose -f docker-compose.api.yml logs -f email-classifier-api"
    echo ""
    echo "🧪 Para testar a API:"
    echo "   python test_api.py"
    echo ""
    echo "🛑 Para parar a API:"
    echo "   docker-compose -f docker-compose.api.yml down"
else
    echo "❌ Erro ao iniciar a API"
    exit 1
fi
