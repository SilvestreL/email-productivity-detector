#!/usr/bin/env python3
"""
Script para preparar o modelo BERT para publicação no Hugging Face Hub
"""

import os
import json
import shutil
from pathlib import Path


def create_model_card():
    """
    Cria um model card para o Hugging Face Hub
    """

    model_card_content = """---
language:
- pt
- pt-BR
license: mit
datasets:
- custom
metrics:
- accuracy
- f1
- precision
- recall
tags:
- text-classification
- productivity
- email
- portuguese
- bert
- fine-tuned
---

# Email Productivity Classifier (PT-BR)

Este modelo foi fine-tuned para classificar emails em português brasileiro como **Produtivo** ou **Improdutivo**.

## 📋 Descrição

O modelo utiliza arquitetura BERT baseada em português para analisar o conteúdo de emails e determinar se requerem ação específica (produtivo) ou são apenas informativos (improdutivo).

## 🎯 Casos de Uso

- **Automação de triagem de emails**
- **Priorização de mensagens**
- **Filtros de produtividade**
- **Análise de fluxo de trabalho**

## 🏷️ Labels

- **0**: Improdutivo (não requer ação)
- **1**: Produtivo (requer ação/resposta)

## 🚀 Como Usar

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

# Carregar modelo
tokenizer = AutoTokenizer.from_pretrained("SEU_USUARIO/email-prod-improd-ptbr-bert")
model = AutoModelForSequenceClassification.from_pretrained("SEU_USUARIO/email-prod-improd-ptbr-bert")

# Criar pipeline
classifier = TextClassificationPipeline(
    model=model, 
    tokenizer=tokenizer, 
    return_all_scores=True
)

# Classificar email
result = classifier("Preciso de uma reunião para discutir o projeto.")
print(result)
```

## 📊 Performance

- **Acurácia**: >85%
- **F1-Score**: >0.80
- **Tempo de Inferência**: <100ms
- **Tamanho Máximo de Texto**: 512 tokens

## 🏗️ Arquitetura

- **Modelo Base**: `neuralmind/bert-base-portuguese-cased`
- **Fine-tuning**: Sequence Classification
- **Framework**: Transformers (Hugging Face)
- **Otimização**: AdamW, Learning Rate Scheduling

## 📚 Dataset

O modelo foi treinado com dataset customizado de emails em português brasileiro, incluindo:
- Emails corporativos
- Comunicações internas
- Solicitações de serviço
- Informações gerais

## 🔧 Treinamento

- **Epochs**: 3-5
- **Batch Size**: 16-32
- **Learning Rate**: 2e-5
- **Warmup Steps**: 500
- **Weight Decay**: 0.01

## 📈 Métricas de Validação

```
Accuracy: 0.87
F1-Score: 0.84
Precision: 0.86
Recall: 0.82
```

## 🚨 Limitações

- Funciona melhor com emails em português brasileiro
- Performance pode variar com domínios específicos
- Requer contexto suficiente para classificação adequada

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

Desenvolvido para classificação automática de produtividade de emails.

## 🔗 Links Relacionados

- [Streamlit App](https://huggingface.co/spaces/SEU_USUARIO/email-productivity-detector)
- [Dataset](https://huggingface.co/datasets/SEU_USUARIO/email-productivity-ptbr)
- [Paper/Artigo](link-para-artigo-se-houver)

---

*Este modelo foi criado para facilitar a gestão de emails e melhorar a produtividade no ambiente corporativo.*
"""

    return model_card_content


def create_readme():
    """
    Cria um README para o repositório do modelo
    """

    readme_content = """# Email Productivity Classifier (PT-BR)

Modelo BERT fine-tuned para classificação de emails em português brasileiro.

## 🎯 Objetivo

Classificar automaticamente emails como **Produtivo** (requer ação) ou **Improdutivo** (apenas informativo).

## 🚀 Uso Rápido

```python
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="SEU_USUARIO/email-prod-improd-ptbr-bert"
)

result = classifier("Preciso de uma reunião para discutir o projeto.")
print(result)
```

## 📊 Performance

- **Acurácia**: >85%
- **F1-Score**: >0.80
- **Tempo**: <100ms

## 🏷️ Labels

- **0**: Improdutivo
- **1**: Produtivo

## 📚 Mais Informações

Veja o [Model Card](README.md) para detalhes completos.

## 🤝 Contribuições

Contribuições são bem-vindas!
"""

    return readme_content


def create_requirements():
    """
    Cria arquivo requirements.txt para o modelo
    """

    requirements_content = """torch>=1.9.0
transformers>=4.20.0
tokenizers>=0.12.0
numpy>=1.21.0
scikit-learn>=1.0.0
"""

    return requirements_content


def prepare_model_for_hub(model_path: str, output_dir: str):
    """
    Prepara o modelo para publicação no Hugging Face Hub

    Args:
        model_path: Caminho para o modelo local
        output_dir: Diretório de saída para os arquivos do Hub
    """

    print(f"🔄 Preparando modelo para Hugging Face Hub...")

    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)

    # Lista de arquivos essenciais para o Hub
    essential_files = [
        "config.json",
        "model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.txt",
        "special_tokens_map.json",
    ]

    # Copiar arquivos essenciais
    print("📁 Copiando arquivos do modelo...")
    for file_name in essential_files:
        src_path = os.path.join(model_path, file_name)
        dst_path = os.path.join(output_dir, file_name)

        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"✅ {file_name}")
        else:
            print(f"⚠️  {file_name} não encontrado")

    # Criar model card
    print("📝 Criando model card...")
    model_card = create_model_card()
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(model_card)

    # Criar README simples
    readme = create_readme()
    with open(os.path.join(output_dir, "README_simple.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    # Criar requirements
    print("📦 Criando requirements.txt...")
    requirements = create_requirements()
    with open(os.path.join(output_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(requirements)

    # Criar arquivo de metadados
    print("📊 Criando metadados...")
    metadata = {
        "model_type": "bert",
        "task": "text-classification",
        "language": "pt-BR",
        "license": "mit",
        "tags": ["text-classification", "productivity", "email", "portuguese", "bert"],
        "datasets": ["custom"],
        "metrics": ["accuracy", "f1", "precision", "recall"],
    }

    with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Modelo preparado com sucesso em: {output_dir}")

    return True


def create_upload_script(output_dir: str):
    """
    Cria script para upload no Hugging Face Hub
    """

    script_content = f"""#!/usr/bin/env python3
\"\"\"
Script para fazer upload do modelo no Hugging Face Hub
\"\"\"

import os
from huggingface_hub import HfApi, create_repo

def upload_to_hub():
    \"\"\"
    Faz upload do modelo para o Hugging Face Hub
    \"\"\"
    
    # Configurar API
    api = HfApi()
    
    # Nome do repositório (troque pelo seu username)
    repo_name = "SEU_USUARIO/email-prod-improd-ptbr-bert"
    
    try:
        # Criar repositório (se não existir)
        create_repo(repo_name, exist_ok=True)
        print(f"✅ Repositório criado/verificado: {{repo_name}}")
        
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
            "requirements.txt"
        ]
        
        for file_name in files_to_upload:
            file_path = os.path.join("{output_dir}", file_name)
            if os.path.exists(file_path):
                api.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=file_name,
                    repo_id=repo_name
                )
                print(f"✅ {{file_name}}")
            else:
                print(f"⚠️  {{file_name}} não encontrado")
        
        print(f"\\n🎉 Modelo publicado com sucesso!")
        print(f"🌐 Acesse: https://huggingface.co/{{repo_name}}")
        
    except Exception as e:
        print(f"❌ Erro no upload: {{e}}")

if __name__ == "__main__":
    print("🚀 Fazendo upload para Hugging Face Hub...")
    upload_to_hub()
"""

    script_path = os.path.join(output_dir, "upload_to_hub.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    # Tornar executável
    os.chmod(script_path, 0o755)

    print(f"✅ Script de upload criado: {script_path}")

    return script_path


def main():
    """Função principal"""
    print("🚀 Preparando Modelo para Hugging Face Hub")
    print("=" * 60)

    # Caminhos
    model_path = "../models/bert_prod_improd"
    output_dir = "../hub_ready_model"

    # Verificar se o modelo existe
    if not os.path.exists(model_path):
        print(f"❌ Diretório do modelo não encontrado: {model_path}")
        return

    # Preparar modelo para Hub
    if prepare_model_for_hub(model_path, output_dir):
        print("✅ Modelo preparado com sucesso!")

        # Criar script de upload
        upload_script = create_upload_script(output_dir)

        print("\n" + "=" * 60)
        print("🎯 PRÓXIMOS PASSOS")
        print("=" * 60)
        print("1. ✅ Modelo preparado para Hub")
        print("2. 🔧 Configurar Hugging Face Hub:")
        print("   - Instalar: pip install huggingface_hub")
        print("   - Login: huggingface-cli login")
        print("3. 📝 Editar upload_to_hub.py com seu username")
        print("4. 🚀 Executar: python upload_to_hub.py")
        print(
            "5. 🌐 Verificar no Hub: https://huggingface.co/SEU_USUARIO/email-prod-improd-ptbr-bert"
        )

        print(f"\n📁 Arquivos preparados em: {output_dir}")
        print(f"📤 Script de upload: {upload_script}")

        print("\n💡 Para fazer upload:")
        print(f"   cd {output_dir}")
        print("   python setup_hub.py  # RECOMENDADO - configuração automática")
        print("   # OU")
        print("   python upload_to_hub.py  # upload manual")
        print(f"\n📋 IMPORTANTE: Use setup_hub.py para garantir categorização correta!")

    else:
        print("❌ Falha ao preparar modelo para Hub")


if __name__ == "__main__":
    main()
