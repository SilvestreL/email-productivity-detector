# 🐳 Docker - Email Productivity Classifier

Este documento contém instruções para containerizar e executar a aplicação **Email Productivity Classifier** usando Docker.

## 📋 Pré-requisitos

- **Docker** instalado ([Instalar Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** instalado ([Instalar Docker Compose](https://docs.docker.com/compose/install/))

## 🚀 Execução Rápida

### Opção 1: Scripts Automatizados (Recomendado)

```bash
# Build da imagem
./docker-build.sh

# Executar aplicação
./docker-run.sh
```

### Opção 2: Comandos Manuais

```bash
# Build da imagem
docker build -t email-productivity-classifier .

# Executar com docker-compose
docker-compose up -d
```

## 🌐 URLs de Acesso

Após executar a aplicação, você pode acessar:

- **📄 Interface HTML**: http://localhost
- **🤖 App Streamlit**: http://localhost:8501
- **🔗 Via Nginx**: http://localhost/streamlit/

## 🏗️ Arquitetura Docker

### Serviços

1. **email-classifier** (Streamlit)
   - Porta: 8501
   - Função: Aplicação principal
   - Health check: Automático

2. **nginx** (Web Server)
   - Porta: 80
   - Função: Proxy reverso e servidor web
   - Dependência: email-classifier

### Volumes

- **model_data**: Persistência do modelo treinado
- **./logs**: Logs da aplicação

## 📁 Estrutura de Arquivos Docker

```
email-productivity-detector/
├── Dockerfile                 # Configuração da imagem
├── docker-compose.yml         # Orquestração dos serviços
├── nginx.conf                 # Configuração do Nginx
├── .dockerignore              # Arquivos ignorados no build
├── docker-build.sh            # Script de build
├── docker-run.sh              # Script de execução
└── DOCKER_README.md           # Este arquivo
```

## 🔧 Comandos Úteis

### Build e Execução

```bash
# Build da imagem
docker build -t email-productivity-classifier .

# Executar apenas o Streamlit
docker run -p 8501:8501 email-productivity-classifier

# Executar com docker-compose
docker-compose up -d

# Parar serviços
docker-compose down

# Rebuild e executar
docker-compose up --build -d
```

### Monitoramento

```bash
# Ver logs do Streamlit
docker-compose logs -f email-classifier

# Ver logs do Nginx
docker-compose logs -f nginx

# Ver status dos containers
docker-compose ps

# Ver uso de recursos
docker stats
```

### Manutenção

```bash
# Limpar containers parados
docker container prune

# Limpar imagens não utilizadas
docker image prune

# Limpar volumes não utilizados
docker volume prune

# Limpar tudo
docker system prune -a
```

## ⚙️ Configurações

### Variáveis de Ambiente

```yaml
# docker-compose.yml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_SERVER_HEADLESS=true
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Portas

- **8501**: Streamlit (acesso direto)
- **80**: Nginx (proxy reverso)

### Volumes

- **model_data**: Persistência do modelo ML
- **./logs**: Logs da aplicação

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Porta já em uso
```bash
# Verificar portas em uso
lsof -i :8501
lsof -i :80

# Parar serviços conflitantes
sudo lsof -ti:8501 | xargs kill -9
```

#### 2. Erro de permissão
```bash
# Dar permissão aos scripts
chmod +x docker-build.sh docker-run.sh
```

#### 3. Imagem não encontrada
```bash
# Rebuild da imagem
docker-compose build --no-cache
```

#### 4. Erro de memória
```bash
# Aumentar memória do Docker
# Docker Desktop > Settings > Resources > Memory
```

### Logs de Debug

```bash
# Logs detalhados
docker-compose logs -f --tail=100 email-classifier

# Executar em modo interativo
docker-compose run --rm email-classifier bash
```

## 🚀 Deploy em Produção

### 1. Build para Produção

```bash
# Build otimizado
docker build -t email-productivity-classifier:prod .

# Tag para registry
docker tag email-productivity-classifier:prod your-registry/email-classifier:latest
```

### 2. Deploy com Docker Compose

```bash
# Arquivo docker-compose.prod.yml
version: '3.8'
services:
  email-classifier:
    image: your-registry/email-classifier:latest
    restart: always
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
    volumes:
      - model_data:/app/models
```

### 3. Monitoramento

```bash
# Health check
curl http://localhost/health

# Métricas
docker stats email-productivity-classifier
```

## 📊 Performance

### Otimizações

1. **Multi-stage build** (se necessário)
2. **Cache de dependências**
3. **Compressão de imagens**
4. **Health checks**

### Recursos Recomendados

- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB

## 🔒 Segurança

### Configurações Implementadas

- **Nginx**: Headers de segurança
- **Docker**: Usuário não-root
- **Streamlit**: Modo headless
- **Volumes**: Isolamento de dados

### Recomendações Adicionais

1. **HTTPS**: Configurar SSL/TLS
2. **Firewall**: Restringir portas
3. **Secrets**: Usar Docker secrets
4. **Updates**: Manter imagens atualizadas

## 📝 Exemplos de Uso

### Desenvolvimento

```bash
# Desenvolvimento local
docker-compose up -d

# Testes
docker-compose run --rm email-classifier python test_model.py
```

### Produção

```bash
# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Backup
docker run --rm -v model_data:/data -v $(pwd):/backup alpine tar czf /backup/model-backup.tar.gz -C /data .
```

---

## 🎉 Conclusão

A containerização da aplicação **Email Productivity Classifier** está completa e pronta para:

- ✅ **Desenvolvimento local**
- ✅ **Testes automatizados**
- ✅ **Deploy em produção**
- ✅ **Escalabilidade horizontal**
- ✅ **Monitoramento e logs**

**A aplicação está pronta para ser deployada em qualquer ambiente que suporte Docker!**
