# 📋 Instruções de Deploy - Hugging Face Spaces

## 🎯 Visão Geral

Este guia explica como fazer deploy da aplicação **Email Productivity Classifier** no Hugging Face Spaces usando Docker.

## 🚀 Método 1: Deploy Automático (Recomendado)

### Passo 1: Preparar o Repositório

1. **Fork este repositório** no GitHub
2. **Clone para sua máquina local**:
   ```bash
   git clone https://github.com/SEU-USERNAME/email-productivity-detector.git
   cd email-productivity-detector
   ```

### Passo 2: Criar o Space no Hugging Face

1. Acesse [Hugging Face Spaces](https://huggingface.co/spaces)
2. Clique em **"Create new Space"**
3. Configure:
   - **Owner**: Seu username
   - **Space name**: `email-productivity-classifier`
   - **SDK**: **Docker** (importante!)
   - **License**: MIT
4. Clique em **"Create Space"**

### Passo 3: Conectar com GitHub

1. No Space criado, clique em **"Settings"**
2. Em **"Repository"**, clique em **"Connect to GitHub"**
3. Selecione seu repositório forkado
4. **Ative o deploy automático**

### Passo 4: Primeiro Deploy

1. Faça um commit e push para o repositório:
   ```bash
   git add .
   git commit -m "Initial commit for HF Spaces"
   git push origin main
   ```
2. O deploy automático começará imediatamente
3. Aguarde alguns minutos para o build completar

## 🐳 Método 2: Deploy Manual com Docker

### Pré-requisitos

- Docker instalado e rodando
- Conta no Hugging Face
- Token de acesso (Settings > Access Tokens)

### Passo 1: Login no Hugging Face

```bash
# Faça login no Container Registry do HF
docker login registry.hf.space
# Use seu token de acesso quando solicitado
```

### Passo 2: Build e Deploy

```bash
# Execute o script de deploy automatizado
./deploy.sh

# OU faça manualmente:
docker build -t email-classifier .
docker tag email-classifier registry.hf.space/SEU-USERNAME/email-productivity-classifier:latest
docker push registry.hf.space/SEU-USERNAME/email-productivity-classifier:latest
```

## 🔧 Configurações do Space

### Arquivo `.huggingface/spaces.toml`

Este arquivo já está configurado com:

- **SDK**: Docker
- **Porta**: 7860
- **Recursos**: 2 CPU, 8GB RAM
- **Health check** configurado

### Variáveis de Ambiente

O Dockerfile já configura:

- `STREAMLIT_SERVER_PORT=7860`
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- `PYTHONPATH=/app`

## 🧪 Teste Local

### Com Docker Compose

```bash
# Build e execução
docker-compose up --build

# Acesse: http://localhost:7860
```

### Com Docker Direto

```bash
# Build
docker build -t email-classifier .

# Execução
docker run -p 7860:7860 email-classifier

# Acesse: http://localhost:7860
```

## 📊 Monitoramento

### Health Check

- Endpoint: `/_stcore/health`
- Verifica se a aplicação está rodando
- Configurado no Dockerfile

### Logs

- Acesse o Space no HF
- Clique em **"Logs"** para ver os logs em tempo real
- Útil para debug

## 🚨 Troubleshooting

### Erro: "Model not found"

- Verifique se o diretório `models/` está incluído no repositório
- O modelo deve estar em `models/model_distilbert_cased/`

### Erro: "Port already in use"

- A porta 7860 é padrão para Streamlit
- Verifique se não há outro serviço usando esta porta

### Erro: "Build failed"

- Verifique os logs do build no HF
- Confirme se o Dockerfile está correto
- Verifique se todas as dependências estão no requirements.txt

### Erro: "Permission denied"

- Execute: `chmod +x deploy.sh`
- Verifique permissões do Docker

## 🔄 Atualizações

### Deploy Automático

- Faça push para o repositório
- O deploy acontece automaticamente

### Deploy Manual

- Execute novamente: `./deploy.sh`
- Ou faça o processo manual

## 📱 Acesso à Aplicação

Após o deploy bem-sucedido:

- **URL**: `https://huggingface.co/spaces/SEU-USERNAME/email-productivity-classifier`
- **Status**: Verifique se está "Running" no dashboard

## 🎉 Pronto!

Sua aplicação estará disponível publicamente no Hugging Face Spaces com:

- ✅ Interface web responsiva
- ✅ Classificação de emails em tempo real
- ✅ Suporte multilíngue
- ✅ Sugestão de respostas
- ✅ Upload de arquivos
- ✅ Performance otimizada

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do Space
2. Consulte a documentação do HF
3. Abra uma issue no repositório
4. Entre em contato: lucassilvestreee@gmail.com

---

**Status**: ✅ Configurado para Deploy no Hugging Face Spaces
