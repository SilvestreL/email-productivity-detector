#!/usr/bin/env python3
"""
Script para testar todas as categorias do classificador inteligente
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_all_categories():
    """
    Testa todas as categorias do classificador inteligente
    """
    
    # Importar o classificador do app
    from app import smart_classifier
    
    print("🧪 TESTANDO TODAS AS CATEGORIAS")
    print("=" * 60)
    
    # Testes organizados por categoria
    test_cases = {
        "aniversario_parabens": [
            "Feliz aniversário, João! Muitas felicidades e saúde.",
            "Parabéns pelo seu aniversário! Desejo muitos anos de vida.",
            "Feliz aniversário! Que Deus abençoe muito sua vida."
        ],
        
        "feriado_datas_especiais": [
            "Desejo a todos um excelente feriado, aproveitem bastante!",
            "Feliz Natal a todos! Que seja um momento especial.",
            "Bom feriado! Aproveitem o descanso.",
            "Desejo a todos um ótimo fim de semana!"
        ],
        
        "saudacoes_sociais": [
            "Bom dia a todos! Apenas para informar que hoje é sexta-feira.",
            "Oi pessoal! Só passando para dar um oi.",
            "Bom dia equipe! Apenas informando que estarei ausente hoje.",
            "Olá a todos! Só para avisar que amanhã é feriado."
        ],
        
        "agradecimento": [
            "Obrigado pelo envio dos documentos.",
            "Valeu pela ajuda!",
            "Agradeço muito o suporte.",
            "Obrigada a todos pela colaboração."
        ],
        
        "solicitacao_acao": [
            "Preciso de uma reunião para discutir o projeto.",
            "Solicito orçamento para desenvolvimento de aplicação.",
            "Necessito de suporte técnico urgente.",
            "Requer análise do sistema de produção."
        ],
        
        "problema_urgencia": [
            "Estamos enfrentando problemas com o servidor.",
            "O sistema está apresentando erros críticos.",
            "Falha no banco de dados, precisa de suporte.",
            "Bug crítico na aplicação de produção."
        ],
        
        "lembrete_agendamento": [
            "Lembre-se da reunião amanhã às 10h.",
            "Deadline do projeto é na próxima sexta.",
            "Agenda reunião para discutir o cronograma.",
            "Lembrete: apresentação na próxima semana."
        ],
        
        "informacao_geral": [
            "Informo que o sistema estará em manutenção.",
            "Comunico que a reunião foi cancelada.",
            "Aviso que o prazo foi prorrogado.",
            "Notifico que novos recursos estão disponíveis."
        ]
    }
    
    # Executar testes
    results = {}
    
    for category, texts in test_cases.items():
        print(f"\n🏷️  TESTANDO CATEGORIA: {category.upper()}")
        print("-" * 50)
        
        category_results = []
        
        for i, text in enumerate(texts, 1):
            print(f"\n📧 Teste {i}: {text}")
            
            # Simular predição do modelo BERT (para teste)
            model_prediction = {
                "category": "produtivo",  # Simulação de erro do BERT
                "confidence": 0.75
            }
            
            # Classificação inteligente
            result = smart_classifier.smart_classify(text, model_prediction)
            
            print(f"   🎯 Categoria Final: {result['category']}")
            print(f"   📊 Confiança: {result['confidence']:.1%}")
            print(f"   🔧 Método: {result['method']}")
            print(f"   ✅ Correção: {result['correction_applied']}")
            
            # Verificar se classificou corretamente
            is_correct = result['category'] == category
            status = "✅ CORRETO" if is_correct else "❌ INCORRETO"
            print(f"   {status}")
            
            category_results.append({
                "text": text,
                "expected": category,
                "actual": result['category'],
                "correct": is_correct,
                "confidence": result['confidence'],
                "method": result['method']
            })
        
        # Estatísticas da categoria
        correct_count = sum(1 for r in category_results if r['correct'])
        total_count = len(category_results)
        accuracy = correct_count / total_count if total_count > 0 else 0
        
        print(f"\n📊 Estatísticas da categoria '{category}':")
        print(f"   ✅ Corretos: {correct_count}/{total_count}")
        print(f"   📈 Acurácia: {accuracy:.1%}")
        
        results[category] = {
            "accuracy": accuracy,
            "tests": category_results
        }
    
    # Resumo geral
    print(f"\n{'='*60}")
    print("📊 RESUMO GERAL")
    print(f"{'='*60}")
    
    total_tests = sum(len(r['tests']) for r in results.values())
    total_correct = sum(sum(1 for t in r['tests'] if t['correct']) for r in results.values())
    overall_accuracy = total_correct / total_tests if total_tests > 0 else 0
    
    print(f"🎯 Total de Testes: {total_tests}")
    print(f"✅ Total de Corretos: {total_correct}")
    print(f"📈 Acurácia Geral: {overall_accuracy:.1%}")
    
    # Ranking das categorias
    print(f"\n🏆 RANKING DAS CATEGORIAS:")
    sorted_categories = sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True)
    
    for i, (category, data) in enumerate(sorted_categories, 1):
        print(f"   {i}º {category.upper()}: {data['accuracy']:.1%}")
    
    return results

if __name__ == "__main__":
    test_all_categories()
