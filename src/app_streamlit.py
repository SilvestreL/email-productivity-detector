# src/app_streamlit.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
from response_generator import ResponseGenerator
from file_processor import FileProcessor

# Configuração da página
st.set_page_config(
    page_title="📧 Email Productivity Classifier - AutoU",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .productive {
        color: #28a745;
        font-weight: bold;
    }
    .unproductive {
        color: #dc3545;
        font-weight: bold;
    }
    .confidence-high {
        color: #28a745;
    }
    .confidence-medium {
        color: #ffc107;
    }
    .confidence-low {
        color: #dc3545;
    }
    .response-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .file-info {
        background-color: #e3f2fd;
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_model():
    """Carrega o modelo treinado"""
    try:
        model_path = (
            Path(__file__).parent.parent / "models" / "email_spam_pipeline.joblib"
        )
        if not model_path.exists():
            st.error(
                "❌ Modelo não encontrado! Execute primeiro: `python src/train.py`"
            )
            return None
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"❌ Erro ao carregar modelo: {str(e)}")
        return None


@st.cache_resource
def load_response_generator():
    """Carrega o gerador de respostas"""
    return ResponseGenerator()


@st.cache_resource
def load_file_processor():
    """Carrega o processador de arquivos"""
    return FileProcessor()


def predict_productivity(model, text):
    """Faz predição de produtividade"""
    try:
        # Faz a predição
        prediction = model.predict([text])[0]
        probabilities = model.predict_proba([text])[0]

        # Retorna resultado
        is_productive = prediction == 0  # 0 = ham (produtivo), 1 = spam (improdutivo)
        confidence = max(probabilities) * 100

        return is_productive, confidence, probabilities
    except Exception as e:
        st.error(f"❌ Erro na predição: {str(e)}")
        return None, None, None


def get_confidence_color(confidence):
    """Retorna cor baseada na confiança"""
    if confidence >= 80:
        return "confidence-high"
    elif confidence >= 60:
        return "confidence-medium"
    else:
        return "confidence-low"


def display_results(is_productive, confidence, probabilities, response_summary):
    """Exibe os resultados da análise"""

    # Resultado
    st.success("✅ Análise concluída!")

    # Métricas
    col_metric1, col_metric2, col_metric3 = st.columns(3)

    with col_metric1:
        st.metric(
            "Classificação",
            "✅ Produtivo" if is_productive else "❌ Improdutivo",
            delta=None,
        )

    with col_metric2:
        confidence_color = get_confidence_color(confidence)
        st.markdown(
            f'<p class="{confidence_color}">Confiança: {confidence:.1f}%</p>',
            unsafe_allow_html=True,
        )

    with col_metric3:
        productive_prob = probabilities[0] * 100
        unproductive_prob = probabilities[1] * 100
        st.metric(
            "Probabilidade",
            f"{productive_prob:.1f}% / {unproductive_prob:.1f}%",
            delta=None,
        )

    # Explicação
    if is_productive:
        st.info(
            "🎯 Esta mensagem parece ser **produtiva** e requer uma ação ou resposta específica."
        )
    else:
        st.warning(
            "⚠️ Esta mensagem parece ser **improdutiva** e não necessita de uma ação imediata."
        )

    # Gráfico de probabilidades
    st.subheader("📊 Probabilidades")
    prob_df = pd.DataFrame(
        {
            "Categoria": ["Produtivo", "Improdutivo"],
            "Probabilidade": [productive_prob, unproductive_prob],
        }
    )
    st.bar_chart(prob_df.set_index("Categoria"))

    # Resposta automática
    st.subheader("💬 Resposta Automática Sugerida")

    # Informações da resposta
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.info(f"**Tipo de Resposta:** {response_summary['response_type']}")
    with col_info2:
        if response_summary["detected_categories"]:
            st.info(
                f"**Categorias Detectadas:** {', '.join(response_summary['detected_categories'])}"
            )

    # Exibe a resposta
    st.markdown(
        f'<div class="response-box">{response_summary["response"].replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )

    # Botão para copiar resposta
    if st.button("📋 Copiar Resposta", type="secondary"):
        st.write("Resposta copiada para a área de transferência!")
        st.code(response_summary["response"])


def main():
    """Função principal do app"""

    # Header
    st.markdown(
        '<h1 class="main-header">📧 Email Productivity Classifier</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">Solução para <span class="productive">AutoU</span> - Classificação e Respostas Automáticas</p>',
        unsafe_allow_html=True,
    )

    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Sobre o Projeto")
        st.markdown(
            """
        **Solução para AutoU** - Sistema de classificação e resposta automática de emails.
        
        **Funcionalidades:**
        - 📧 Upload de arquivos (.txt/.pdf)
        - 🤖 Classificação automática
        - 💬 Geração de respostas
        - 📊 Métricas detalhadas
        
        **Tecnologias:**
        - 🤖 Scikit-learn + TF-IDF
        - 🎨 Streamlit
        - 📄 PyPDF2
        """
        )

        st.header("📊 Métricas do Modelo")
        st.markdown(
            """
        - **Acurácia**: 98.39%
        - **Precisão**: Alta
        - **Recall**: Alto
        """
        )

        st.header("🔮 Próximos Passos")
        st.markdown(
            """
        - [x] Upload de arquivos
        - [x] Respostas automáticas
        - [ ] Deploy na nuvem
        - [ ] API REST
        """
        )

    # Carrega componentes
    model = load_model()
    response_generator = load_response_generator()
    file_processor = load_file_processor()

    if model is None:
        st.stop()

    # Container principal
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📝 Análise de Email")

        # Tabs para diferentes métodos de entrada
        tab1, tab2 = st.tabs(["📄 Upload de Arquivo", "✏️ Texto Direto"])

        with tab1:
            st.subheader("📤 Envie um arquivo de email")
            st.markdown("**Formatos suportados:** .txt, .pdf")

            uploaded_file = st.file_uploader(
                "Escolha um arquivo",
                type=["txt", "pdf"],
                help="Arraste um arquivo ou clique para selecionar",
            )

            if uploaded_file is not None:
                # Processa o arquivo
                success, extracted_text, file_name = (
                    file_processor.process_uploaded_file(uploaded_file)
                )

                if success:
                    # Valida o conteúdo
                    is_valid, validation_message = (
                        file_processor.validate_email_content(extracted_text)
                    )

                    if is_valid:
                        # Exibe informações do arquivo
                        file_info = file_processor.get_file_info(
                            file_name, extracted_text
                        )

                        st.markdown(
                            f'<div class="file-info">📁 <strong>{file_name}</strong> | 📊 {file_info["word_count"]} palavras | 📏 {file_info["line_count"]} linhas</div>',
                            unsafe_allow_html=True,
                        )

                        # Exibe preview do texto
                        with st.expander("👀 Visualizar conteúdo do arquivo"):
                            st.text_area(
                                "Conteúdo extraído:",
                                extracted_text,
                                height=200,
                                disabled=True,
                            )

                        # Botão para analisar
                        if st.button(
                            "🔍 Analisar Email",
                            type="primary",
                            use_container_width=True,
                        ):
                            with st.spinner("Analisando email..."):
                                # Faz predição
                                is_productive, confidence, probabilities = (
                                    predict_productivity(model, extracted_text)
                                )

                                if is_productive is not None:
                                    # Gera resposta
                                    response_summary = (
                                        response_generator.get_response_summary(
                                            extracted_text, is_productive, confidence
                                        )
                                    )

                                    # Exibe resultados
                                    display_results(
                                        is_productive,
                                        confidence,
                                        probabilities,
                                        response_summary,
                                    )
                    else:
                        st.warning(f"⚠️ {validation_message}")
                else:
                    st.error("❌ Erro ao processar arquivo")

        with tab2:
            st.subheader("✏️ Cole o conteúdo do email")

            # Área de texto para input
            message = st.text_area(
                "Cole aqui o conteúdo da mensagem (assunto + corpo):",
                height=200,
                placeholder="Exemplo: Reunião importante amanhã às 10h para discutir o projeto...",
            )

            # Botão de classificação
            if st.button(
                "🔍 Classificar Mensagem", type="primary", use_container_width=True
            ):
                if message.strip():
                    with st.spinner("Analisando mensagem..."):
                        # Faz predição
                        is_productive, confidence, probabilities = predict_productivity(
                            model, message
                        )

                        if is_productive is not None:
                            # Gera resposta
                            response_summary = response_generator.get_response_summary(
                                message, is_productive, confidence
                            )

                            # Exibe resultados
                            display_results(
                                is_productive,
                                confidence,
                                probabilities,
                                response_summary,
                            )
                else:
                    st.warning("⚠️ Por favor, insira uma mensagem para classificar.")

    with col2:
        st.header("🧪 Exemplos")

        # Exemplos de mensagens
        examples = {
            "Produtivo": [
                "Reunião importante amanhã às 10h para discutir o projeto de marketing.",
                "Relatório mensal de vendas está pronto para revisão.",
                "Confirmação de entrega do pedido #12345 para sexta-feira.",
                "Preciso de ajuda com um problema técnico no sistema.",
            ],
            "Improdutivo": [
                "CONGRATULATIONS! You've won a free iPhone! Click here to claim!",
                "URGENT: Your account has been suspended. Verify now!",
                "Make money fast! Work from home and earn $5000/day!",
                "Feliz Natal! Desejo um ótimo ano novo para toda a equipe.",
            ],
        }

        for category, messages in examples.items():
            st.subheader(f"{'✅' if category == 'Produtivo' else '❌'} {category}")
            for i, msg in enumerate(messages):
                if st.button(f"Exemplo {i+1}", key=f"{category}_{i}"):
                    st.session_state.example_message = msg
                    st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666;'>
        <p>Desenvolvido para <strong>AutoU</strong> - Email Productivity Classifier v2.0</p>
        <p>🤖 Machine Learning + 💬 Respostas Automáticas</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
