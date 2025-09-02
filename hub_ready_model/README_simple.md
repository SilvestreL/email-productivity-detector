# Email Productivity Classifier (PT-BR)

Modelo BERT fine-tuned para classificação de emails em português brasileiro.

## 🎯 Objetivo

Classificar automaticamente emails como **Produtivo** (requer ação) ou **Improdutivo** (apenas informativo).

## 🚀 Uso Rápido

```python
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="SEU_USUARIO/email-prod-improd-ptbr-bert"
)

result = classifier("Preciso de uma reunião para discutir o projeto.")
print(result)
```

## 📊 Performance

- **Acurácia**: >85%
- **F1-Score**: >0.80
- **Tempo**: <100ms

## 🏷️ Labels

- **0**: Improdutivo
- **1**: Produtivo

## 📚 Mais Informações

Veja o [Model Card](README.md) para detalhes completos.

## 🤝 Contribuições

Contribuições são bem-vindas!
