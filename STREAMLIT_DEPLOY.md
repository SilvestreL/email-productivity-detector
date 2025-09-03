# 🚀 Deploy no Streamlit Cloud

## 📋 Passos para Deploy

### 1. **Preparar o Repositório**

✅ **Arquivos já configurados:**
- `app.py` - Aplicação principal
- `requirements.txt` - Dependências Python
- `packages.txt` - Dependências do sistema
- `.streamlit/config.toml` - Configuração do Streamlit
- `.streamlit/secrets.toml` - Configurações locais

### 2. **Fazer Push para o GitHub**

```bash
# Adicionar todas as mudanças
git add .

# Fazer commit
git commit -m "Configurando para Streamlit Cloud"

# Fazer push (sem os modelos pesados)
git push origin main
```

### 3. **Deploy no Streamlit Cloud**

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta GitHub
3. Clique em **"New app"**
4. Configure:
   - **Repository**: `silvestrel/email-productivity-detector`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Clique em **"Deploy!"**

### 4. **Configurar Variáveis de Ambiente (Opcional)**

No Streamlit Cloud, você pode configurar:
- `MODEL_PATH`: Caminho para o modelo
- `MAX_FILE_SIZE`: Tamanho máximo de arquivo

## 🔧 Configurações Atuais

### Dependências Python
- Streamlit >= 1.28.0
- Transformers >= 4.35.0
- PyTorch >= 2.0.0
- Outras bibliotecas de ML

### Dependências do Sistema
- gcc
- g++

### Configurações do Streamlit
- Porta: 8501
- Modo headless: true
- CORS: false
- XSRF: false

## 📁 Estrutura do Projeto

```
email-productivity-detector/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências Python
├── packages.txt          # Dependências do sistema
├── .streamlit/
│   ├── config.toml      # Configuração do Streamlit
│   └── secrets.toml     # Configurações locais
├── model_loader.py       # Carregador de modelo
└── README.md
```

## 🎯 Vantagens do Streamlit Cloud

✅ **Simples**: Apenas push para GitHub
✅ **Rápido**: Deploy automático
✅ **Gratuito**: Para projetos públicos
✅ **Escalável**: Suporte a milhares de usuários
✅ **Sem Docker**: Não precisa configurar containers

## 🚨 Limitações

⚠️ **Arquivos grandes**: Máximo 100MB por arquivo
⚠️ **Tempo de build**: Pode levar alguns minutos
⚠️ **Recursos**: Limitados na versão gratuita

## 🔄 Atualizações

Para atualizar a aplicação:
1. Faça as mudanças no código
2. Commit e push para GitHub
3. O Streamlit Cloud faz deploy automático

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no Streamlit Cloud
2. Consulte a documentação oficial
3. Abra uma issue no repositório

---

**Status**: ✅ Configurado para Streamlit Cloud
**Próximo passo**: Fazer push para GitHub e deploy!
