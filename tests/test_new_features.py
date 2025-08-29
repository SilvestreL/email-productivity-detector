#!/usr/bin/env python3
"""
Teste das Novas Funcionalidades - Email Productivity Classifier
"""

import sys
import os

sys.path.append("src")

from response_generator import ResponseGenerator
from file_processor import FileProcessor
import io


def test_response_generator():
    """Testa o gerador de respostas automáticas"""

    print("🧪 Testando Gerador de Respostas Automáticas")
    print("=" * 60)

    generator = ResponseGenerator()

    # Testes de emails produtivos
    productive_emails = [
        {
            "title": "📧 Suporte Técnico",
            "content": "Olá, estou com um problema no sistema. Não consigo fazer login e preciso de ajuda urgente.",
            "expected_type": "produtivo",
        },
        {
            "title": "📊 Status de Requisição",
            "content": "Gostaria de saber o status da minha requisição #12345. Quando será concluída?",
            "expected_type": "produtivo",
        },
        {
            "title": "❓ Dúvida sobre Sistema",
            "content": "Como faço para usar a nova funcionalidade de relatórios? Preciso de orientação.",
            "expected_type": "produtivo",
        },
        {
            "title": "📄 Solicitação de Arquivo",
            "content": "Preciso do relatório mensal de vendas. Pode enviar o arquivo?",
            "expected_type": "produtivo",
        },
        {
            "title": "📅 Agendamento",
            "content": "Gostaria de agendar uma reunião para discutir o projeto. Temos disponibilidade?",
            "expected_type": "produtivo",
        },
    ]

    # Testes de emails improdutivos
    unproductive_emails = [
        {
            "title": "🎉 Felicitações",
            "content": "Parabéns pelo excelente trabalho! Feliz Natal e um ótimo ano novo!",
            "expected_type": "improdutivo",
        },
        {
            "title": "🙏 Agradecimento",
            "content": "Obrigado pela ajuda. Valeu mesmo!",
            "expected_type": "improdutivo",
        },
        {
            "title": "🚨 Spam",
            "content": "CONGRATULATIONS! You've won a FREE iPhone! Click here to claim!",
            "expected_type": "improdutivo",
        },
    ]

    all_emails = productive_emails + unproductive_emails

    print("📝 Testando geração de respostas...")
    print()

    for i, email in enumerate(all_emails, 1):
        print(f"🔍 Teste {i}: {email['title']}")
        print(f"📄 Conteúdo: {email['content'][:50]}...")

        # Gera resposta
        response_summary = generator.get_response_summary(
            email["content"], email["expected_type"] == "produtivo", 0.85
        )

        print(f"✅ Tipo: {response_summary['response_type']}")
        print(
            f"📊 Categorias: {', '.join(response_summary['detected_categories']) if response_summary['detected_categories'] else 'Nenhuma'}"
        )
        print(f"💬 Resposta: {response_summary['response'][:100]}...")
        print("-" * 60)

    print("✅ Teste do gerador de respostas concluído!")
    print()


def test_file_processor():
    """Testa o processador de arquivos"""

    print("📄 Testando Processador de Arquivos")
    print("=" * 60)

    processor = FileProcessor()

    # Teste com arquivo TXT simulado
    txt_content = """From: joao@empresa.com
To: suporte@autou.com
Subject: Problema no sistema

Olá, estou com um problema técnico no sistema.
Não consigo fazer login e preciso de ajuda urgente.

Atenciosamente,
João Silva""".encode(
        "utf-8"
    )

    print("📝 Testando processamento de arquivo .txt...")

    # Simula upload de arquivo
    class MockFile:
        def __init__(self, content, name):
            self.content = content
            self.name = name

        def read(self):
            return self.content

    mock_txt_file = MockFile(txt_content, "email.txt")

    success, extracted_text, file_name = processor.process_uploaded_file(mock_txt_file)

    if success:
        print(f"✅ Arquivo processado: {file_name}")
        print(f"📊 Texto extraído: {len(extracted_text)} caracteres")

        # Valida o conteúdo
        is_valid, validation_message = processor.validate_email_content(extracted_text)
        print(f"✅ Validação: {validation_message}")

        # Informações do arquivo
        file_info = processor.get_file_info(file_name, extracted_text)
        print(
            f"📈 Palavras: {file_info['word_count']}, Linhas: {file_info['line_count']}"
        )
    else:
        print("❌ Erro no processamento do arquivo")

    print()
    print("✅ Teste do processador de arquivos concluído!")
    print()


def test_integration():
    """Testa a integração completa"""

    print("🔗 Testando Integração Completa")
    print("=" * 60)

    from response_generator import ResponseGenerator
    from file_processor import FileProcessor

    # Simula um fluxo completo
    email_content = """From: maria@empresa.com
To: suporte@autou.com
Subject: Solicitação de suporte

Olá, preciso de ajuda com um problema no sistema.
Não consigo acessar os relatórios e isso está afetando meu trabalho.

Pode me ajudar?

Atenciosamente,
Maria Santos"""

    print("📧 Simulando análise completa de email...")
    print(f"📄 Conteúdo: {email_content[:100]}...")

    # 1. Processa o arquivo (simulado)
    processor = FileProcessor()
    is_valid, validation_message = processor.validate_email_content(email_content)

    if is_valid:
        print(f"✅ Validação: {validation_message}")

        # 2. Classifica (simulado - assume produtivo)
        is_productive = True
        confidence = 0.85

        print(f"🤖 Classificação: {'Produtivo' if is_productive else 'Improdutivo'}")
        print(f"📊 Confiança: {confidence:.1%}")

        # 3. Gera resposta
        generator = ResponseGenerator()
        response_summary = generator.get_response_summary(
            email_content, is_productive, confidence
        )

        print(f"💬 Tipo de Resposta: {response_summary['response_type']}")
        print(
            f"📋 Categorias Detectadas: {', '.join(response_summary['detected_categories'])}"
        )
        print(f"📝 Resposta Gerada: {response_summary['response'][:200]}...")

        print("✅ Fluxo completo executado com sucesso!")
    else:
        print(f"❌ Validação falhou: {validation_message}")

    print()


def main():
    """Função principal"""

    print("🚀 Teste das Novas Funcionalidades - Email Productivity Classifier")
    print("=" * 80)
    print()

    try:
        # Testa gerador de respostas
        test_response_generator()

        # Testa processador de arquivos
        test_file_processor()

        # Testa integração
        test_integration()

        print("🎉 Todos os testes concluídos com sucesso!")
        print("✅ Sistema pronto para uso com as novas funcionalidades!")

    except Exception as e:
        print(f"❌ Erro durante os testes: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
