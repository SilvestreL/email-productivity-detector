#!/usr/bin/env python3
"""
Script de teste para o Email Productivity Classifier
"""

import joblib
import pandas as pd

def test_model():
    """Testa o modelo com exemplos conhecidos"""
    
    print("🧪 Testando Email Productivity Classifier")
    print("=" * 50)
    
    # Carrega o modelo
    try:
        model = joblib.load('models/email_spam_pipeline.joblib')
        print("✅ Modelo carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return
    
    # Exemplos de teste
    test_messages = [
        # Produtivos
        "Reunião importante amanhã às 10h para discutir o projeto de marketing.",
        "Relatório mensal de vendas está pronto para revisão.",
        "Confirmação de entrega do pedido #12345 para sexta-feira.",
        "Olá, gostaria de agendar uma reunião para discutir o projeto.",
        
        # Improdutivos
        "CONGRATULATIONS! You've won a free iPhone! Click here to claim!",
        "URGENT: Your account has been suspended. Verify now!",
        "Make money fast! Work from home and earn $5000/day!",
        "FREE VIAGRA NOW!!! Click here for amazing deals!",
        "You've been selected for a $1000 Walmart gift card!"
    ]
    
    expected_labels = [
        "Produtivo", "Produtivo", "Produtivo", "Produtivo",
        "Improdutivo", "Improdutivo", "Improdutivo", "Improdutivo", "Improdutivo"
    ]
    
    print("\n📝 Testando mensagens...")
    print("-" * 50)
    
    correct_predictions = 0
    total_predictions = len(test_messages)
    
    for i, (message, expected) in enumerate(zip(test_messages, expected_labels), 1):
        # Faz predição
        prediction = model.predict([message])[0]
        probabilities = model.predict_proba([message])[0]
        
        # Converte para label legível
        predicted_label = "Produtivo" if prediction == 0 else "Improdutivo"
        confidence = max(probabilities) * 100
        
        # Verifica se está correto
        is_correct = predicted_label == expected
        if is_correct:
            correct_predictions += 1
        
        # Exibe resultado
        status = "✅" if is_correct else "❌"
        print(f"{status} Teste {i}: {predicted_label} (esperado: {expected}) - Confiança: {confidence:.1f}%")
        print(f"   Mensagem: {message[:50]}...")
        print()
    
    # Resultado final
    accuracy = (correct_predictions / total_predictions) * 100
    print("=" * 50)
    print(f"🎯 Resultado: {correct_predictions}/{total_predictions} corretos ({accuracy:.1f}%)")
    
    if accuracy >= 80:
        print("✅ Modelo funcionando corretamente!")
    else:
        print("⚠️ Modelo pode precisar de ajustes.")
    
    return accuracy >= 80

if __name__ == "__main__":
    test_model()
