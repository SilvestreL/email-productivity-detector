# Dockerfile para Email Productivity Classifier - AutoU
FROM python:3.10-slim

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p models data

# Treina o modelo (se não existir)
RUN python src/train.py

# Expõe a porta do Streamlit
EXPOSE 8501

# Define o comando para executar a aplicação (Streamlit por padrão)
# Para executar a API: CMD ["python", "src/api.py"]
CMD ["streamlit", "run", "src/app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
