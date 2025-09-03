# 📧 Email Productivity Classifier - 

## 🎯 **Solução Completa para Classificação de Emails**

Sistema inteligente de classificação de emails em **Produtivos** ou **Improdutivos** com geração automática de respostas, desenvolvido para o teste técnico da **AutoU**.

---

## 🚀 **Funcionalidades Principais**

- ✅ **Classificação Inteligente**: ML com 98.39% de acurácia
- ✅ **Respostas Automáticas**: 7 categorias específicas
- ✅ **Upload de Arquivos**: Suporte a .txt e .pdf
- ✅ **Interface Web**: Streamlit moderno e responsivo
- ✅ **API REST**: Integração com qualquer sistema
- ✅ **Containerização**: Docker completo
- ✅ **Documentação**: Automática e interativa

---

## 🏗️ **Arquitetura**

```
email-productivity-detector/
├── 📁 src/                    # Core da aplicação
│   ├── app_streamlit.py       # Interface web
│   ├── api.py                 # API REST
│   ├── train.py               # Treinamento do modelo
│   ├── response_generator.py  # Gerador de respostas
│   └── file_processor.py      # Processador de arquivos
├── 📁 scripts/                # Scripts de execução
├── 📁 tests/                  # Testes automatizados
├── 📁 docs/                   # Documentação completa
├── 📁 models/                 # Modelos treinados
├── 📁 data/                   # Dataset
└── 🐳 Docker/                 # Containerização
```

---

## 🚀 **Como Usar**

### **1. Interface Web (Streamlit)**

```bash
# Executar localmente
python src/app_streamlit.py

# Ou com Docker
./scripts/docker-run.sh
```

### **2. API REST**

```bash
# Executar localmente
./scripts/run-api.sh

# Ou com Docker
./scripts/run-api-docker.sh
```

### **3. Treinar Modelo**

```bash
python src/train.py
```

### **4. Executar Testes**

```bash
# Testes do modelo
python tests/test_model.py

# Testes das funcionalidades
python tests/test_new_features.py

# Testes da API
python tests/test_api.py
```

---

## 🌐 **URLs de Acesso**

### **Interface Web**

- **Streamlit**: http://localhost:8501
- **HTML**: http://localhost

### **API REST**

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📊 **Performance**

- **Acurácia**: 98.39%
- **Latência**: < 10ms
- **Throughput**: ~1000 emails/segundo
- **Categorias**: 7 tipos de resposta automática

---

## 🐳 **Containerização**

### **Executar com Docker**

```bash
# Build da imagem
./scripts/docker-build.sh

# Executar aplicação
./scripts/docker-run.sh

# Executar API
./scripts/run-api-docker.sh
```

### **URLs com Docker**

- **Interface**: http://localhost
- **Streamlit**: http://localhost:8501
- **API**: http://localhost:8000

---

## 📚 **Documentação Detalhada**

- **[📖 Documentação Completa](docs/README.md)**
- **[🐳 Docker](docs/DOCKER_README.md)**
- **[🔗 API REST](docs/API_IMPLEMENTACAO.md)**
- **[📦 Containerização](docs/CONTAINERIZACAO_COMPLETA.md)**
- **[📋 Resumo da Implementação](docs/RESUMO_IMPLEMENTACAO.md)**

---

## 🧪 **Testes**

### **Executar Todos os Testes**

```bash
# Teste do modelo
python tests/test_model.py

# Teste das funcionalidades
python tests/test_new_features.py

# Teste da API
python tests/test_api.py

# Demo interativo
python tests/demo.py
```

---

## 🔧 **Tecnologias**

- **Python 3.10+**
- **Streamlit** - Interface web
- **FastAPI** - API REST
- **Scikit-learn** - Machine Learning
- **Docker** - Containerização
- **Nginx** - Proxy reverso

---

## 📋 **Requisitos do Sistema**

- **Python**: 3.10 ou superior
- **Docker**: 20.10+ (opcional)
- **RAM**: 4GB mínimo
- **Storage**: 2GB livre

---

## 🚀 **Deploy**

### **Local**

```bash
# Instalar dependências
pip install -r requirements.txt

# Treinar modelo
python src/train.py

# Executar aplicação
python src/app_streamlit.py
```

### **Docker**

```bash
# Build e execução
./scripts/docker-run.sh
```

### **Cloud**

- **AWS ECS**: Compatível
- **Google Cloud Run**: Compatível
- **Azure Container Instances**: Compatível
- **Kubernetes**: Compatível

---

## 🎯 **Casos de Uso**

### **Para Empresas**

- **Automatização** de triagem de emails
- **Redução** de tempo de resposta
- **Melhoria** da produtividade da equipe
- **Integração** com sistemas existentes

### **Para Desenvolvedores**

- **API REST** para integração
- **Documentação** automática
- **Testes** automatizados
- **Containerização** pronta

---

## 📞 **Suporte**

### **Problemas Comuns**

- Verificar se o modelo foi treinado
- Confirmar que as dependências estão instaladas
- Verificar se as portas estão disponíveis

### **Logs**

```bash
# Logs da aplicação
docker-compose logs -f

# Logs da API
docker-compose -f docker-compose.api.yml logs -f
```

---

## 🎉 **Conclusão**

Solução completa e funcional para classificação de emails, desenvolvida especificamente para o teste técnico da **AutoU**.


---


