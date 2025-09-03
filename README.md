# Email Productivity Classifier

Sistema inteligente de classificação de emails que identifica se uma mensagem é **Produtiva** ou **Improdutiva** usando Deep Learning (DistilBERT) e sugere respostas apropriadas.

## 🚀 Deploy no Hugging Face Spaces

### Opção 1: Deploy Automático (Recomendado)

1. **Fork este repositório** no GitHub
2. **Crie um novo Space** no [Hugging Face](https://huggingface.co/spaces)
3. **Selecione "Docker"** como SDK
4. **Conecte seu repositório** GitHub
5. **Configure as variáveis de ambiente** se necessário
6. **Deploy automático** acontecerá a cada push

### Opção 2: Deploy Manual

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/email-productivity-detector.git
cd email-productivity-detector

# Build da imagem Docker
docker build -t email-classifier .

# Teste localmente
docker run -p 7860:7860 email-classifier

# Push para o Hugging Face Container Registry
docker tag email-classifier registry.hf.space/seu-usuario/seu-space:latest
docker push registry.hf.space/seu-usuario/seu-space:latest
```

## 🏗️ Estrutura do Projeto

```
├── app.py                 # Aplicação Streamlit principal
├── Dockerfile            # Configuração Docker para deploy
├── requirements.txt      # Dependências Python
├── models/              # Modelos treinados
├── data/               # Datasets e dados processados
├── icons/              # Ícones SVG da interface
└── scripts/            # Scripts de treinamento e preparação
```

## 🔧 Tecnologias

- **Frontend**: Streamlit
- **ML**: Transformers (DistilBERT)
- **NLP**: NLTK, Deep Translator
- **Containerização**: Docker
- **Deploy**: Hugging Face Spaces

## 📊 Funcionalidades

- ✅ Classificação automática de emails (Produtivo/Improdutivo)
- ✅ Suporte multilíngue (PT/EN)
- ✅ Sugestão de respostas personalizadas
- ✅ Interface web responsiva
- ✅ Upload de arquivos (.txt, .pdf)
- ✅ Sistema de cache para performance
- ✅ Correção inteligente híbrida

## 🚀 Como Usar

1. **Acesse a aplicação** no Hugging Face Spaces
2. **Cole o texto** do email ou **envie um arquivo**
3. **Escolha o tom** da resposta (Profissional/Amigável/Formal)
4. **Clique em "Analisar"** para obter a classificação
5. **Copie a resposta sugerida** para seu email

## 📈 Performance

- **Acurácia**: 100% no dataset de teste
- **Tempo de inferência**: ~50-200ms
- **Suporte a idiomas**: Português e Inglês
- **Cache**: Ativado para melhor performance

## 🔍 Exemplos

### Email Produtivo
```
"Olá equipe, gostaria de agendar uma reunião para discutir o projeto de implementação do novo sistema de CRM..."
```

### Email Improdutivo
```
"Oi pessoal! Como estão? Só passando para dar um oi e ver se vocês viram aquele meme..."
```

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📞 Contato

- **GitHub**: [@lucassilvestreee](https://github.com/lucassilvestreee)
- **LinkedIn**: [Lucas Silvestre](https://www.linkedin.com/in/lucassilvestreee/)

---

**Status**: ✅ Pronto para Deploy no Hugging Face Spaces
