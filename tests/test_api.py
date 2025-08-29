#!/usr/bin/env python3
"""
Script para testar a API REST do Email Productivity Classifier
AutoU - Teste Técnico
"""

import requests
import json
import time
import sys
import os

# Configuração da API
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Testa o health check da API"""
    print("🏥 Testando Health Check...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"📊 Modelo carregado: {data['model_loaded']}")
            print(f"🕒 Uptime: {data['uptime']:.2f}s")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: API não está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_single_classification():
    """Testa classificação de email único"""
    print("\n📧 Testando Classificação Única...")
    
    test_emails = [
        {
            "content": "Olá, estou com um problema técnico no sistema. Não consigo fazer login e preciso de ajuda urgente.",
            "subject": "Problema Técnico",
            "sender": "usuario@empresa.com"
        },
        {
            "content": "Parabéns pelo excelente trabalho! Feliz Natal e um ótimo ano novo!",
            "subject": "Felicitações",
            "sender": "amigo@email.com"
        },
        {
            "content": "Gostaria de saber o status da minha requisição #12345. Quando será concluída?",
            "subject": "Status de Requisição",
            "sender": "cliente@empresa.com"
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n🔍 Teste {i}: {email['subject']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/classify",
                json=email,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Produtivo: {data['is_productive']}")
                print(f"📊 Confiança: {data['confidence']:.1%}")
                print(f"🏷️  Tipo: {data['response_type']}")
                print(f"⏱️  Tempo: {data['processing_time']:.3f}s")
            else:
                print(f"❌ Erro: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

def test_batch_classification():
    """Testa classificação em lote"""
    print("\n📦 Testando Classificação em Lote...")
    
    batch_emails = [
        {
            "content": "Preciso de ajuda com o sistema de relatórios.",
            "subject": "Dúvida Sistema",
            "sender": "usuario1@empresa.com"
        },
        {
            "content": "Obrigado pela ajuda. Valeu mesmo!",
            "subject": "Agradecimento",
            "sender": "usuario2@empresa.com"
        },
        {
            "content": "CONGRATULATIONS! You've won a FREE iPhone! Click here to claim!",
            "subject": "Spam",
            "sender": "spam@fake.com"
        }
    ]
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/classify/batch",
            json={"emails": batch_emails},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total processado: {data['total_processed']}")
            print(f"⏱️  Tempo total: {data['processing_time']:.3f}s")
            
            for i, result in enumerate(data['results'], 1):
                print(f"  📧 Email {i}: {'Produtivo' if result['is_productive'] else 'Improdutivo'} ({result['confidence']:.1%})")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def test_file_classification():
    """Testa classificação de arquivo"""
    print("\n📄 Testando Classificação de Arquivo...")
    
    # Cria um arquivo de teste
    test_content = """From: maria@empresa.com
To: suporte@autou.com
Subject: Problema no Sistema

Olá, estou com um problema no sistema de vendas.
Não consigo gerar relatórios e preciso de ajuda urgente.

Atenciosamente,
Maria Santos"""
    
    test_file_path = "test_email.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "text/plain")}
            data = {"include_response": "true"}
            
            response = requests.post(
                f"{API_BASE_URL}/classify/file",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Arquivo: {result['file_info']['name']}")
            print(f"📊 Palavras: {result['file_info']['word_count']}")
            print(f"🤖 Produtivo: {result['classification']['is_productive']}")
            print(f"📈 Confiança: {result['classification']['confidence']:.1%}")
            print(f"⏱️  Tempo: {result['processing_time']:.3f}s")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    finally:
        # Remove arquivo de teste
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_model_info():
    """Testa informações do modelo"""
    print("\n🤖 Testando Informações do Modelo...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/model/info")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tipo: {data['type']}")
            print(f"📊 Features: {data['features']}")
            print(f"🏷️  Classes: {data['classes']}")
            print(f"📦 Carregado: {data['loaded']}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def test_api_docs():
    """Testa acesso à documentação da API"""
    print("\n📚 Testando Documentação da API...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        
        if response.status_code == 200:
            print("✅ Documentação acessível em: http://localhost:8000/docs")
            print("✅ ReDoc acessível em: http://localhost:8000/redoc")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def main():
    """Função principal"""
    print("🚀 Teste da API REST - Email Productivity Classifier")
    print("=" * 60)
    
    # Verifica se a API está rodando
    if not test_health_check():
        print("\n❌ API não está disponível. Execute primeiro:")
        print("   python src/api.py")
        return
    
    # Executa todos os testes
    test_single_classification()
    test_batch_classification()
    test_file_classification()
    test_model_info()
    test_api_docs()
    
    print("\n🎉 Todos os testes concluídos!")
    print("📚 Acesse a documentação em: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
