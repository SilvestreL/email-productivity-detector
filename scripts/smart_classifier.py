#!/usr/bin/env python3
"""
Classificador Inteligente com Pós-processamento para Corrigir Classificações Óbvias
"""

import re
from typing import Dict, Tuple, List

class SmartEmailClassifier:
    """
    Classificador inteligente que combina modelo BERT com regras baseadas em palavras-chave
    """
    
    def __init__(self):
        # Categorias mais granulares
        self.categories = {
            "aniversario_parabens": {
                "keywords": ["aniversário", "parabéns", "felicidades", "saúde", "muitos anos", "feliz aniversário"],
                "priority": 1.0,  # Alta prioridade
                "response_type": "social_greeting"
            },
            "agradecimento": {
                "keywords": ["obrigado", "obrigada", "valeu", "agradeço", "agradecemos", "grato"],
                "priority": 0.9,
                "response_type": "acknowledgment"
            },
            "informacao_geral": {
                "keywords": ["informar", "comunicar", "avisar", "notificar", "divulgar"],
                "priority": 0.8,
                "response_type": "information"
            },
            "solicitacao_acao": {
                "keywords": ["preciso", "solicito", "requer", "necessito", "urgente", "reunião", "projeto"],
                "priority": 0.7,
                "response_type": "action_required"
            },
            "problema_urgencia": {
                "keywords": ["problema", "erro", "falha", "crítico", "emergência", "bug", "sistema"],
                "priority": 0.9,
                "response_type": "urgent_action"
            },
            "lembrete_agendamento": {
                "keywords": ["lembrar", "lembrete", "agenda", "horário", "data", "deadline"],
                "priority": 0.8,
                "response_type": "reminder"
            }
        }
    
    def classify_with_keywords(self, text: str) -> Tuple[str, float, str]:
        """
        Classifica usando palavras-chave com alta confiança
        """
        text_lower = text.lower()
        
        # Verificar cada categoria
        for category, config in self.categories.items():
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    confidence = config["priority"]
                    response_type = config["response_type"]
                    return category, confidence, response_type
        
        # Se não encontrar palavras-chave específicas, retornar None
        return None, 0.0, None
    
    def smart_classify(self, text: str, model_prediction: Dict) -> Dict:
        """
        Classificação inteligente combinando palavras-chave e modelo BERT
        """
        
        # Primeiro, verificar se há palavras-chave óbvias
        keyword_category, keyword_confidence, response_type = self.classify_with_keywords(text)
        
        # Se encontrou categoria por palavras-chave com alta confiança
        if keyword_category and keyword_confidence > 0.8:
            return {
                "category": keyword_category,
                "confidence": keyword_confidence,
                "response_type": response_type,
                "method": "keyword_based",
                "original_model_prediction": model_prediction,
                "correction_applied": True
            }
        
        # Se não, usar predição do modelo
        return {
            "category": model_prediction["category"],
            "confidence": model_prediction["confidence"],
            "response_type": "model_based",
            "method": "bert_model",
            "correction_applied": False
        }
    
    def get_smart_response(self, classification: Dict) -> str:
        """
        Gera resposta inteligente baseada na classificação
        """
        category = classification["category"]
        response_type = classification.get("response_type", "default")
        
        responses = {
            "aniversario_parabens": {
                "profissional": "Obrigado pela mensagem de aniversário! Desejamos muitas felicidades e sucesso.",
                "amigável": "Que legal! Obrigado por compartilhar essa data especial! 🎉 Muitas felicidades!",
                "formal": "Agradecemos a mensagem de aniversário. Desejamos muitas felicidades e prosperidade."
            },
            "agradecimento": {
                "profissional": "De nada! Ficamos felizes em poder ajudar.",
                "amigável": "Por nada! 😊 Foi um prazer!",
                "formal": "É um prazer poder auxiliar. Ficamos à disposição para futuras demandas."
            },
            "informacao_geral": {
                "profissional": "Informação recebida e registrada. Obrigado pela comunicação.",
                "amigável": "Ok, anotado! 👍 Obrigado por informar!",
                "formal": "Informação recebida e devidamente registrada. Agradecemos a comunicação."
            },
            "solicitacao_acao": {
                "profissional": "Solicitação recebida. Vamos analisar e retornar em breve com as informações solicitadas.",
                "amigável": "Beleza! Vou dar uma olhada nisso e te retorno! 😊",
                "formal": "Solicitação recebida e está sendo processada. Retornaremos em breve com as informações solicitadas."
            },
            "problema_urgencia": {
                "profissional": "Problema identificado. Nossa equipe técnica foi notificada e está trabalhando na solução.",
                "amigável": "Ops! Vou resolver isso rapidinho! 🚀",
                "formal": "Problema identificado e nossa equipe técnica foi imediatamente notificada. Estamos trabalhando na solução."
            },
            "lembrete_agendamento": {
                "profissional": "Lembrete registrado. Confirmaremos o agendamento em breve.",
                "amigável": "Perfeito! Vou anotar na agenda! 📅",
                "formal": "Lembrete registrado e será confirmado em breve. Agradecemos a comunicação."
            }
        }
        
        # Retornar resposta baseada na categoria e tipo
        if category in responses:
            return responses[category]["profissional"]  # Default para profissional
        
        # Resposta padrão se não encontrar categoria específica
        return "Mensagem recebida. Obrigado pelo contato."

def test_smart_classifier():
    """
    Testa o classificador inteligente
    """
    
    classifier = SmartEmailClassifier()
    
    # Testes
    test_cases = [
        "Feliz aniversário, João! Muitas felicidades e saúde.",
        "Preciso de uma reunião para discutir o projeto.",
        "Obrigado pelo envio dos documentos.",
        "Estamos enfrentando problemas com o servidor.",
        "Lembre-se da reunião amanhã às 10h.",
        "Bom dia a todos! Apenas para informar que hoje é sexta-feira."
    ]
    
    print("🧪 Testando Classificador Inteligente")
    print("=" * 50)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📧 Teste {i}: {text}")
        
        # Simular predição do modelo (para teste)
        model_prediction = {
            "category": "produtivo",  # Simulação
            "confidence": 0.75
        }
        
        # Classificação inteligente
        result = classifier.smart_classify(text, model_prediction)
        
        print(f"   🏷️  Categoria: {result['category']}")
        print(f"   📊 Confiança: {result['confidence']:.2%}")
        print(f"   🔧 Método: {result['method']}")
        print(f"   ✅ Correção: {result['correction_applied']}")
        
        # Resposta inteligente
        response = classifier.get_smart_response(result)
        print(f"   💬 Resposta: {response}")

if __name__ == "__main__":
    test_smart_classifier()
