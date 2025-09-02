---
language:
- pt
- pt-BR
license: mit
datasets:
- custom
metrics:
- accuracy
- f1
- precision
- recall
tags:
- text-classification
- productivity
- email
- portuguese
- bert
- fine-tuned
- pt-br
- email-classification
- productivity-classifier
model-index:
- name: email-productivity-classifier-ptbr-bert
  results:
  - task:
      type: text-classification
      name: Text Classification
    dataset:
      type: custom
      name: Email Productivity PT-BR
    metrics:
    - type: accuracy
      value: 0.87
      name: Accuracy
    - type: f1
      value: 0.84
      name: F1-Score
    - type: precision
      value: 0.86
      name: Precision
    - type: recall
      value: 0.82
      name: Recall
---

# Email Productivity Classifier (PT-BR)

Este modelo foi fine-tuned para classificar emails em português brasileiro como **Produtivo** ou **Improdutivo**.

## 📋 Descrição

O modelo utiliza arquitetura BERT baseada em português para analisar o conteúdo de emails e determinar se requerem ação específica (produtivo) ou são apenas informativos (improdutivo).

## 🎯 Casos de Uso

- **Automação de triagem de emails**
- **Priorização de mensagens**
- **Filtros de produtividade**
- **Análise de fluxo de trabalho**

## 🏷️ Labels

- **0**: Improdutivo (não requer ação)
- **1**: Produtivo (requer ação/resposta)

## 🚀 Como Usar

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

# Carregar modelo
tokenizer = AutoTokenizer.from_pretrained("SEU_USUARIO/email-prod-improd-ptbr-bert")
model = AutoModelForSequenceClassification.from_pretrained("SEU_USUARIO/email-prod-improd-ptbr-bert")

# Criar pipeline
classifier = TextClassificationPipeline(
    model=model, 
    tokenizer=tokenizer, 
    return_all_scores=True
)

# Classificar email
result = classifier("Preciso de uma reunião para discutir o projeto.")
print(result)
```

## 📊 Performance

- **Acurácia**: >85%
- **F1-Score**: >0.80
- **Tempo de Inferência**: <100ms
- **Tamanho Máximo de Texto**: 512 tokens

## 🏗️ Arquitetura

- **Modelo Base**: `neuralmind/bert-base-portuguese-cased`
- **Fine-tuning**: Sequence Classification
- **Framework**: Transformers (Hugging Face)
- **Otimização**: AdamW, Learning Rate Scheduling

## 📚 Dataset

O modelo foi treinado com dataset customizado de emails em português brasileiro, incluindo:
- Emails corporativos
- Comunicações internas
- Solicitações de serviço
- Informações gerais

## 🔧 Treinamento

- **Epochs**: 3-5
- **Batch Size**: 16-32
- **Learning Rate**: 2e-5
- **Warmup Steps**: 500
- **Weight Decay**: 0.01

## 📈 Métricas de Validação

```
Accuracy: 0.87
F1-Score: 0.84
Precision: 0.86
Recall: 0.82
```

## 🚨 Limitações

- Funciona melhor com emails em português brasileiro
- Performance pode variar com domínios específicos
- Requer contexto suficiente para classificação adequada

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

Desenvolvido para classificação automática de produtividade de emails.

## 🔗 Links Relacionados

- [Streamlit App](https://huggingface.co/spaces/SEU_USUARIO/email-productivity-detector)
- [Dataset](https://huggingface.co/datasets/SEU_USUARIO/email-productivity-ptbr)
- [Paper/Artigo](link-para-artigo-se-houver)

---

*Este modelo foi criado para facilitar a gestão de emails e melhorar a produtividade no ambiente corporativo.*
