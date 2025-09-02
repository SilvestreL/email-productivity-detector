#!/usr/bin/env python3
"""
Script para configurar corretamente o modelo no Hugging Face Hub
"""

from huggingface_hub import HfApi, create_repo, upload_file
import os
import json


def setup_model_on_hub():
    """
    Configura o modelo corretamente no Hugging Face Hub
    """

    # Configurar API
    api = HfApi()

    # Nome do repositório (troque pelo seu username)
    repo_name = "SEU_USUARIO/email-prod-improd-ptbr-bert"

    try:
        # Criar repositório (se não existir)
        create_repo(repo_name, exist_ok=True, private=False, repo_type="model")
        print(f"✅ Repositório criado/verificado: {repo_name}")

        # Configurar metadados do repositório
        repo_metadata = {
            "tags": [
                "text-classification",
                "productivity",
                "email",
                "portuguese",
                "bert",
                "pt-br",
                "email-classification",
                "productivity-classifier",
                "fine-tuned",
            ],
            "language": "pt-BR",
            "license": "mit",
            "library_name": "transformers",
            "pipeline_tag": "text-classification",
        }

        # Fazer upload dos arquivos principais
        print("📤 Fazendo upload dos arquivos principais...")

        files_to_upload = [
            "config.json",
            "model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "special_tokens_map.json",
        ]

        for file_name in files_to_upload:
            file_path = file_name
            if os.path.exists(file_path):
                api.upload_file(
                    path_or_fileobj=file_path, path_in_repo=file_name, repo_id=repo_name
                )
                print(f"✅ {file_name}")
            else:
                print(f"⚠️  {file_name} não encontrado")

        # Fazer upload da documentação
        print("\n📝 Fazendo upload da documentação...")

        doc_files = ["README.md", "requirements.txt"]

        for file_name in doc_files:
            file_path = file_name
            if os.path.exists(file_path):
                api.upload_file(
                    path_or_fileobj=file_path, path_in_repo=file_name, repo_id=repo_name
                )
                print(f"✅ {file_name}")
            else:
                print(f"⚠️  {file_name} não encontrado")

        # Configurar metadados específicos do modelo
        print("\n🔧 Configurando metadados do modelo...")

        # Criar arquivo de configuração específico do Hub
        hub_config = {
            "model_type": "bert",
            "task": "text-classification",
            "pipeline_tag": "text-classification",
            "library_name": "transformers",
            "tags": [
                "text-classification",
                "productivity",
                "email",
                "portuguese",
                "bert",
                "pt-br",
                "email-classification",
                "productivity-classifier",
                "fine-tuned",
            ],
            "language": "pt-BR",
            "license": "mit",
            "datasets": ["custom"],
            "metrics": ["accuracy", "f1", "precision", "recall"],
        }

        # Salvar configuração do Hub
        with open("hub_config.json", "w", encoding="utf-8") as f:
            json.dump(hub_config, f, indent=2, ensure_ascii=False)

        # Fazer upload da configuração do Hub
        api.upload_file(
            path_or_fileobj="hub_config.json",
            path_in_repo="hub_config.json",
            repo_id=repo_name,
        )
        print("✅ hub_config.json")

        print(f"\n🎉 Modelo configurado com sucesso no Hugging Face Hub!")
        print(f"🌐 Acesse: https://huggingface.co/{repo_name}")
        print(f"🏷️  Categoria: Text Classification")
        print(f"🌍 Idioma: Português Brasileiro (pt-BR)")
        print(f"📊 Task: text-classification")

        # Verificar se o modelo aparece na categoria correta
        print(f"\n🔍 Para verificar a categorização:")
        print(f"   1. Acesse: https://huggingface.co/models?search=text-classification")
        print(f"   2. Procure por: email-prod-improd-ptbr-bert")
        print(f"   3. Verifique se aparece em: Text Classification")

    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Configurando Modelo no Hugging Face Hub")
    print("=" * 60)
    setup_model_on_hub()
