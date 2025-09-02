# Makefile para Email Productivity Classifier
# Comandos: make prepare, make train, make run

.PHONY: help prepare train run install install-train clean test

# Variáveis
PYTHON := python3
PIP := pip3
VENV := venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

# Cores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(GREEN)Email Productivity Classifier - Comandos disponíveis:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Exemplos:$(NC)"
	@echo "  make prepare    # Prepara o dataset"
	@echo "  make train      # Treina o modelo"
	@echo "  make run        # Executa a aplicação"
	@echo "  make install    # Instala dependências da aplicação"
	@echo "  make install-train # Instala dependências de treinamento"

install: ## Instala dependências da aplicação
	@echo "$(GREEN)📦 Instalando dependências da aplicação...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependências da aplicação instaladas!$(NC)"

install-train: ## Instala dependências de treinamento
	@echo "$(GREEN)📦 Instalando dependências de treinamento...$(NC)"
	$(PIP) install -r requirements-train.txt
	@echo "$(GREEN)✅ Dependências de treinamento instaladas!$(NC)"

install-venv: ## Cria ambiente virtual e instala dependências
	@echo "$(GREEN)🐍 Criando ambiente virtual...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)📦 Instalando dependências...$(NC)"
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install -r requirements-train.txt
	@echo "$(GREEN)✅ Ambiente virtual criado e dependências instaladas!$(NC)"
	@echo "$(YELLOW)💡 Para ativar: source $(VENV)/bin/activate$(NC)"

prepare: ## Prepara o dataset para treinamento
	@echo "$(GREEN)🔄 Preparando dataset...$(NC)"
	$(PYTHON) scripts/prepare_dataset.py
	@echo "$(GREEN)✅ Dataset preparado!$(NC)"

train: ## Treina o modelo
	@echo "$(GREEN)🤖 Treinando modelo...$(NC)"
	$(PYTHON) scripts/train.py
	@echo "$(GREEN)✅ Modelo treinado!$(NC)"

run: ## Executa a aplicação Streamlit
	@echo "$(GREEN)🚀 Iniciando aplicação...$(NC)"
	@echo "$(YELLOW)💡 Acesse: http://localhost:8501$(NC)"
	streamlit run app.py

run-venv: ## Executa a aplicação no ambiente virtual
	@echo "$(GREEN)🚀 Iniciando aplicação no ambiente virtual...$(NC)"
	@echo "$(YELLOW)💡 Acesse: http://localhost:8501$(NC)"
	$(VENV_BIN)/streamlit run app.py

test: ## Testa a aplicação com amostras
	@echo "$(GREEN)🧪 Testando aplicação...$(NC)"
	@echo "$(YELLOW)💡 Execute manualmente: streamlit run app.py$(NC)"
	@echo "$(YELLOW)💡 Teste com emails produtivos e improdutivos$(NC)"

clean: ## Limpa arquivos temporários
	@echo "$(GREEN)🧹 Limpando arquivos temporários...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

clean-models: ## Remove modelos treinados
	@echo "$(GREEN)🧹 Removendo modelos treinados...$(NC)"
	rm -rf models/
	rm -rf data/processed/
	@echo "$(GREEN)✅ Modelos removidos!$(NC)"

clean-all: clean clean-models ## Remove tudo (modelos + arquivos temporários)
	@echo "$(GREEN)🧹 Limpeza completa!$(NC)"

setup: install-venv prepare ## Setup completo (ambiente + dataset)
	@echo "$(GREEN)✅ Setup completo!$(NC)"
	@echo "$(YELLOW)💡 Próximos passos:$(NC)"
	@echo "  1. make train    # Treinar modelo"
	@echo "  2. make run      # Executar aplicação"

full-pipeline: prepare train ## Pipeline completo (dataset + treinamento)
	@echo "$(GREEN)✅ Pipeline completo executado!$(NC)"
	@echo "$(YELLOW)💡 Próximo passo: make run$(NC)"

# Comandos de desenvolvimento
dev-install: ## Instala dependências de desenvolvimento
	@echo "$(GREEN)📦 Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-train.txt
	$(PIP) install black flake8 pytest
	@echo "$(GREEN)✅ Dependências de desenvolvimento instaladas!$(NC)"

format: ## Formata código com black
	@echo "$(GREEN)🎨 Formatando código...$(NC)"
	black *.py scripts/*.py
	@echo "$(GREEN)✅ Código formatado!$(NC)"

lint: ## Verifica código com flake8
	@echo "$(GREEN)🔍 Verificando código...$(NC)"
	flake8 *.py scripts/*.py --max-line-length=100 --ignore=E203,W503
	@echo "$(GREEN)✅ Verificação concluída!$(NC)"

# Comandos de deploy
check-model: ## Verifica se o modelo está configurado
	@echo "$(GREEN)🔍 Verificando configuração do modelo...$(NC)"
	@grep -n "MODEL_ID" app.py || echo "$(RED)❌ MODEL_ID não encontrado em app.py$(NC)"
	@grep -n "SEU_USUARIO" app.py && echo "$(YELLOW)⚠️  Configure seu MODEL_ID no app.py$(NC)" || echo "$(GREEN)✅ MODEL_ID configurado$(NC)"

deploy-check: check-model ## Verifica se está pronto para deploy
	@echo "$(GREEN)🚀 Verificando preparação para deploy...$(NC)"
	@test -f app.py && echo "$(GREEN)✅ app.py encontrado$(NC)" || echo "$(RED)❌ app.py não encontrado$(NC)"
	@test -f requirements.txt && echo "$(GREEN)✅ requirements.txt encontrado$(NC)" || echo "$(RED)❌ requirements.txt não encontrado$(NC)"
	@test -f README.md && echo "$(GREEN)✅ README.md encontrado$(NC)" || echo "$(RED)❌ README.md não encontrado$(NC)"
	@echo "$(GREEN)✅ Verificação de deploy concluída!$(NC)"

# Comandos de informações
info: ## Mostra informações do projeto
	@echo "$(GREEN)📋 Informações do projeto:$(NC)"
	@echo "  Nome: Email Productivity Classifier"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Pip: $(shell $(PIP) --version)"
	@echo "  Diretório: $(shell pwd)"
	@echo "  Arquivos Python: $(shell find . -name '*.py' | wc -l)"
	@echo "  Tamanho do projeto: $(shell du -sh . | cut -f1)"

# Comando padrão
.DEFAULT_GOAL := help
