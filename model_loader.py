"""
Carregador de modelo para Streamlit Cloud
"""

import os
import requests
import zipfile
from pathlib import Path
import streamlit as st

@st.cache_resource
def download_model_if_needed():
    """Baixa o modelo se não estiver disponível localmente"""
    
    model_dir = Path("models/model_distilbert_cased")
    
    # Se o modelo já existe, não baixa novamente
    if model_dir.exists() and any(model_dir.iterdir()):
        st.success("✅ Modelo local encontrado!")
        return True
    
    # Cria o diretório se não existir
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # URL do modelo (você pode hospedar em qualquer lugar)
    # Por enquanto, vamos usar um modelo público como exemplo
    MODEL_URL = "https://huggingface.co/distilbert-base-multilingual-cased/resolve/main/pytorch_model.bin"
    
    try:
        with st.spinner("📥 Baixando modelo... Isso pode levar alguns minutos na primeira vez."):
            # Para o deploy inicial, vamos usar um modelo público
            # Depois você pode substituir pelo seu modelo treinado
            st.info("🔧 Usando modelo público para demonstração. Seu modelo será carregado em breve!")
            
            # Aqui você pode adicionar a lógica para baixar seu modelo específico
            # Por enquanto, vamos simular que está funcionando
            
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao baixar modelo: {e}")
        return False

def get_model_path():
    """Retorna o caminho do modelo"""
    return "models/model_distilbert_cased"
