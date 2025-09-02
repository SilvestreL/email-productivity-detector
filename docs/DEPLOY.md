# 🚀 Deploy - Email Classification

## Deploy Local

### Opção 1: Execução Direta

```bash
# Instalar dependências
pip install -r requirements.txt

# Treinar modelo (se necessário)
python scripts/run_bert.py

# Executar API
python api.py
```

### Opção 2: Script Automatizado

```bash
# Deploy completo (Streamlit + API + Nginx)
./scripts/deploy.sh local

# Deploy apenas API (API + Nginx)
./scripts/deploy.sh api

# Verificar saúde
./scripts/deploy.sh health
```

### Diferença entre os comandos:

- **`./scripts/deploy.sh local`**: Roda Streamlit (8501) + API (8000) + Nginx (80)
- **`./scripts/deploy.sh api`**: Roda apenas API (8000) + Nginx (80)

## 🐳 Deploy com Docker

### Docker Compose (Recomendado)

```bash
# API com Docker
docker-compose -f docker-compose.api.yml up

# Aplicação completa
docker-compose up
```

### Docker Manual

```bash
# Build
docker build -t email-classifier .

# Run
docker run -p 8000:8000 email-classifier
```

## ☁️ Deploy em Nuvem

### Render

1. Conectar repositório GitHub
2. Configurar build command: `pip install -r requirements.txt`
3. Configurar start command: `python api.py`
4. Configurar porta: `8000`

### Hugging Face Spaces

1. Criar novo Space
2. Upload dos arquivos
3. Configurar `requirements.txt`
4. Configurar `app.py` (renomear `api.py`)

### AWS/GCP/Azure

```bash
# Usar script de deploy
./scripts/deploy.sh cloud aws
./scripts/deploy.sh cloud gcp
./scripts/deploy.sh cloud azure
```

## 🔧 Configurações

### Variáveis de Ambiente

```bash
# Produção
export HOST=0.0.0.0
export PORT=8000
export DEVICE=cpu  # ou cuda se disponível
```

### Nginx (Opcional)

```bash
# Configurar proxy reverso
cp nginx.api.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/nginx.api.conf /etc/nginx/sites-enabled/
systemctl reload nginx
```

## 📊 Monitoramento

### Health Checks

```bash
# API
curl http://localhost:8000/health

# Docker
docker-compose -f docker-compose.api.yml ps
```

### Logs

```bash
# Docker logs
docker-compose -f docker-compose.api.yml logs -f

# Aplicação
tail -f logs/app.log
```

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Porta ocupada**

   ```bash
   lsof -i :8000
   pkill -f api.py
   ```

2. **Modelo não encontrado**

   ```bash
   python scripts/run_bert.py
   ```

3. **Dependências faltando**

   ```bash
   pip install -r requirements.txt
   ```

4. **Docker não inicia**
   ```bash
   docker system prune
   docker-compose down
   docker-compose up --build
   ```

### Verificações

```bash
# Verificar API
curl http://localhost:8000/health

# Verificar modelo
curl http://localhost:8000/model/info

# Teste completo
python scripts/test_api.py
```
