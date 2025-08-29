#!/usr/bin/env python3
"""
Demonstração interativa do Email Productivity Classifier
"""

import joblib
import pandas as pd
import time


def load_model():
    """Carrega o modelo treinado"""
    try:
        return joblib.load("models/email_spam_pipeline.joblib")
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return None


def predict_message(model, message):
    """Faz predição de uma mensagem"""
    try:
        # Faz a predição
        prediction = model.predict([message])[0]
        probabilities = model.predict_proba([message])[0]

        # Retorna resultado
        is_productive = prediction == 0
        confidence = max(probabilities) * 100

        return is_productive, confidence, probabilities
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
        return None, None, None


def demo():
    """Demonstração interativa"""

    print("🎬 Email Productivity Classifier - Demonstração")
    print("=" * 60)

    # Carrega o modelo
    print("📥 Carregando modelo...")
    model = load_model()
    if model is None:
        return

    print("✅ Modelo carregado com sucesso!")
    print()

    # Exemplos de demonstração
    demo_messages = [
        {
            "title": "📧 Email de Trabalho",
            "message": "Olá João, gostaria de agendar uma reunião para discutir o projeto de marketing da próxima semana. Podemos marcar para amanhã às 14h?",
            "expected": "Produtivo",
        },
        {
            "title": "📊 Relatório Importante",
            "message": "Relatório mensal de vendas está pronto para revisão. As metas foram atingidas em 95% e precisamos discutir estratégias para o próximo mês.",
            "expected": "Produtivo",
        },
        {
            "title": "🎯 Proposta Comercial",
            "message": "Prezado cliente, temos uma proposta especial para sua empresa. Desconto de 20% em todos os produtos até o final do mês. Entre em contato!",
            "expected": "Produtivo",
        },
        {
            "title": "🚨 Spam - Prêmio Falso",
            "message": "CONGRATULATIONS! You've won a FREE iPhone 15! Click here to claim your prize NOW! Limited time offer! Don't miss out!",
            "expected": "Improdutivo",
        },
        {
            "title": "⚠️ Spam - Urgência Falsa",
            "message": "URGENT: Your bank account has been SUSPENDED! Verify your identity immediately or lose access forever! Click here NOW!",
            "expected": "Improdutivo",
        },
        {
            "title": "💰 Spam - Dinheiro Fácil",
            "message": "Make $5000/day working from home! No experience needed! Join thousands of people earning money online! Click here to start!",
            "expected": "Improdutivo",
        },
    ]

    print("🧪 Executando demonstração automática...")
    print()

    correct = 0
    total = len(demo_messages)

    for i, demo in enumerate(demo_messages, 1):
        print(f"🔍 Teste {i}: {demo['title']}")
        print(f"📝 Mensagem: {demo['message']}")

        # Faz predição
        is_productive, confidence, probabilities = predict_message(
            model, demo["message"]
        )

        if is_productive is not None:
            predicted = "Produtivo" if is_productive else "Improdutivo"
            expected = demo["expected"]

            # Verifica se está correto
            is_correct = predicted == expected
            if is_correct:
                correct += 1

            # Exibe resultado
            status = "✅" if is_correct else "❌"
            print(f"{status} Predito: {predicted} | Esperado: {expected}")
            print(f"📊 Confiança: {confidence:.1f}%")

            if is_productive:
                productive_prob = probabilities[0] * 100
                unproductive_prob = probabilities[1] * 100
            else:
                productive_prob = probabilities[0] * 100
                unproductive_prob = probabilities[1] * 100

            print(
                f"📈 Probabilidades: Produtivo {productive_prob:.1f}% | Improdutivo {unproductive_prob:.1f}%"
            )
        else:
            print("❌ Erro na predição")

        print("-" * 60)
        time.sleep(1)  # Pausa para visualização

    # Resultado final
    accuracy = (correct / total) * 100
    print(f"🎯 Resultado da Demonstração: {correct}/{total} corretos ({accuracy:.1f}%)")

    if accuracy >= 80:
        print("🎉 Demonstração bem-sucedida! O modelo está funcionando corretamente.")
    else:
        print("⚠️ O modelo pode precisar de ajustes adicionais.")

    print()
    print(
        "💡 Dica: Execute 'streamlit run src/app_streamlit.py' para usar a interface web!"
    )
    print("=" * 60)


if __name__ == "__main__":
    demo()
