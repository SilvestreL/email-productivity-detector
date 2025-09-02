#!/usr/bin/env python3
"""
Script de debug para investigar o que o modelo BERT está retornando
"""

import os
import sys
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def debug_model():
    """
    Debug do modelo para entender o que está sendo retornado
    """

    model_path = "../models/bert_prod_improd"

    print("🔍 DEBUG DO MODELO BERT")
    print("=" * 50)

    try:
        # Carregar modelo
        print("🔄 Carregando modelo...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)

        # Verificar configuração
        print(f"📊 Configuração do modelo:")
        print(f"   - id2label: {model.config.id2label}")
        print(f"   - label2id: {model.config.label2id}")
        print(f"   - num_labels: {model.config.num_labels}")

        # Criar pipeline
        print("\n🔄 Criando pipeline...")
        pipeline = TextClassificationPipeline(
            model=model, tokenizer=tokenizer, return_all_scores=True, device=-1  # CPU
        )

        # Testar com texto simples
        test_text = "Preciso de uma reunião para discutir o projeto."
        print(f"\n🧪 Testando com texto: '{test_text}'")

        # Fazer predição
        result = pipeline(test_text)
        print(f"\n📤 Resultado bruto:")
        print(f"   Tipo: {type(result)}")
        print(f"   Conteúdo: {result}")

        # Analisar estrutura
        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            print(f"\n🔍 Primeiro resultado:")
            print(f"   Tipo: {type(first_result)}")
            print(f"   Conteúdo: {first_result}")

            if isinstance(first_result, list):
                for i, pred in enumerate(first_result):
                    print(f"\n   Predição {i}:")
                    print(f"     Tipo: {type(pred)}")
                    print(f"     Conteúdo: {pred}")
                    if isinstance(pred, dict):
                        for key, value in pred.items():
                            print(f"     {key}: {value} (tipo: {type(value)})")

        # Testar com top_k
        print(f"\n🧪 Testando com top_k=None...")
        pipeline_top_k = TextClassificationPipeline(
            model=model, tokenizer=tokenizer, top_k=None, device=-1
        )

        result_top_k = pipeline_top_k(test_text)
        print(f"📤 Resultado com top_k=None:")
        print(f"   Conteúdo: {result_top_k}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_model()
