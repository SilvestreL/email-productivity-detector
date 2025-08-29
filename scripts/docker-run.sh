#!/bin/bash

# Script para executar a aplicação com Docker - Email Productivity Classifier
# AutoU

echo "🚀 Executando Email Productivity Classifier com Docker"
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

echo "🐳 Iniciando serviços com docker-compose..."

# Cria diretório de logs se não existir
mkdir -p logs

# Executa com docker-compose
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Aplicação iniciada com sucesso!"
    echo ""
    echo "🌐 URLs de acesso:"
    echo "   📄 Interface HTML: http://localhost"
    echo "   🤖 App Streamlit: http://localhost:8501"
    echo "   🔗 Via Nginx: http://localhost/streamlit/"
    echo ""
    echo "📊 Status dos containers:"
    docker-compose ps
    echo ""
    echo "📋 Logs da aplicação:"
    echo "   docker-compose logs -f email-classifier"
    echo ""
    echo "🛑 Para parar a aplicação:"
    echo "   docker-compose down"
else
    echo "❌ Erro ao iniciar a aplicação"
    exit 1
fi
