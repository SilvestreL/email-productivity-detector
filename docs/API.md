# 🔗 API REST - Email Classification

## Visão Geral

API REST completa para classificação de emails usando Hugging Face DistilBERT e geração automática de respostas.

## 🚀 Quick Start

```bash
# Executar API
python api.py

# Testar API
python scripts/test_api.py

# Acessar documentação
http://localhost:8000/docs
```

## 📋 Endpoints

### **Informações**

- `GET /` - Informações da API
- `GET /health` - Health check
- `GET /model/info` - Informações do modelo

### **Classificação**

- `POST /classify` - Classificar email único
- `POST /analyze` - Análise completa (classificação + resposta)

### **Respostas**

- `POST /generate-response` - Gerar resposta automática
- `GET /categories` - Categorias disponíveis

## 📝 Exemplos de Uso

### Classificar Email

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Olá, preciso de ajuda com o sistema",
    "subject": "Suporte Técnico"
  }'
```

### Análise Completa

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Parabéns! Você ganhou R$ 1000! Clique aqui agora!",
    "subject": "Oferta Especial"
  }'
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Modelo
SPAM_MODEL_PATH=artifacts/best_model.pt
SPAM_MODEL_NAME=distilbert-base-uncased

# Servidor
HOST=0.0.0.0
PORT=8000
```

### Dependências

```bash
pip install fastapi uvicorn transformers torch
```

## 🐳 Docker

```bash
# Build
docker build -t email-classifier .

# Run
docker run -p 8000:8000 email-classifier

# Docker Compose
docker-compose -f docker-compose.api.yml up
```

## 📊 Resposta da API

### Classificação

```json
{
  "category": "spam",
  "confidence": 0.92,
  "explanation": "Modelo DistilBERT classificou como spam com 92% de confiança"
}
```

### Análise Completa

```json
{
  "classification": {
    "category": "spam",
    "confidence": 0.92,
    "explanation": "Modelo DistilBERT classificou como spam com 92% de confiança"
  },
  "response_generation": {
    "suggested_response": "Obrigado pelo contato, mas não estou interessado neste tipo de comunicação.",
    "confidence": 0.9,
    "reasoning": "Resposta baseada em template para emails spam com tom professional"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🧪 Testes

```bash
# Teste completo
python scripts/test_api.py

# Teste específico
curl http://localhost:8000/health
```

## 🔍 Troubleshooting

### Erro de Modelo

- Verificar se `artifacts/best_model.pt` existe
- Executar `python scripts/run_bert.py` para treinar

### Erro de Porta

```bash
# Verificar porta
lsof -i :8000

# Matar processo
pkill -f api.py
```

### Erro de Dependências

```bash
pip install -r requirements.txt
```
