
# 📋 FLUXO DE TRABALHO - Email Productivity Detector

## 🎯 Objetivo
Classificar emails em português brasileiro como Produtivo ou Improdutivo usando modelo BERT fine-tuned.

## 📁 Estrutura do Projeto
```
email-productivity-detector/
├── models/
│   └── bert_prod_improd/          # Modelo BERT treinado
├── scripts/
│   ├── test_bert_model.py         # Testes do modelo
│   ├── update_app_local.py        # Atualiza app para modelo local
│   ├── prepare_for_hub.py         # Prepara para Hugging Face Hub
│   └── organize_workflow.py       # Este script
├── app.py                         # App Streamlit
└── requirements.txt               # Dependências
```

## 🚀 Fluxo de Trabalho

### 1. ✅ Modelo Treinado
- Modelo BERT fine-tuned em `models/bert_prod_improd/`
- Configurado para classificação binária (Produtivo/Improdutivo)
- Otimizado para português brasileiro

### 2. 🧪 Testes do Modelo
```bash
cd scripts
python test_bert_model.py
```
- Testa classificação com exemplos
- Mede performance e acurácia
- Gera relatório de resultados

### 3. 🔄 Integração no Streamlit
```bash
cd scripts
python update_app_local.py
```
- Atualiza app.py para usar modelo local
- Cria backup do arquivo original
- Configura caminhos corretos

### 4. 🚀 Teste do App
```bash
streamlit run app.py
```
- Interface web para classificação
- Upload de arquivos (.txt, .pdf)
- Respostas automáticas sugeridas

### 5. 🌐 Publicação no Hub
```bash
cd scripts
python prepare_for_hub.py
cd ../hub_ready_model
python upload_to_hub.py
```
- Prepara arquivos para Hub
- Cria model card e documentação
- Script de upload automático

## 📊 Métricas Esperadas
- **Acurácia**: >85%
- **F1-Score**: >0.80
- **Tempo de Inferência**: <100ms
- **Suporte**: Textos até 512 tokens

## 🔧 Dependências
- torch >= 1.9.0
- transformers >= 4.20.0
- streamlit
- nltk
- huggingface_hub (para publicação)

## 🎯 Próximos Passos
1. ✅ Modelo treinado e testado
2. 🔄 App integrado e funcionando
3. 🌐 Publicar no Hugging Face Hub
4. 📊 Monitorar performance em produção
5. 🔄 Iterar e melhorar

## 💡 Dicas
- Sempre teste o modelo antes de publicar
- Mantenha backup dos arquivos originais
- Documente mudanças e melhorias
- Monitore métricas de performance
