#!/usr/bin/env python3
"""
Script principal para organizar o fluxo completo de trabalho
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def run_command(command: str, cwd: str = None, description: str = ""):
    """
    Executa um comando e exibe o resultado

    Args:
        command: Comando a ser executado
        cwd: Diretório de trabalho
        description: Descrição do comando
    """
    if description:
        print(f"\n🔄 {description}")
        print(f"💻 Comando: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode == 0:
            print("✅ Comando executado com sucesso!")
            if result.stdout:
                print("📤 Saída:")
                print(result.stdout)
        else:
            print(f"❌ Erro na execução: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

    return True


def check_dependencies():
    """
    Verifica se as dependências estão instaladas
    """
    print("🔍 Verificando dependências...")

    required_packages = ["torch", "transformers", "streamlit", "nltk"]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} não encontrado")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("💡 Instale com: pip install " + " ".join(missing_packages))
        return False

    return True


def test_model():
    """
    Testa o modelo BERT
    """
    print("\n🧪 TESTANDO MODELO BERT")
    print("=" * 50)

    script_path = "test_bert_model.py"
    if os.path.exists(script_path):
        return run_command(
            f"python {script_path}",
            cwd=".",
            description="Executando testes do modelo BERT",
        )
    else:
        print(f"❌ Script de teste não encontrado: {script_path}")
        return False


def update_app():
    """
    Atualiza o app Streamlit para usar modelo local
    """
    print("\n🔄 ATUALIZANDO STREAMLIT APP")
    print("=" * 50)

    script_path = "update_app_local.py"
    if os.path.exists(script_path):
        return run_command(
            f"python {script_path}",
            cwd=".",
            description="Atualizando app para modelo local",
        )
    else:
        print(f"❌ Script de atualização não encontrado: {script_path}")
        return False


def test_streamlit_app():
    """
    Testa o app Streamlit
    """
    print("\n🚀 TESTANDO STREAMLIT APP")
    print("=" * 50)

    # Verificar se o app.py foi atualizado
    app_path = "../app.py"
    if not os.path.exists(app_path):
        print(f"❌ App.py não encontrado: {app_path}")
        return False

    # Verificar se o modelo local está configurado
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()
        if "models/bert_prod_improd" in content:
            print("✅ App configurado para modelo local")
        else:
            print("❌ App não configurado para modelo local")
            return False

    print("✅ App Streamlit está pronto para uso!")
    print("💡 Para executar: streamlit run ../app.py")

    return True


def prepare_for_hub():
    """
    Prepara o modelo para publicação no Hugging Face Hub
    """
    print("\n🌐 PREPARANDO PARA HUGGING FACE HUB")
    print("=" * 50)

    script_path = "prepare_for_hub.py"
    if os.path.exists(script_path):
        return run_command(
            f"python {script_path}", cwd=".", description="Preparando modelo para Hub"
        )
    else:
        print(f"❌ Script de preparação não encontrado: {script_path}")
        return False


def create_workflow_summary():
    """
    Cria um resumo do fluxo de trabalho
    """
    summary = """
# 📋 FLUXO DE TRABALHO - Email Productivity Detector

## 🎯 Objetivo
Classificar emails em português brasileiro como Produtivo ou Improdutivo usando modelo BERT fine-tuned.

## 📁 Estrutura do Projeto
```
email-productivity-detector/
├── models/
│   └── bert_prod_improd/          # Modelo BERT treinado
├── scripts/
│   ├── test_bert_model.py         # Testes do modelo
│   ├── update_app_local.py        # Atualiza app para modelo local
│   ├── prepare_for_hub.py         # Prepara para Hugging Face Hub
│   └── organize_workflow.py       # Este script
├── app.py                         # App Streamlit
└── requirements.txt               # Dependências
```

## 🚀 Fluxo de Trabalho

### 1. ✅ Modelo Treinado
- Modelo BERT fine-tuned em `models/bert_prod_improd/`
- Configurado para classificação binária (Produtivo/Improdutivo)
- Otimizado para português brasileiro

### 2. 🧪 Testes do Modelo
```bash
cd scripts
python test_bert_model.py
```
- Testa classificação com exemplos
- Mede performance e acurácia
- Gera relatório de resultados

### 3. 🔄 Integração no Streamlit
```bash
cd scripts
python update_app_local.py
```
- Atualiza app.py para usar modelo local
- Cria backup do arquivo original
- Configura caminhos corretos

### 4. 🚀 Teste do App
```bash
streamlit run app.py
```
- Interface web para classificação
- Upload de arquivos (.txt, .pdf)
- Respostas automáticas sugeridas

### 5. 🌐 Publicação no Hub
```bash
cd scripts
python prepare_for_hub.py
cd ../hub_ready_model
python upload_to_hub.py
```
- Prepara arquivos para Hub
- Cria model card e documentação
- Script de upload automático

## 📊 Métricas Esperadas
- **Acurácia**: >85%
- **F1-Score**: >0.80
- **Tempo de Inferência**: <100ms
- **Suporte**: Textos até 512 tokens

## 🔧 Dependências
- torch >= 1.9.0
- transformers >= 4.20.0
- streamlit
- nltk
- huggingface_hub (para publicação)

## 🎯 Próximos Passos
1. ✅ Modelo treinado e testado
2. 🔄 App integrado e funcionando
3. 🌐 Publicar no Hugging Face Hub
4. 📊 Monitorar performance em produção
5. 🔄 Iterar e melhorar

## 💡 Dicas
- Sempre teste o modelo antes de publicar
- Mantenha backup dos arquivos originais
- Documente mudanças e melhorias
- Monitore métricas de performance
"""

    with open("../WORKFLOW_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write(summary)

    print("✅ Resumo do fluxo criado: WORKFLOW_SUMMARY.md")


def main():
    """Função principal"""
    print("🚀 ORGANIZANDO FLUXO DE TRABALHO")
    print("=" * 60)
    print("Email Productivity Detector - BERT Fine-tuned")
    print("=" * 60)

    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Dependências não atendidas. Instale os pacotes necessários.")
        return

    # Executar fluxo completo
    steps = [
        ("🧪 Testando modelo BERT", test_model),
        ("🔄 Atualizando app Streamlit", update_app),
        ("🚀 Verificando app", test_streamlit_app),
        ("🌐 Preparando para Hugging Face Hub", prepare_for_hub),
    ]

    results = {}

    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"📋 PASSO: {step_name}")
        print(f"{'='*60}")

        start_time = time.time()
        success = step_func()
        end_time = time.time()

        results[step_name] = {"success": success, "time": end_time - start_time}

        if success:
            print(f"✅ {step_name} - Concluído em {results[step_name]['time']:.1f}s")
        else:
            print(f"❌ {step_name} - Falhou em {results[step_name]['time']:.1f}s")
            print("⚠️  Continuando com próximos passos...")

    # Criar resumo do fluxo
    create_workflow_summary()

    # Resumo final
    print(f"\n{'='*60}")
    print("🎯 RESUMO FINAL")
    print(f"{'='*60}")

    successful_steps = sum(1 for r in results.values() if r["success"])
    total_steps = len(results)

    print(f"✅ Passos bem-sucedidos: {successful_steps}/{total_steps}")

    for step_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {step_name}: {result['time']:.1f}s")

    if successful_steps == total_steps:
        print(f"\n🎉 FLUXO COMPLETADO COM SUCESSO!")
        print("🎯 Próximos passos:")
        print("   1. Teste o app: streamlit run ../app.py")
        print("   2. Publique no Hub: cd ../hub_ready_model && python upload_to_hub.py")
        print("   3. Monitore performance e itere melhorias")
    else:
        print(f"\n⚠️  FLUXO PARCIALMENTE COMPLETADO")
        print("🔧 Verifique os passos que falharam e execute manualmente")

    print(f"\n📋 Resumo completo salvo em: WORKFLOW_SUMMARY.md")


if __name__ == "__main__":
    main()
