#!/usr/bin/env python3
"""
Script para fazer upload do modelo no Hugging Face Hub
"""

import os
from huggingface_hub import HfApi, create_repo

def upload_to_hub():
    """
    Faz upload do modelo para o Hugging Face Hub
    """
    
    # Configurar API
    api = HfApi()
    
    # Nome do repositório (troque pelo seu username)
    repo_name = "SEU_USUARIO/email-prod-improd-ptbr-bert"
    
    try:
        # Criar repositório (se não existir)
        create_repo(repo_name, exist_ok=True)
        print(f"✅ Repositório criado/verificado: {repo_name}")
        
        # Fazer upload dos arquivos
        print("📤 Fazendo upload dos arquivos...")
        
        # Lista de arquivos para upload
        files_to_upload = [
            "config.json",
            "model.safetensors", 
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "special_tokens_map.json",
            "README.md",
            "requirements.txt",
            "hf_config.json"
        ]
        
        for file_name in files_to_upload:
            file_path = os.path.join("../hub_ready_model", file_name)
            if os.path.exists(file_path):
                api.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=file_name,
                    repo_id=repo_name
                )
                print(f"✅ {file_name}")
            else:
                print(f"⚠️  {file_name} não encontrado")
        
        print(f"\n🎉 Modelo publicado com sucesso!")
        print(f"🌐 Acesse: https://huggingface.co/{repo_name}")
        
    except Exception as e:
        print(f"❌ Erro no upload: {e}")

if __name__ == "__main__":
    print("🚀 Fazendo upload para Hugging Face Hub...")
    upload_to_hub()
