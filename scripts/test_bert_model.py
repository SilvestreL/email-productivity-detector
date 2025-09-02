#!/usr/bin/env python3
"""
Script de teste para o modelo BERT fine-tuned para classificação de emails
"""

import os
import sys
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)
import json
from typing import Dict, List
import time

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_model(model_path: str):
    """
    Carrega o modelo BERT fine-tuned

    Args:
        model_path: Caminho para o diretório do modelo

    Returns:
        Tuple com (tokenizer, model, pipeline)
    """
    try:
        print(f"🔄 Carregando modelo de: {model_path}")

        # Verificar se o diretório existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Diretório do modelo não encontrado: {model_path}")

        # Carregar tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("✅ Tokenizer carregado com sucesso")

        # Carregar modelo
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        print("✅ Modelo carregado com sucesso")

        # Configurar dispositivo
        device = 0 if torch.cuda.is_available() else -1
        device_name = "CUDA" if device == 0 else "CPU"
        print(f"🖥️  Dispositivo: {device_name}")

        # Criar pipeline
        pipeline = TextClassificationPipeline(
            model=model, tokenizer=tokenizer, return_all_scores=True, device=device
        )
        print("✅ Pipeline criado com sucesso")

        return tokenizer, model, pipeline

    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return None, None, None


def test_classification(pipeline, test_texts: List[str]) -> List[Dict]:
    """
    Testa a classificação com textos de exemplo

    Args:
        pipeline: Pipeline de classificação
        test_texts: Lista de textos para testar

    Returns:
        Lista de resultados de classificação
    """
    results = []

    for i, text in enumerate(test_texts):
        print(f"\n📧 Testando texto {i+1}:")
        print(f"Texto: {text[:100]}{'...' if len(text) > 100 else ''}")

        start_time = time.time()

        try:
            # Classificar texto
            result = pipeline(text)

            # Processar resultado
            scores = {}
            for pred in result[0]:
                # O modelo retorna labels como strings ("Improdutivo", "Produtivo")
                label_name = pred["label"]
                scores[label_name] = float(pred["score"])

            # Determinar categoria
            category = max(scores, key=scores.get)
            confidence = scores[category]

            inference_time = (time.time() - start_time) * 1000  # ms

            result_dict = {
                "text": text,
                "category": category,
                "confidence": confidence,
                "scores": scores,
                "inference_time_ms": round(inference_time, 2),
            }

            results.append(result_dict)

            print(f"✅ Categoria: {category}")
            print(f"📊 Confiança: {confidence:.2%}")
            print(f"⏱️  Tempo: {inference_time:.0f}ms")
            print(f"📈 Scores: {scores}")

        except Exception as e:
            print(f"❌ Erro na classificação: {e}")
            results.append({"text": text, "error": str(e)})

    return results


def main():
    """Função principal"""
    print("🚀 Teste do Modelo BERT para Classificação de Emails")
    print("=" * 60)

    # Caminho para o modelo
    model_path = "../models/bert_prod_improd"

    # Carregar modelo
    tokenizer, model, pipeline = load_model(model_path)

    if pipeline is None:
        print("❌ Falha ao carregar modelo. Encerrando.")
        return

    print("\n" + "=" * 60)
    print("🧪 TESTES DE CLASSIFICAÇÃO")
    print("=" * 60)

    # Textos de teste
    test_texts = [
        # Email produtivo - solicita ação
        "Prezados, gostaria de solicitar uma reunião para discutir o projeto de implementação do novo sistema. Precisamos definir cronograma, recursos necessários e responsabilidades. Podem me informar a disponibilidade da equipe para próxima semana?",
        # Email produtivo - requer resposta
        "Olá, preciso de um orçamento para desenvolvimento de aplicação web. O projeto inclui sistema de login, dashboard administrativo e relatórios. Qual seria o prazo e valor estimado?",
        # Email improdutivo - apenas informação
        "Bom dia a todos! Apenas para informar que hoje é aniversário da empresa. Desejamos a todos um excelente dia!",
        # Email improdutivo - agradecimento
        "Obrigado pelo envio dos documentos. Recebemos tudo em ordem.",
        # Email produtivo - problema técnico
        "Estamos enfrentando problemas com o servidor de produção. O sistema está apresentando lentidão e alguns usuários não conseguem acessar. Precisamos de suporte urgente para resolver esta situação.",
        # Email improdutivo - piada/descontraído
        "Por que o programador foi ao médico? Porque estava com bugs! 😄 Bom dia a todos!",
    ]

    # Executar testes
    results = test_classification(pipeline, test_texts)

    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)

    # Estatísticas
    successful_tests = [r for r in results if "error" not in r]
    failed_tests = [r for r in results if "error" in r]

    print(f"✅ Testes bem-sucedidos: {len(successful_tests)}")
    print(f"❌ Testes com erro: {len(failed_tests)}")

    if successful_tests:
        avg_confidence = sum(r["confidence"] for r in successful_tests) / len(
            successful_tests
        )
        avg_time = sum(r["inference_time_ms"] for r in successful_tests) / len(
            successful_tests
        )

        print(f"📊 Confiança média: {avg_confidence:.2%}")
        print(f"⏱️  Tempo médio: {avg_time:.0f}ms")

        # Contar categorias
        categories = {}
        for r in successful_tests:
            cat = r["category"]
            categories[cat] = categories.get(cat, 0) + 1

        print(f"🏷️  Distribuição de categorias: {categories}")

    # Salvar resultados
    output_file = "test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Resultados salvos em: {output_file}")

    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASSOS")
    print("=" * 60)
    print("1. ✅ Modelo testado com sucesso")
    print("2. 🔄 Integrar no Streamlit app")
    print("3. 🚀 Publicar no Hugging Face Hub")
    print("4. 📊 Monitorar performance em produção")


if __name__ == "__main__":
    main()
