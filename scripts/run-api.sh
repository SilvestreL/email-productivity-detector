#!/bin/bash

# Script para executar a API REST - Email Productivity Classifier
# AutoU

echo "🚀 Executando API REST - Email Productivity Classifier"
echo "=================================================="

# Verifica se o ambiente virtual está ativo
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verifica se as dependências estão instaladas
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Instalando dependências da API..."
    pip install -r requirements.txt
fi

# Verifica se o modelo existe
if [ ! -f "models/email_spam_pipeline.joblib" ]; then
    echo "🤖 Treinando modelo..."
    python src/train.py
fi

echo "🌐 Iniciando API REST..."
echo "📚 Documentação: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""

# Executa a API
python src/api.py
