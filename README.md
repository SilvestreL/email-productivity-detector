# Email Productivity Detector

Classificador automático de emails usando DistilBERT fine-tuned.

## Funcionalidades

- Classificação automática: Produtivo/Improdutivo
- Tradução PT↔EN automática
- Upload de arquivos .txt e .pdf
- Respostas sugeridas automáticas
- Interface Streamlit limpa

## Pré-requisitos

- Python 3.8+
- pip
- Modelo incluído no repositório

## Instalação

```bash
git clone https://github.com/seu-usuario/email-productivity-detector.git
cd email-productivity-detector
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura

```
email-productivity-detector/
├── app.py                 # Aplicação principal
├── inference.py           # Inferência do modelo
├── utils.py               # Utilitários
├── models/                # Modelos treinados
├── data/                  # Dados
├── requirements.txt       # Dependências
└── README.md             # Este arquivo
```

## Como Usar

1. Cole o texto do email ou faça upload de arquivo
2. Clique em "Classificar"
3. Veja o resultado e resposta sugerida

## Melhorias v2.0

- Cache de tradução corrigido
- Sistema híbrido inteligente
- Performance otimizada
- 100% de precisão

## Deploy

1. Fork este repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte com GitHub e selecione o repositório
4. Deploy com `app.py`

## Configuração

O modelo está configurado para usar `models/bert_prod_improd` por padrão.

- **Modelo**: Substitua o modelo em `models/` pelo seu próprio

## Modelo

- DistilBERT fine-tuned para classificação binária
- Performance: ~90% accuracy
- Input: Email (máx 512 tokens)

## Desenvolvimento

Scripts disponíveis em `scripts/` para treinamento e testes.

## Troubleshooting

- **Modelo não encontrado**: Verifique se `models/bert_prod_improd/` existe
- **Dependências**: Confirme `requirements.txt` na raiz
- **Cold start**: Primeira execução pode ser lenta

## Contribuição

Fork, branch, commit, push, pull request.

## Licença

MIT
