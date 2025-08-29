# 📧 Email Productivity Classifier - AutoU

Solução desenvolvida para **AutoU** que utiliza inteligência artificial para classificar emails e gerar respostas automáticas, liberando tempo da equipe.

## ✨ Funcionalidades Implementadas

### 🎯 **Classificação Inteligente**
- Detecta automaticamente se um email é **produtivo** ou **improdutivo**
- Modelo de ML com **98.39% de acurácia**
- Pipeline TF-IDF + Logistic Regression otimizado

### 💬 **Respostas Automáticas**
- Gera respostas personalizadas baseadas na classificação
- Templates específicos para diferentes tipos de email:
  - **Suporte Técnico**: Problemas, bugs, ajuda
  - **Status de Requisição**: Acompanhamento de processos
  - **Dúvidas sobre Sistema**: Orientações e tutoriais
  - **Solicitação de Arquivos**: Documentos e relatórios
  - **Agendamento**: Reuniões e encontros
  - **Felicitações/Agradecimentos**: Respostas cordiais
  - **Spam**: Filtros automáticos

### 📄 **Upload de Arquivos**
- Suporte para arquivos **.txt** e **.pdf**
- Extração automática de texto
- Validação de conteúdo de email
- Preview do conteúdo extraído

### 📊 **Métricas Detalhadas**
- Confiança da classificação (%)
- Probabilidades para cada categoria
- Gráficos interativos
- Informações do arquivo processado

### 🎨 **Interface Moderna**
- Design responsivo e intuitivo
- Tabs para diferentes métodos de entrada
- Exemplos interativos
- Botão para copiar respostas

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+** - Linguagem principal
- **Scikit-learn** - Machine Learning (TF-IDF + Logistic Regression)
- **Streamlit** - Interface web interativa
- **Pandas** - Manipulação de dados
- **PyPDF2** - Processamento de arquivos PDF
- **Joblib** - Serialização de modelos
- **NumPy** - Computação numérica

---

## 📂 Estrutura do Projeto

```
email-productivity-detector/
├── data/
│   └── spam.csv                    # Dataset (5.5k mensagens)
├── models/
│   └── email_spam_pipeline.joblib  # Modelo treinado
├── src/
│   ├── train.py                    # Script de treinamento
│   ├── app_streamlit.py            # App Streamlit principal
│   ├── response_generator.py       # Gerador de respostas
│   └── file_processor.py           # Processador de arquivos
├── index.html                      # Interface HTML
├── test_model.py                   # Teste do modelo
├── test_new_features.py            # Teste das novas funcionalidades
├── demo.py                         # Demonstração interativa
├── requirements.txt                # Dependências
├── README.md                       # Documentação principal
└── INSTRUCOES.md                   # Guia de uso
```

---

## 🚀 Como Usar

### 1. **Configuração Inicial**

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/email-productivity-classifier.git
cd email-productivity-detector

# Crie um ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2. **Treinar o Modelo**

```bash
# Execute o script de treinamento
python src/train.py
```

**Saída esperada:**
```
🤖 Email Productivity Classifier - Treinamento
==================================================
📊 Carregando dataset...
✅ Dataset carregado: 5572 mensagens
📈 Distribuição: {'ham': 4825, 'spam': 747}
🔧 Criando pipeline de ML...
🚀 Iniciando treinamento...
📚 Treino: 4457 mensagens
🧪 Teste: 1115 mensagens
🎯 Acurácia: 0.9839
💾 Salvando modelo...
✅ Modelo salvo em: models/email_spam_pipeline.joblib
🎉 Treinamento concluído com sucesso!
```

### 3. **Usar a Aplicação**

```bash
# Inicie o app Streamlit
streamlit run src/app_streamlit.py
```

Acesse: [http://localhost:8501](http://localhost:8501)

### 4. **Métodos de Entrada**

#### 📄 **Upload de Arquivo**
1. Clique na aba "Upload de Arquivo"
2. Arraste um arquivo .txt ou .pdf ou clique para selecionar
3. Visualize o conteúdo extraído
4. Clique em "Analisar Email"

#### ✏️ **Texto Direto**
1. Clique na aba "Texto Direto"
2. Cole o conteúdo do email na área de texto
3. Clique em "Classificar Mensagem"

### 5. **Resultados**

Após a análise, você verá:
- ✅ **Classificação**: Produtivo ou Improdutivo
- 📊 **Confiança**: Porcentagem de confiança
- 📈 **Probabilidades**: Gráfico de barras
- 💬 **Resposta Automática**: Sugestão de resposta
- 📋 **Botão para Copiar**: Copie a resposta gerada

---

## 🎯 Exemplos de Uso

### ✅ **Emails Produtivos**
- "Reunião importante amanhã às 10h para discutir o projeto"
- "Relatório mensal de vendas está pronto para revisão"
- "Preciso de ajuda com um problema técnico no sistema"
- "Gostaria de agendar uma reunião para discutir o projeto"

### ❌ **Emails Improdutivos**
- "CONGRATULATIONS! You've won a FREE iPhone!"
- "URGENT: Your account has been SUSPENDED!"
- "Feliz Natal! Desejo um ótimo ano novo para toda a equipe"
- "Obrigado pela ajuda. Valeu mesmo!"

---

## 📊 Performance do Modelo

- **Acurácia**: 98.39%
- **Precisão**: 99% (Produtivo), 93% (Improdutivo)
- **Recall**: 99% (Produtivo), 95% (Improdutivo)
- **Dataset**: 5.5k mensagens (4.8k ham, 747 spam)
- **Features**: TF-IDF com n-grams (1-3) + Engenharia de features

---

## 🧪 Testes

### Teste do Modelo
```bash
python test_model.py
```

### Teste das Novas Funcionalidades
```bash
python test_new_features.py
```

### Demonstração Interativa
```bash
python demo.py
```

---

## 🎨 Interface HTML

O projeto inclui uma interface HTML (`index.html`) que serve como landing page e redireciona para a aplicação Streamlit.

**Características:**
- Design moderno e responsivo
- Informações sobre funcionalidades
- Métricas do sistema
- Botão de acesso direto à aplicação

---

## 🔮 Próximos Passos

- [x] **Classificação de emails** ✅
- [x] **Geração de respostas automáticas** ✅
- [x] **Upload de arquivos (.txt/.pdf)** ✅
- [x] **Interface HTML** ✅
- [ ] **Deploy na nuvem** (Streamlit Cloud, Heroku, etc.)
- [ ] **API REST** para integração
- [ ] **Modelos alternativos** (XGBoost, BERT)
- [ ] **Explicabilidade** (palavras-chave)
- [ ] **Histórico de predições**
- [ ] **Upload de múltiplos arquivos**

---

## 🚨 Solução de Problemas

### Erro: "Modelo não encontrado"
```bash
# Execute primeiro o treinamento
python src/train.py
```

### Erro: "ModuleNotFoundError"
```bash
# Ative o ambiente virtual
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Port already in use"
```bash
# Use uma porta diferente
streamlit run src/app_streamlit.py --server.port 8502
```

---

## 🤝 Contribuição

Sinta-se à vontade para abrir **issues** e enviar **pull requests**.

### Como contribuir:
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- **AutoU** pelo desafio técnico
- Dataset: [SMS Spam Collection](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset)
- Scikit-learn pela biblioteca de ML
- Streamlit pela plataforma de apps web

---

**🎉 Solução completa desenvolvida para AutoU - Email Productivity Classifier v2.0**

**🤖 Machine Learning + 💬 Respostas Automáticas + 📄 Upload de Arquivos**
