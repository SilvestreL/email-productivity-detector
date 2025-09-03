#!/usr/bin/env python3
"""
Script para fazer deploy direto no Hugging Face Spaces
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Executa um comando e trata erros"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído!")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}: {e}")
        print(f"Stderr: {e.stderr}")
        return None

def check_git_lfs():
    """Verifica se o Git LFS está instalado"""
    try:
        subprocess.run(["git", "lfs", "version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_git_lfs():
    """Configura o Git LFS para arquivos grandes"""
    if not check_git_lfs():
        print("📦 Instalando Git LFS...")
        if sys.platform == "darwin":  # macOS
            run_command("brew install git-lfs", "Instalando Git LFS via Homebrew")
        elif sys.platform.startswith("linux"):
            run_command("sudo apt-get install git-lfs", "Instalando Git LFS via apt")
        else:
            print("❌ Sistema operacional não suportado para instalação automática do Git LFS")
            print("💡 Instale manualmente: https://git-lfs.com/")
            return False
    
    # Inicializa Git LFS
    run_command("git lfs install", "Inicializando Git LFS")
    
    # Configura arquivos para rastrear
    lfs_files = [
        "*.safetensors",
        "*.bin",
        "*.pt",
        "*.pth",
        "*.json",
        "*.txt"
    ]
    
    for pattern in lfs_files:
        run_command(f"git lfs track '{pattern}'", f"Configurando rastreamento para {pattern}")
    
    return True

def deploy_to_hf():
    """Faz o deploy no Hugging Face Spaces"""
    
    print("🚀 Iniciando deploy no Hugging Face Spaces...")
    
    # Verifica se está no diretório correto
    if not Path("app.py").exists():
        print("❌ Execute este script no diretório raiz do projeto")
        return False
    
    # Verifica se o Docker está rodando
    if run_command("docker info", "Verificando Docker") is None:
        print("❌ Docker não está rodando. Inicie o Docker e tente novamente.")
        return False
    
    # Verifica se está logado no Hugging Face
    if run_command("docker login registry.hf.space", "Verificando login no HF") is None:
        print("❌ Faça login no Hugging Face Container Registry primeiro:")
        print("   docker login registry.hf.space")
        print("   Use seu token de acesso do HF (Settings > Access Tokens)")
        return False
    
    # Build da imagem
    if run_command("docker build -t email-classifier .", "Fazendo build da imagem") is None:
        return False
    
    # Tag da imagem
    username = "silvestrel"  # Seu username do HF
    space_name = "EmailProductivityClassifier"
    
    run_command(f"docker tag email-classifier registry.hf.space/{username}/{space_name}:latest", 
                "Tagging da imagem")
    
    # Push para o registry
    if run_command(f"docker push registry.hf.space/{username}/{space_name}:latest", 
                   "Fazendo push para o HF") is None:
        return False
    
    # Limpeza
    run_command("docker rmi email-classifier", "Limpando imagens locais")
    run_command(f"docker rmi registry.hf.space/{username}/{space_name}:latest", 
                "Limpando tags locais")
    
    print("🎉 Deploy concluído com sucesso!")
    print(f"🔗 Acesse: https://huggingface.co/spaces/{username}/{space_name}")
    print("💡 O deploy pode levar alguns minutos para ficar disponível")
    
    return True

def main():
    """Função principal"""
    print("📧 Email Productivity Classifier - Deploy no HF Spaces")
    print("=" * 60)
    
    # Opção 1: Deploy direto (recomendado)
    print("\n🚀 Opção 1: Deploy Direto no HF (Recomendado)")
    print("   - Não precisa fazer push do modelo para o GitHub")
    print("   - Modelo é baixado durante o build do Docker")
    print("   - Mais rápido e eficiente")
    
    # Opção 2: Deploy com Git LFS
    print("\n📦 Opção 2: Deploy com Git LFS")
    print("   - Usa Git LFS para arquivos grandes")
    print("   - Modelo fica no repositório")
    print("   - Pode ser mais lento")
    
    choice = input("\nEscolha uma opção (1 ou 2): ").strip()
    
    if choice == "1":
        return deploy_to_hf()
    elif choice == "2":
        if setup_git_lfs():
            print("\n✅ Git LFS configurado!")
            print("💡 Agora você pode fazer push normal para o GitHub")
            print("   git add .")
            print("   git commit -m 'Deploy com Git LFS'")
            print("   git push origin main")
        else:
            print("❌ Falha ao configurar Git LFS")
            return False
    else:
        print("❌ Opção inválida")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
