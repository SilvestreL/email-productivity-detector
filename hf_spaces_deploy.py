#!/usr/bin/env python3
"""
Script para deploy direto no Hugging Face Spaces
SEM usar GitHub - resolve o problema dos arquivos pesados
"""

import os
import subprocess
import sys
from pathlib import Path


def check_docker():
    """Verifica se o Docker está funcionando"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker não está funcionando")
            return False
    except FileNotFoundError:
        print("❌ Docker não está instalado")
        return False


def check_hf_login():
    """Verifica se está logado no Hugging Face"""
    try:
        result = subprocess.run(
            ["docker", "login", "registry.hf.space"],
            capture_output=True,
            text=True,
            input="\n",
        )
        if result.returncode == 0:
            print("✅ Logado no Hugging Face Container Registry")
            return True
        else:
            print("❌ Falha no login do Hugging Face")
            return False
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False


def build_docker_image():
    """Faz o build da imagem Docker"""
    print("🔨 Fazendo build da imagem Docker...")

    try:
        # Remove imagens antigas se existirem
        subprocess.run(
            ["docker", "rmi", "email-classifier"],
            capture_output=True,
        )

        # Build da nova imagem
        result = subprocess.run(
            ["docker", "build", "-t", "email-classifier", "."],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Build da imagem concluído!")
            return True
        else:
            print(f"❌ Erro no build: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Erro durante build: {e}")
        return False


def deploy_to_hf():
    """Faz o deploy no Hugging Face Spaces"""

    username = "silvestrel"
    space_name = "EmailProductivityClassifier"

    print(f"🚀 Fazendo deploy para: {username}/{space_name}")

    try:
        # Tag da imagem
        print("🏷️  Fazendo tag da imagem...")
        subprocess.run(
            [
                "docker",
                "tag",
                "email-classifier",
                f"registry.hf.space/{username}/{space_name}:latest",
            ],
            check=True,
        )

        # Push para o registry
        print("📤 Fazendo push para o Hugging Face...")
        result = subprocess.run(
            ["docker", "push", f"registry.hf.space/{username}/{space_name}:latest"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Push concluído com sucesso!")
            return True
        else:
            print(f"❌ Erro no push: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Erro durante deploy: {e}")
        return False


def cleanup():
    """Limpa imagens Docker locais"""
    print("🧹 Limpando imagens locais...")

    try:
        subprocess.run(
            ["docker", "rmi", "email-classifier"],
            capture_output=True,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            [
                "docker",
                "rmi",
                f"registry.hf.space/silvestrel/EmailProductivityClassifier:latest",
            ],
            capture_output=True,
            stderr=subprocess.PIPE,
        )
        print("✅ Limpeza concluída!")
    except Exception as e:
        print(f"⚠️  Erro na limpeza: {e}")


def main():
    """Função principal"""
    print("🚀 Deploy Direto no Hugging Face Spaces")
    print("=" * 50)
    print("💡 Esta abordagem resolve o problema dos arquivos pesados!")
    print("   - Sem GitHub (sem limites de tamanho)")
    print("   - Deploy direto no HF Spaces")
    print("   - Modelos baixados do Google Drive")
    print()

    # Verificações
    if not check_docker():
        print("❌ Docker não está disponível. Instale e inicie o Docker.")
        return False

    if not check_hf_login():
        print("❌ Faça login no Hugging Face primeiro:")
        print("   docker login registry.hf.space")
        print("   Use seu token de acesso (Settings > Access Tokens)")
        return False

    # Deploy
    if not build_docker_image():
        print("❌ Falha no build da imagem")
        return False

    if not deploy_to_hf():
        print("❌ Falha no deploy")
        return False

    # Sucesso!
    print("\n🎉 Deploy concluído com sucesso!")
    print(
        f"🔗 Acesse: https://huggingface.co/spaces/silvestrel/EmailProductivityClassifier"
    )
    print("💡 O deploy pode levar alguns minutos para ficar disponível")

    # Limpeza
    cleanup()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
