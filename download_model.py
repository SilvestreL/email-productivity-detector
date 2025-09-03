#!/usr/bin/env python3
"""
Script para baixar o modelo treinado durante o build do Docker
"""

import os
import requests
import zipfile
from pathlib import Path

def download_model():
    """Baixa o modelo treinado do Hugging Face Hub"""
    
    # URL do modelo (você pode hospedar o modelo no HF Hub)
    MODEL_URL = "https://huggingface.co/silvestrel/email-productivity-classifier/resolve/main/model.zip"
    
    # Diretório de destino
    MODEL_DIR = Path("models/model_distilbert_cased")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Baixando modelo de: {MODEL_URL}")
    
    try:
        # Download do modelo
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()
        
        # Salva o arquivo zip
        zip_path = "model.zip"
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extrai o modelo
        print("📦 Extraindo modelo...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(MODEL_DIR)
        
        # Remove o arquivo zip
        os.remove(zip_path)
        
        print("✅ Modelo baixado e extraído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao baixar modelo: {e}")
        print("💡 Usando modelo local se disponível...")
        
        # Se falhar, verifica se há modelo local
        if MODEL_DIR.exists() and any(MODEL_DIR.iterdir()):
            print("✅ Modelo local encontrado!")
        else:
            print("⚠️  Nenhum modelo encontrado. A aplicação pode não funcionar.")

if __name__ == "__main__":
    download_model()
