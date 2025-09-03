"""
Carregador de modelo do Google Drive para Hugging Face Spaces
"""

import os
import requests
import zipfile
from pathlib import Path
import streamlit as st
import time

def download_from_drive(file_id, output_path):
    """
    Baixa arquivo do Google Drive usando o ID do arquivo
    
    Args:
        file_id: ID do arquivo no Google Drive
        output_path: Caminho onde salvar o arquivo
    """
    
    # URL para download direto do Google Drive
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    
    try:
        # Faz o download
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Salva o arquivo
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao baixar do Drive: {e}")
        return False

@st.cache_resource
def load_model_from_drive():
    """
    Carrega o modelo treinado do Google Drive
    """
    
    # IDs dos arquivos no Google Drive (você precisa configurar)
    DRIVE_FILES = {
        "model.safetensors": "SEU_FILE_ID_MODEL",  # Substitua pelo ID real
        "config.json": "SEU_FILE_ID_CONFIG",       # Substitua pelo ID real
        "tokenizer.json": "SEU_FILE_ID_TOKENIZER", # Substitua pelo ID real
        "vocab.txt": "SEU_FILE_ID_VOCAB",         # Substitua pelo ID real
        "special_tokens_map.json": "SEU_FILE_ID_SPECIAL", # Substitua pelo ID real
        "tokenizer_config.json": "SEU_FILE_ID_TOKENIZER_CONFIG" # Substitua pelo ID real
    }
    
    model_dir = Path("models/model_distilbert_cased")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Verifica se o modelo já existe
    if model_dir.exists() and any(model_dir.iterdir()):
        st.success("✅ Modelo já carregado!")
        return str(model_dir)
    
    # Baixa cada arquivo do Drive
    with st.spinner("📥 Baixando modelo do Google Drive... Isso pode levar alguns minutos na primeira vez."):
        
        for filename, file_id in DRIVE_FILES.items():
            if file_id == "SEU_FILE_ID_MODEL":  # Placeholder
                st.warning(f"⚠️ Configure o ID do arquivo {filename} no Google Drive")
                continue
                
            file_path = model_dir / filename
            st.info(f"📥 Baixando {filename}...")
            
            if download_from_drive(file_id, file_path):
                st.success(f"✅ {filename} baixado!")
            else:
                st.error(f"❌ Falha ao baixar {filename}")
                return None
            
            # Pequena pausa para não sobrecarregar
            time.sleep(1)
    
    st.success("🎉 Modelo carregado com sucesso do Google Drive!")
    return str(model_dir)

def get_model_path():
    """Retorna o caminho do modelo"""
    return load_model_from_drive()

# Função para configurar os IDs do Drive
def setup_drive_ids():
    """
    Interface para configurar os IDs dos arquivos do Google Drive
    """
    st.sidebar.markdown("### 🔧 Configuração do Google Drive")
    
    st.info("""
    **Para usar esta aplicação:**
    
    1. Faça upload dos arquivos do modelo para o Google Drive
    2. Compartilhe os arquivos como "Qualquer pessoa com o link pode visualizar"
    3. Copie o ID de cada arquivo da URL
    4. Configure os IDs abaixo
    """)
    
    # Exemplo de como obter o ID do Drive
    st.markdown("""
    **Como obter o ID do arquivo:**
    
    URL: `https://drive.google.com/file/d/1ABC123...XYZ/view`
    ID: `1ABC123...XYZ`
    """)
    
    # Campos para configurar os IDs
    model_id = st.text_input("ID do model.safetensors", value="")
    config_id = st.text_input("ID do config.json", value="")
    tokenizer_id = st.text_input("ID do tokenizer.json", value="")
    vocab_id = st.text_input("ID do vocab.txt", value="")
    
    if st.button("💾 Salvar IDs"):
        # Aqui você pode salvar em um arquivo de configuração
        st.success("IDs salvos! Reinicie a aplicação para aplicar as mudanças.")
