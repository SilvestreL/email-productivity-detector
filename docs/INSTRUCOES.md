# 📋 Instruções de Uso - Email Productivity Classifier

## 🚀 Como Usar o Sistema

### 1. **Configuração Inicial**

```bash
# Clone o repositório (se ainda não fez)
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

### 3. **Usar a Interface Web (Recomendado)**

```bash
# Inicie o app Streamlit
streamlit run src/app_streamlit.py
```

Acesse: [http://localhost:8501](http://localhost:8501)

**Como usar:**
1. Cole uma mensagem na área de texto
2. Clique em "🔍 Classificar Mensagem"
3. Veja o resultado e métricas

### 4. **Testar o Modelo**

```bash
# Execute o script de teste
python test_model.py

# Ou execute a demonstração
python demo.py
```

## 📊 Performance do Modelo

- **Acurácia**: 98.39%
- **Precisão**: 99% (Produtivo), 93% (Improdutivo)
- **Recall**: 99% (Produtivo), 95% (Improdutivo)

## 🎯 Exemplos de Uso

### ✅ Mensagens Produtivas (Ham)
- "Reunião importante amanhã às 10h"
- "Relatório mensal de vendas está pronto"
- "Confirmação de entrega do pedido #12345"
- "Olá, gostaria de agendar uma reunião"

### ❌ Mensagens Improdutivas (Spam)
- "CONGRATULATIONS! You've won a FREE iPhone!"
- "URGENT: Your account has been SUSPENDED!"
- "Make $5000/day working from home!"
- "FREE VIAGRA NOW!!! Click here!"

## 🔧 Funcionalidades

### Interface Web (Streamlit)
- 🎨 Design moderno e responsivo
- 📊 Métricas detalhadas (confiança, probabilidades)
- 📈 Gráficos de probabilidades
- 🧪 Exemplos interativos
- 📱 Interface mobile-friendly

### Scripts de Teste
- `test_model.py`: Testa com exemplos conhecidos
- `demo.py`: Demonstração interativa completa

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Scikit-learn**: Machine Learning
- **Streamlit**: Interface Web
- **Pandas**: Manipulação de Dados
- **Joblib**: Serialização de Modelos
- **TF-IDF**: Extração de Features
- **Logistic Regression**: Classificação

## 📁 Estrutura de Arquivos

```
email-productivity-detector/
├── data/
│   └── spam.csv              # Dataset (5.5k mensagens)
├── models/
│   └── email_spam_pipeline.joblib  # Modelo treinado
├── src/
│   ├── train.py              # Script de treinamento
│   └── app_streamlit.py      # App Streamlit
├── test_model.py             # Script de teste
├── demo.py                   # Demonstração
├── requirements.txt          # Dependências
├── README.md                 # Documentação principal
└── INSTRUCOES.md            # Este arquivo
```

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

# Instale as dependências
pip install -r requirements.txt
```

### Erro: "Port already in use"
```bash
# Use uma porta diferente
streamlit run src/app_streamlit.py --server.port 8502
```

## 📈 Melhorias Implementadas

1. **Features de Engenharia**:
   - Contagem de caracteres especiais (!, ?, maiúsculas, números)
   - Detecção de URLs
   - Palavras-chave suspeitas
   - Comprimento da mensagem

2. **Pipeline Otimizado**:
   - TF-IDF com n-grams (1-3)
   - Logistic Regression com class_weight='balanced'
   - Parâmetros otimizados

3. **Interface Melhorada**:
   - Design responsivo
   - Métricas detalhadas
   - Exemplos interativos

## 🔮 Próximos Passos

- [ ] Explicabilidade (palavras-chave)
- [ ] Deploy na nuvem
- [ ] API REST
- [ ] Modelos alternativos (XGBoost, BERT)
- [ ] Upload de arquivos
- [ ] Histórico de predições

## 📞 Suporte

Se encontrar problemas:
1. Verifique se o ambiente virtual está ativo
2. Confirme se todas as dependências estão instaladas
3. Execute `python test_model.py` para verificar o modelo
4. Consulte o README.md para mais detalhes

---

**🎉 Sistema pronto para uso!**
