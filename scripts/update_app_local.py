#!/usr/bin/env python3
"""
Script para atualizar o app.py para usar o modelo BERT local
"""

import os
import shutil
import re

def update_app_for_local_model():
    """
    Atualiza o app.py para usar o modelo local em vez do Hugging Face Hub
    """
    
    app_file = "../app.py"
    backup_file = "../app.py.backup"
    
    # Fazer backup do arquivo original
    if os.path.exists(app_file):
        shutil.copy2(app_file, backup_file)
        print(f"✅ Backup criado: {backup_file}")
    
    # Ler o arquivo atual
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir o MODEL_ID para usar modelo local
    old_model_id = 'MODEL_ID = "SEU_USUARIO/email-prod-improd-ptbr-bert"'
    new_model_id = 'MODEL_ID = "models/bert_prod_improd"'
    
    content = content.replace(old_model_id, new_model_id)
    
    # Atualizar a função get_classifier para usar modelo local
    old_classifier = '''@st.cache_resource(show_spinner=True)
def get_classifier():
    """Carrega o modelo fine-tuned para classificação de emails"""
    try:
        # Carregar tokenizer e modelo
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)

        # Configurar dispositivo
        device = 0 if torch.cuda.is_available() else -1

        # Criar pipeline
        return TextClassificationPipeline(
            model=model, tokenizer=tokenizer, return_all_scores=True, device=device
        )
    except Exception as e:
        st.error(f"Erro ao carregar modelo: {e}")
        st.info("💡 Certifique-se de que o modelo está disponível no Hugging Face Hub")
        return None'''
    
    new_classifier = '''@st.cache_resource(show_spinner=True)
def get_classifier():
    """Carrega o modelo fine-tuned para classificação de emails"""
    try:
        # Carregar tokenizer e modelo local
        model_path = os.path.join(os.path.dirname(__file__), MODEL_ID)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)

        # Configurar dispositivo
        device = 0 if torch.cuda.is_available() else -1

        # Criar pipeline
        return TextClassificationPipeline(
            model=model, tokenizer=tokenizer, return_all_scores=True, device=device
        )
    except Exception as e:
        st.error(f"Erro ao carregar modelo: {e}")
        st.info("💡 Certifique-se de que o modelo está disponível em models/bert_prod_improd")
        return None'''
    
    content = content.replace(old_classifier, new_classifier)
    
    # Atualizar informações sobre o modelo
    old_info = '''**Modelo**: BERT PT-BR Fine-tuned  
            **Método**: Text Classification  
            **Labels**: Produtivo/Improdutivo  
            **Cache**: Ativado
            **NLP**: Stopwords PT-BR'''
    
    new_info = '''**Modelo**: BERT PT-BR Fine-tuned (Local)  
            **Método**: Text Classification  
            **Labels**: Produtivo/Improdutivo  
            **Cache**: Ativado
            **NLP**: Stopwords PT-BR'''
    
    content = content.replace(old_info, new_info)
    
    # Atualizar informações técnicas
    old_tech_info = '''"modelo": MODEL_ID,
                        "método": "text-classification",
                        "tempo_inferencia_ms": round(inference_time, 2),
                        "scores_completos": classification["scores"],
                        "tamanho_texto_original": len(classification["original_text"]),
                        "tamanho_texto_processado": len(
                            classification["processed_text"]
                        ),'''
    
    new_tech_info = '''"modelo": "BERT Local (Fine-tuned)",
                        "método": "text-classification",
                        "tempo_inferencia_ms": round(inference_time, 2),
                        "scores_completos": classification["scores"],
                        "tamanho_texto_original": len(classification["original_text"]),
                        "tamanho_texto_processado": len(
                            classification["processed_text"]
                        ),
                        "modelo_local": MODEL_ID,'''
    
    content = content.replace(old_tech_info, new_tech_info)
    
    # Atualizar informações do rodapé
    old_footer = '''**🤖 Modelo**  
            BERT PT-BR Fine-tuned  
            Text Classification'''
    
    new_footer = '''**🤖 Modelo**  
            BERT PT-BR Fine-tuned (Local)  
            Text Classification'''
    
    content = content.replace(old_footer, new_footer)
    
    # Atualizar dica sobre cold start
    old_tip = '💡 **Dica**: A primeira execução pode levar alguns segundos (cold start). Para modelo multilíngue, altere MODEL_ID no código.'
    
    new_tip = '💡 **Dica**: A primeira execução pode levar alguns segundos (cold start). Modelo local carregado de models/bert_prod_improd.'
    
    content = content.replace(old_tip, new_tip)
    
    # Escrever o arquivo atualizado
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ App.py atualizado com sucesso!")
    print(f"📁 Modelo local configurado: {new_model_id}")
    
    return True

def create_local_model_config():
    """
    Cria arquivo de configuração para o modelo local
    """
    
    config_content = '''# Configuração do Modelo Local
MODEL_CONFIG = {
    "name": "BERT PT-BR Fine-tuned para Classificação de Emails",
    "version": "1.0.0",
    "type": "text-classification",
    "labels": ["Improdutivo", "Produtivo"],
    "language": "pt-BR",
    "framework": "transformers",
    "base_model": "neuralmind/bert-base-portuguese-cased",
    "fine_tuned": True,
    "local_path": "models/bert_prod_improd",
    "performance": {
        "expected_accuracy": ">85%",
        "expected_inference_time": "<100ms",
        "max_text_length": 512
    }
}

# Configurações de cache
CACHE_CONFIG = {
    "model_cache": True,
    "tokenizer_cache": True,
    "max_cache_size": "2GB"
}
'''
    
    config_file = "../config/local_model.py"
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ Arquivo de configuração criado: {config_file}")

def main():
    """Função principal"""
    print("🔄 Atualizando Streamlit App para Modelo Local")
    print("=" * 60)
    
    # Atualizar app.py
    if update_app_for_local_model():
        print("✅ App.py atualizado com sucesso!")
    else:
        print("❌ Falha ao atualizar app.py")
        return
    
    # Criar arquivo de configuração
    create_local_model_config()
    
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASSOS")
    print("=" * 60)
    print("1. ✅ App atualizado para modelo local")
    print("2. 🧪 Testar o modelo com scripts/test_bert_model.py")
    print("3. 🚀 Executar o Streamlit app atualizado")
    print("4. 📊 Verificar performance e acurácia")
    print("5. 🌐 Publicar no Hugging Face Hub quando estiver satisfeito")
    
    print("\n💡 Para testar o app atualizado:")
    print("   streamlit run app.py")
    
    print("\n💡 Para testar apenas o modelo:")
    print("   cd scripts && python test_bert_model.py")

if __name__ == "__main__":
    main()
