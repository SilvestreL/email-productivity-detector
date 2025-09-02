# 📧 Email Productivity Classifier

> **Classificador de Emails com IA usando BERT Fine-tuned em Português**  
> Sistema inteligente para classificar emails em Produtivo/Improdutivo e gerar respostas automáticas

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37.1+-red.svg)](https://streamlit.io)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-BERT-yellow.svg)](https://huggingface.co)
[![Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue.svg)](https://huggingface.co/spaces)

---

## 🎯 **Visão Geral**

Sistema completo de classificação de emails que:

- 🤖 **Classifica emails** em Produtivo ou Improdutivo usando BERT fine-tuned em português
- 📁 **Suporta upload** de arquivos .txt e .pdf além de entrada de texto
- 🔤 **Pré-processamento NLP** em português brasileiro (remoção de stopwords)
- 💬 **Gera respostas automáticas** baseadas na classificação e tom selecionado
- 🌐 **Interface web** moderna e intuitiva com Streamlit
- ⚡ **Cache inteligente** para performance otimizada
- 🚀 **Pronto para Hugging Face Spaces** - zero configuração
- 🎯 **Modelo treinado** especificamente para classificação de produtividade de emails

---

## 🚀 **Como Usar Online**

### **Hugging Face Spaces**

1. Acesse o link do Space: [🔗 Link do Space]
2. **3 passos simples**:
   - **1️⃣** Envie arquivo (.txt/.pdf) ou cole o texto do email
   - **2️⃣** Escolha o tom da resposta (profissional, amigável, formal)
   - **3️⃣** Clique em "Analisar Email"
3. Veja a classificação e resposta sugerida

**Zero instalação necessária!** 🎉

---

## 🤖 **Sobre o Modelo**

### **Modelo Fine-tuned**

- **Base**: `neuralmind/bert-base-portuguese-cased` (BERT em português)
- **Dataset**: Adaptado de spam.csv para classificação de produtividade
- **Labels**: Produtivo (ham) vs Improdutivo (spam)
- **Métricas**: Accuracy e F1-score otimizados para classificação de emails
- **Hub**: [🔗 Link do modelo no Hugging Face Hub](https://huggingface.co/SEU_USUARIO/email-prod-improd-ptbr-bert)

### **Fine-tuning Process**

O modelo foi fine-tuned seguindo estas etapas:

1. **Preparação do Dataset**: Conversão de spam.csv para formato de classificação de produtividade
2. **Treinamento**: Fine-tuning do BERT português com 3 épocas
3. **Validação**: Métricas de accuracy e F1-score
4. **Deploy**: Upload para Hugging Face Hub

### **Reproduzir o Treinamento**

```bash
# 1. Preparar dataset
python scripts/prepare_dataset.py

# 2. Treinar modelo
python scripts/train.py

# 3. Configurar MODEL_ID no app.py
```

---

## 🛠️ **Como Rodar Localmente**

### **Pré-requisitos**

- Python 3.10+
- pip

### **Instalação**

```bash
# Clone o repositório
git clone <repository-url>
cd email-productivity-detector

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run app.py
```

### **Acesso Local**

- 🌐 **Interface Web**: http://localhost:8501

---

## 🏗️ **Stack Tecnológica**

```
👤 Usuário → 🌐 Streamlit → 📁 Upload/Texto → 🔤 NLP PT-BR → 🤖 DistilBERT MNLI → 💬 Templates → 📧 Resposta
```

### **Componentes**

- **Frontend**: Streamlit (interface web moderna)
- **Modelo**: BERT português fine-tuned (text classification)
- **Classificação**: Labels Produtivo/Improdutivo
- **Upload**: Suporte a .txt e .pdf
- **NLP**: Pré-processamento em português (stopwords)
- **Respostas**: Templates baseados na categoria e tom
- **Cache**: @st.cache_resource para performance

---

## 📁 **Estrutura do Projeto**

```
email-productivity-detector/
├── 📄 README.md                    # Este arquivo
├── 🚀 app.py                       # Aplicação principal (Streamlit)
├── 📋 requirements.txt             # Dependências da aplicação
├── 📋 requirements-train.txt       # Dependências para treinamento
├── 📁 scripts/                     # Scripts de treinamento
│   ├── prepare_dataset.py          # Preparação do dataset
│   └── train.py                    # Treinamento do modelo
├── 📁 data/                        # Dados
│   ├── spam.csv                    # Dataset original
│   └── processed/                  # Dataset processado
├── 📁 models/                      # Modelos treinados
│   └── email-prod-improd-ptbr-bert/ # Modelo fine-tuned
└── 📁 docs/                        # Documentação
    ├── API.md                      # Documentação da API (referência)
    └── DEPLOY.md                   # Guia de deploy (referência)
```

---

## 🧪 **Como Usar**

### **1. Interface Web - 3 Passos Simples**

#### **1️⃣ Envie arquivo ou cole texto**

- **Upload**: Arquivos .txt ou .pdf
- **Texto**: Cole o conteúdo diretamente
- **Prioridade**: Arquivo tem prioridade sobre texto colado

#### **2️⃣ Escolha o tom da resposta**

- **Profissional**: Tom corporativo formal
- **Amigável**: Tom descontraído e próximo
- **Formal**: Tom institucional

#### **3️⃣ Clique em Analisar**

- Veja a classificação (Produtivo/Improdutivo)
- Receba resposta sugerida personalizada

### **2. Funcionalidades**

- ✅ **Classificação Fine-tuned**: Modelo treinado especificamente para emails
- ✅ **Upload de Arquivos**: .txt e .pdf suportados
- ✅ **Pré-processamento NLP**: Stopwords em português brasileiro
- ✅ **Cache Inteligente**: Modelo carregado apenas uma vez
- ✅ **Templates Personalizados**: Respostas para Produtivo e Improdutivo
- ✅ **Múltiplos Tons**: Profissional, amigável, formal
- ✅ **Métricas Detalhadas**: Confiança, scores, tempo, tamanho do texto
- ✅ **Interface Responsiva**: Funciona em desktop e mobile

---

## 🔧 **Arquitetura Técnica**

### **Modelo**

- **Base**: `neuralmind/bert-base-portuguese-cased`
- **Método**: Text Classification (Fine-tuned)
- **Labels**: `{0: "Improdutivo", 1: "Produtivo"}`
- **Cache**: `@st.cache_resource` para evitar recarga
- **Hub**: Modelo disponível no Hugging Face Hub

### **Classificação**

```python
# Exemplo de uso
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

tokenizer = AutoTokenizer.from_pretrained("SEU_USUARIO/email-prod-improd-ptbr-bert")
model = AutoModelForSequenceClassification.from_pretrained("SEU_USUARIO/email-prod-improd-ptbr-bert")
classifier = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)
result = classifier(text)
```

### **Pré-processamento NLP**

- **Stopwords**: Remoção de palavras irrelevantes em português
- **Normalização**: Limpeza de espaços e caracteres especiais
- **Tokenização**: Processamento por palavras
- **Opcional**: Stemming com RSLP (comentado no código)

### **Upload de Arquivos**

- **.txt**: Decodificação UTF-8
- **.pdf**: Extração de texto com pdfplumber
- **Prioridade**: Arquivo > Texto colado

### **Respostas**

- **Produtivo**: Solicita confirmação de objetivo/prazo/anexos
- **Improdutivo**: Agradece e indica que não requer ação
- **Tons**: Profissional, amigável, formal
- **Personalização**: Inclui assunto original

---

## 📊 **Performance**

- **Modelo**: BERT português fine-tuned
- **Dispositivo**: CPU/GPU automático
- **Latência**: < 1s por classificação (após cache)
- **Cold Start**: ~3-5s na primeira execução
- **Cache**: Ativado para performance otimizada
- **NLP**: Processamento rápido de stopwords
- **Métricas**: Accuracy e F1-score otimizados para classificação de emails

---

## 🚀 **Deploy em Hugging Face Spaces**

### **Configuração**

1. Criar novo Space no Hugging Face
2. Selecionar **SDK: Streamlit**
3. Upload dos arquivos:
   - `app.py`
   - `requirements.txt`
   - `README.md`

### **Arquivos Necessários**

- ✅ `app.py` - Aplicação principal
- ✅ `requirements.txt` - Dependências
- ✅ `README.md` - Documentação

### **Configuração Automática**

O Space detecta automaticamente:

- SDK: Streamlit
- Entry point: `app.py`
- Dependências: `requirements.txt`

---

## 🔍 **Troubleshooting**

### **Problemas Comuns**

1. **Cold Start Lento**

   - ⏱️ Primeira execução: ~3-5s
   - ✅ Execuções seguintes: < 1s (cache ativo)

2. **Modelo Não Carrega**

   - 🔄 Recarregue a página
   - 📡 Verifique conexão com Hugging Face

3. **Erro de Dependências**

   - 📋 Verifique `requirements.txt`
   - 🔄 Reinstale dependências

4. **Upload de Arquivo Falha**
   - 📁 Verifique se é .txt ou .pdf
   - 🔤 Certifique-se que o arquivo não está corrompido

### **Logs**

```bash
# Local
streamlit run app.py --logger.level debug

# Hugging Face Spaces
# Logs disponíveis na interface do Space
```

---

## 📚 **Documentação Adicional**

- [📖 **API Reference**](docs/API.md) - Documentação da API (referência histórica)
- [🚀 **Deploy Guide**](docs/DEPLOY.md) - Guia de deploy (referência histórica)

---

## 🛠️ **Tecnologias**

- **Python 3.10+**: Linguagem principal
- **Streamlit 1.37.1+**: Interface web moderna
- **Hugging Face Transformers 4.43.3+**: BERT fine-tuned
- **PyTorch 2.6.0+**: Backend de ML
- **pdfplumber 0.11.4+**: Extração de texto de PDFs
- **NLTK 3.9.1+**: Processamento de linguagem natural
- **Text Classification**: Modelo fine-tuned para classificação de emails

---

## 🔧 **Desenvolvimento**

```bash
# Setup local
git clone <repository-url>
cd email-productivity-detector
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

---

## 🧪 **Testes**

```bash
# Teste local
streamlit run app.py

# Teste de funcionalidades
# 1. Teste com email produtivo
# 2. Teste com email improdutivo
# 3. Teste com upload de .txt
# 4. Teste com upload de .pdf
# 5. Teste com diferentes tons
# 6. Verificar cache e performance
```

---

## 📄 **Licença**

Este projeto está licenciado sob a **MIT License**.

---

## 🙏 **Agradecimentos**

- **Hugging Face** pelo BERT português e infraestrutura
- **Streamlit** pela interface web moderna
- **NeuralMind** pelo modelo BERT em português
- **NLTK** pelo processamento de linguagem natural

---

**🚀 Email Productivity Classifier - Pronto para Hugging Face Spaces!**
