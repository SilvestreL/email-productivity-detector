# Classificador de Produtividade de E-mails

Aplicação Streamlit para classificar e-mails em **Produtivo** ou **Improdutivo** e sugerir respostas automáticas baseadas na classificação.

## 🚀 Funcionalidades

- **Classificação Automática**: Modelo BERT fine-tuned para classificar e-mails
- **Upload de Arquivos**: Suporte para arquivos .txt e .pdf
- **Respostas Sugeridas**: Templates automáticos baseados na classificação
- **Interface Minimalista**: Design limpo e profissional sem emojis
- **Sidebar Retrátil**: Interface organizada com opção de recolher
- **Métricas do Modelo**: Visualização de performance e acurácia
- **Histórico**: Rastreamento de classificações realizadas

## 📋 Pré-requisitos

- Python 3.8+
- pip ou conda
- Modelo treinado (incluído no repositório)

## 🛠️ Instalação Local

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/email-productivity-detector.git
cd email-productivity-detector
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
email-productivity-detector/
├── app.py                 # Aplicação principal Streamlit
├── inference.py           # Módulo de inferência do modelo
├── utils.py               # Utilitários e funções auxiliares
├── models/                # Modelos treinados
│   └── bert_prod_improd/ # Modelo BERT fine-tuned
├── metrics/               # Métricas e relatórios do modelo
├── data/                  # Dados e histórico
├── scripts/               # Scripts de teste e organização
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 🎯 Como Usar

### 1. Classificar E-mail

- **Opção A**: Cole o texto do e-mail diretamente
- **Opção B**: Faça upload de arquivo .txt ou .pdf
- Clique em "Classificar"
- Veja o resultado e resposta sugerida

### 2. Interface da Sidebar

- **Links**: GitHub e Documentação
- **Modelo**: Informações sobre o modelo carregado
- **Métricas**: Accuracy, Precision, Recall, F1
- **Como interpretar**: Explicações das métricas
- **Sobre o projeto**: Descrição e informações
- **Recolher barra**: Botão para retrair a sidebar

### 3. Navegação

- **Classificar**: Página principal para classificação
- **Métricas**: Performance e acurácia do modelo
- **Histórico**: Registro de classificações realizadas
- **Ajuda**: Instruções de uso e documentação

## 🚀 Deploy - Streamlit Cloud

### 1. Preparar Repositório

- **Fork** este repositório no GitHub
- **Verifique** se `app.py` está na raiz
- **Confirme** que `requirements.txt` está atualizado

### 2. Acessar Streamlit Cloud

- Acesse [share.streamlit.io](https://share.streamlit.io)
- Faça login com sua conta GitHub

### 3. Criar Nova Aplicação

1. Clique em **"New app"**
2. **Selecione** seu repositório forkado
3. **Configure**:
   - **Main file path**: `app.py`
   - **Python version**: 3.9
   - **Requirements file**: `requirements.txt`
4. Clique em **"Deploy"**

### 4. Configurar Modelo (Opcional)

Se usar modelo privado no Hugging Face Hub:

1. Vá em **"Settings"** → **"Secrets"**
2. Adicione:
   ```
   HUGGINGFACEHUB_API_TOKEN = seu_token_aqui
   ```

### 5. Acesso

- **URL pública**: `https://seu-app.streamlit.app`
- **Deploy automático** a cada push para `main`

## 🔧 Configuração

### Configuração do Modelo

#### Opção 1: Hugging Face Hub (Recomendado)

```bash
# Modelo público
MODEL_DIR=usuario/repositorio

# Modelo privado (requer token)
export HUGGINGFACEHUB_API_TOKEN=seu_token_aqui
MODEL_DIR=usuario/repositorio-privado
```

#### Opção 2: Modelo Local

```bash
# Diretório local do modelo
MODEL_DIR=models/bert_prod_improd
```

### Outras Variáveis

```bash
# Diretório de métricas (padrão: metrics)
METRICS_DIR=metrics

# Arquivo de histórico (padrão: data/email_history.csv)
HISTORY_FILE=data/email_history.csv
```

### Personalização

- **Templates de Resposta**: Edite as funções em `utils.py`
- **Estilo CSS**: Modifique o CSS inline no `app.py`
- **Modelo**: Substitua o modelo em `models/` pelo seu próprio

## 📊 Modelo

### Arquitetura

- **Base**: DistilBERT (distilbert-base-cased)
- **Fine-tuning**: Para classificação binária (Produtivo/Improdutivo)
- **Input**: Texto de e-mail (máximo 512 tokens)
- **Output**: Probabilidade para cada classe

### Performance

- **Accuracy**: ~90%
- **F1-Score**: ~90%
- **Precision**: ~90%
- **Recall**: ~90%

### Hospedagem

- **Recomendado**: Hugging Face Hub público
- **Alternativa**: Modelo local (apenas se pequeno)
- **Privado**: HF Hub com token de acesso

## 🧪 Testes e Desenvolvimento

### Scripts Disponíveis

```bash
cd scripts

# Testar modelo BERT
python test_bert_model.py

# Atualizar app para modelo local
python update_app_local.py

# Preparar modelo para Hugging Face Hub
python prepare_for_hub.py

# Organizar workflow completo
python organize_workflow.py

# Treinar modelo (se necessário)
python train.py

# Balancear dataset
python balance_dataset.py

# Aplicar oversampling
python apply_oversampling.py
```

### Testes do Modelo

```bash
cd scripts
python test_bert_model.py
```

**Resultados Esperados:**
- 📧 6/6 testes bem-sucedidos
- 📊 Confiança média: 83.20%
- ⏱️ Tempo médio: 616ms
- 🏷️ Distribuição: 5 Produtivos, 1 Improdutivo

### Treinamento (Opcional)

Se você quiser treinar seu próprio modelo:

```bash
cd scripts

# Preparar dataset
python prepare_dataset.py

# Balancear classes
python balance_dataset.py

# Treinar modelo
python train.py

# Testar resultados
python test_training.py
```

## 🐛 Troubleshooting

### Erro: "Modelo não encontrado"

- **HF Hub**: Verifique se o nome do repositório está correto
- **Local**: Confirme se `models/bert_prod_improd/` existe
- **Privado**: Configure `HUGGINGFACEHUB_API_TOKEN` nos Secrets

### Erro: "Dependências não encontradas"

- Verifique se `requirements.txt` está na raiz
- Confirme versão Python: 3.9 (Streamlit Cloud)
- Aguarde o build automático após push

### Erro: "Arquivo PDF não processado"

- Verifique se o arquivo não está corrompido
- Confirme se é .txt ou .pdf
- Tamanho máximo recomendado: 10MB

### Erro: "Cold Start Lento"

- Primeira execução: 2-5 minutos (download do modelo)
- Execuções seguintes: < 30 segundos (cache ativo)
- Use `@st.cache_resource` para otimização

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/email-productivity-detector/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/email-productivity-detector/wiki)
- **Email**: seu-email@exemplo.com

## 🙏 Agradecimentos

- [Hugging Face](https://huggingface.co/) pelos modelos e bibliotecas
- [Streamlit](https://streamlit.io/) pela plataforma de desenvolvimento
- Comunidade open source por contribuições e feedback

---

**Desenvolvido com ❤️ para melhorar a produtividade no trabalho com e-mails**
