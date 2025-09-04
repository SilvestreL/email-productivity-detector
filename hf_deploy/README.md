# 📧 Email Productivity Classifier

## 🚀 Deploy no Hugging Face Spaces

Esta aplicação classifica emails como produtivos ou improdutivos usando um modelo DistilBERT fine-tuned.

## 🔧 Configuração Necessária

### 1. Upload dos Modelos no Google Drive

Faça upload dos seguintes arquivos para o Google Drive:
- `model.safetensors` (251MB)
- `config.json`
- `tokenizer.json`
- `vocab.txt`
- `special_tokens_map.json`
- `tokenizer_config.json`

### 2. Configure o Compartilhamento

- Clique com botão direito em cada arquivo
- Selecione "Compartilhar"
- Escolha "Qualquer pessoa com o link pode visualizar"

### 3. Obtenha os IDs

- Abra cada arquivo no Drive
- A URL será: `https://drive.google.com/file/d/ID_DO_ARQUIVO/view`
- Copie o `ID_DO_ARQUIVO`

### 4. Configure na Aplicação

Edite `drive_model_loader.py` e substitua os placeholders pelos IDs reais:

```python
DRIVE_FILES = {
    "model.safetensors": "SEU_ID_REAL_AQUI",
    "config.json": "SEU_ID_REAL_AQUI",
    "tokenizer.json": "SEU_ID_REAL_AQUI",
    "vocab.txt": "SEU_ID_REAL_AQUI",
    "special_tokens_map.json": "SEU_ID_REAL_AQUI",
    "tokenizer_config.json": "SEU_ID_REAL_AQUI"
}
```

## 📱 Como Usar

1. **Upload de arquivo:** Faça upload de um PDF ou TXT
2. **Digite texto:** Ou cole o texto diretamente
3. **Classifique:** Clique em "Classificar Email"
4. **Veja resultados:** Classificação, confiança e resposta sugerida

## 🎯 Funcionalidades

- ✅ Classificação automática de emails
- ✅ Upload de arquivos PDF e TXT
- ✅ Geração de respostas sugeridas
- ✅ Interface responsiva e profissional
- ✅ Modelos carregados do Google Drive

## 🚀 Deploy

Esta aplicação está configurada para rodar no Hugging Face Spaces com:
- **SDK:** Docker
- **Porta:** 8501
- **Dependências:** Python e sistema configuradas

## 📞 Suporte

Para problemas ou dúvidas:
- Email: lucassilvestreee@gmail.com
- GitHub: silvestrel/email-productivity-detector
