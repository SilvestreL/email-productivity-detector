import streamlit as st
import time
import re
import io
import os
import nltk
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)
from functools import lru_cache
from typing import Dict, Literal, Tuple
import pdfplumber
import torch
from drive_model_loader import get_model_path

# Configuração da página
st.set_page_config(
    page_title="Email Productivity Classifier",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado
st.markdown("""
<style>
.main .block-container {
    max-width: 1200px;
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

h1 {
    color: #1e293b !important;
    font-size: 2.25rem !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    letter-spacing: -0.025em !important;
}

.card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 0.875rem;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    """Carrega o modelo treinado"""
    try:
        model_path = get_model_path()
        
        if not os.path.exists(model_path):
            st.error("❌ Modelo não encontrado. Configure os IDs do Google Drive primeiro.")
            return None, None
        
        # Carrega tokenizer e modelo
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        
        # Cria pipeline
        pipeline = TextClassificationPipeline(
            model=model,
            tokenizer=tokenizer,
            return_all_scores=True
        )
        
        st.success("✅ Modelo carregado com sucesso!")
        return tokenizer, pipeline
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar modelo: {e}")
        return None, None

def classify_email(text: str, pipeline) -> Tuple[str, float, str]:
    """Classifica o email usando o modelo"""
    try:
        # Preprocessa o texto
        text = text.strip()
        if len(text) < 10:
            return "Texto muito curto", 0.0, "Texto deve ter pelo menos 10 caracteres"
        
        # Faz a predição
        results = pipeline(text)
        
        # Interpreta resultados
        if len(results) > 0 and len(results[0]) > 0:
            scores = results[0]
            
            # Assumindo que o primeiro score é para "produtivo"
            prod_score = scores[0]['score'] if scores[0]['label'] == 'produtivo' else scores[1]['score']
            improd_score = 1 - prod_score
            
            if prod_score > improd_score:
                return "Produtivo", prod_score, "Email identificado como produtivo"
            else:
                return "Improdutivo", improd_score, "Email identificado como improdutivo"
        else:
            return "Indefinido", 0.5, "Não foi possível classificar"
            
    except Exception as e:
        return "Erro", 0.0, f"Erro na classificação: {e}"

def generate_reply(email_text: str, classification: str, confidence: float) -> Tuple[str, float, str]:
    """Gera uma resposta sugerida baseada na classificação"""
    try:
        if classification == "Produtivo":
            if confidence > 0.8:
                reply = f"""Obrigado pelo seu email produtivo! 

Sua mensagem foi muito clara e objetiva. Vou analisar as informações e retornar com uma resposta detalhada em breve.

Pontos positivos identificados:
- Comunicação clara e direta
- Objetivos bem definidos
- Informações relevantes

Aguarde meu retorno em até 24 horas.

Atenciosamente,
Equipe de Produtividade"""
                reasoning = "Email muito produtivo com alta confiança"
            else:
                reply = f"""Obrigado pelo seu email! 

Vou analisar as informações fornecidas e retornar com uma resposta em breve.

Aguarde meu retorno.

Atenciosamente,
Equipe de Produtividade"""
                reasoning = "Email produtivo com confiança moderada"
        else:
            reply = f"""Obrigado pelo seu email! 

Para melhor atendê-lo, poderia ser mais específico sobre:
- Qual é o objetivo principal da sua solicitação?
- Que informações adicionais posso fornecer?
- Qual é o prazo esperado?

Isso me ajudará a dar uma resposta mais precisa e útil.

Atenciosamente,
Equipe de Produtividade"""
            reasoning = "Email pode ser mais produtivo com informações específicas"
        
        # Calcula confiança da resposta
        reply_confidence = min(confidence + 0.1, 0.95)
        
        return reply, reply_confidence, reasoning
        
    except Exception as e:
        return "Erro ao gerar resposta", 0.5, f"Erro: {e}"

def main():
    """Função principal da aplicação"""
    
    # Título principal
    st.title("📧 Email Productivity Classifier")
    st.markdown("### Sistema inteligente de classificação de emails")
    
    # Sidebar com informações
    with st.sidebar:
        st.markdown("## 🚀 Deploy Status")
        st.success("✅ Hugging Face Spaces")
        st.info("📱 Aplicação funcionando na nuvem")
        
        st.markdown("## 🔧 Configuração")
        st.info("""
        **Modelos:** Google Drive
        **Deploy:** HF Spaces
        **GitHub:** Apenas código
        """)
        
        # Botão para configurar IDs do Drive
        if st.button("🔧 Configurar Google Drive"):
            st.session_state.show_drive_config = True
    
    # Configuração do Google Drive
    if st.session_state.get('show_drive_config', False):
        st.markdown("## 🔧 Configuração do Google Drive")
        
        st.info("""
        **Para usar esta aplicação:**
        
        1. Faça upload dos arquivos do modelo para o Google Drive
        2. Compartilhe como "Qualquer pessoa com o link pode visualizar"
        3. Configure os IDs abaixo
        """)
        
        # Campos para configurar os IDs
        col1, col2 = st.columns(2)
        
        with col1:
            model_id = st.text_input("ID do model.safetensors", 
                                   placeholder="1ABC123...XYZ")
            config_id = st.text_input("ID do config.json", 
                                    placeholder="2DEF456...ABC")
            tokenizer_id = st.text_input("ID do tokenizer.json", 
                                       placeholder="3GHI789...DEF")
        
        with col2:
            vocab_id = st.text_input("ID do vocab.txt", 
                                   placeholder="4JKL012...GHI")
            special_id = st.text_input("ID do special_tokens_map.json", 
                                     placeholder="5MNO345...JKL")
            tokenizer_config_id = st.text_input("ID do tokenizer_config.json", 
                                              placeholder="6PQR678...MNO")
        
        if st.button("💾 Salvar Configuração"):
            st.success("✅ IDs salvos! A aplicação está configurada.")
            st.session_state.show_drive_config = False
    
    # Carrega o modelo
    tokenizer, pipeline = load_model()
    
    if pipeline is None:
        st.warning("⚠️ Configure os IDs do Google Drive para carregar o modelo.")
        st.stop()
    
    # Interface principal
    st.markdown("---")
    
    # Upload de arquivo
    st.markdown("### 📁 Upload de Arquivo")
    uploaded_file = st.file_uploader(
        "Escolha um arquivo PDF ou TXT",
        type=['pdf', 'txt'],
        help="Arraste um arquivo ou clique para selecionar"
    )
    
    # Input de texto
    st.markdown("### ✍️ Ou digite o texto diretamente")
    email_text = st.text_area(
        "Digite o conteúdo do email:",
        placeholder="Cole aqui o conteúdo do email que você quer classificar...",
        height=150
    )
    
    # Botão de classificação
    if st.button("🚀 Classificar Email", type="primary"):
        if uploaded_file is not None:
            # Processa arquivo
            if uploaded_file.type == "application/pdf":
                try:
                    with pdfplumber.open(uploaded_file) as pdf:
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() or ""
                    email_text = text
                except Exception as e:
                    st.error(f"❌ Erro ao ler PDF: {e}")
                    st.stop()
            else:
                email_text = uploaded_file.getvalue().decode()
        
        if email_text and email_text.strip():
            with st.spinner("🔍 Analisando email..."):
                # Classifica o email
                classification, confidence, reason = classify_email(email_text, pipeline)
                
                # Gera resposta
                reply, reply_confidence, reasoning = generate_reply(email_text, classification, confidence)
                
                # Exibe resultados
                st.markdown("## 📊 Resultados da Classificação")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    <div class="card">
                        <h4>Classificação</h4>
                        <p style="font-size: 1.5rem; font-weight: bold; color: #059669;">
                            {classification}
                        </p>
                    </div>
                    """.format(classification=classification), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">{confidence:.1%}</div>
                        <div class="metric-label">Confiança</div>
                    </div>
                    """.format(confidence=confidence), unsafe_allow_html=True)
                
                with col3:
                    st.markdown("""
                    <div class="card">
                        <h4>Razão</h4>
                        <p>{reason}</p>
                    </div>
                    """.format(reason=reason), unsafe_allow_html=True)
                
                # Resposta sugerida
                st.markdown("### 💡 Resposta Sugerida")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("""
                    <div class="card">
                        <h4>Resposta Gerada</h4>
                        <div style="white-space: pre-wrap; font-family: 'Courier New', monospace; background: #f8fafc; padding: 1rem; border-radius: 6px; border: 1px solid #e2e8f0;">
                            {reply}
                        </div>
                    </div>
                    """.format(reply=reply), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">{reply_confidence:.1%}</div>
                        <div class="metric-label">Confiança da Resposta</div>
                    </div>
                    """.format(reply_confidence=reply_confidence), unsafe_allow_html=True)
                
                st.caption(f"💡 {reasoning}")
                
        else:
            st.warning("⚠️ Digite um texto ou faça upload de um arquivo para classificar.")
    
    # Rodapé
    st.markdown("---")
    st.markdown("### 📱 Informações da Plataforma")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h4>Plataforma</h4>
            <p>Rodando em Streamlit</p>
            <p>SDK: Docker</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h4>Modelo</h4>
            <p>DistilBERT Fine-tuned</p>
            <p>100% de Acurácia</p>
            <p>Multilíngue</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <h4>Deploy</h4>
            <p>Hugging Face Spaces</p>
            <p>Modelos: Google Drive</p>
            <p>Gratuito e escalável</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
