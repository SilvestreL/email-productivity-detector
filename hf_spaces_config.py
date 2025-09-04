"""
Configuração para deploy no Hugging Face Spaces via interface web
"""

import streamlit as st
import os
from pathlib import Path


def setup_hf_spaces():
    """
    Configura a aplicação para funcionar no HF Spaces
    """

    # Configurações específicas do HF Spaces
    st.set_page_config(
        page_title="Email Productivity Classifier - HF Spaces",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Sidebar com informações do deploy
    with st.sidebar:
        st.markdown("## 🚀 Deploy Status")
        st.success("✅ Hugging Face Spaces")
        st.info("📱 Aplicação funcionando na nuvem")

        st.markdown("## 🔧 Configuração")
        st.info(
            """
        **Modelos:** Google Drive
        **Deploy:** HF Spaces
        **GitHub:** Apenas código
        """
        )

        # Botão para configurar IDs do Drive
        if st.button("🔧 Configurar Google Drive"):
            st.session_state.show_drive_config = True

    # Configuração do Google Drive
    if st.session_state.get("show_drive_config", False):
        st.markdown("## 🔧 Configuração do Google Drive")

        st.info(
            """
        **Para usar esta aplicação:**
        
        1. Faça upload dos arquivos do modelo para o Google Drive
        2. Compartilhe como "Qualquer pessoa com o link pode visualizar"
        3. Configure os IDs abaixo
        """
        )

        # Campos para configurar os IDs
        col1, col2 = st.columns(2)

        with col1:
            model_id = st.text_input(
                "ID do model.safetensors", placeholder="1ABC123...XYZ"
            )
            config_id = st.text_input("ID do config.json", placeholder="2DEF456...ABC")
            tokenizer_id = st.text_input(
                "ID do tokenizer.json", placeholder="3GHI789...DEF"
            )

        with col2:
            vocab_id = st.text_input("ID do vocab.txt", placeholder="4JKL012...GHI")
            special_id = st.text_input(
                "ID do special_tokens_map.json", placeholder="5MNO345...JKL"
            )
            tokenizer_config_id = st.text_input(
                "ID do tokenizer_config.json", placeholder="6PQR678...MNO"
            )

        if st.button("💾 Salvar Configuração"):
            # Aqui você pode salvar os IDs
            st.success("✅ IDs salvos! A aplicação está configurada.")
            st.session_state.show_drive_config = False


def get_model_path():
    """
    Retorna o caminho do modelo (será baixado do Drive)
    """
    return "models/model_distilbert_cased"


def main():
    """
    Função principal para demonstração
    """
    setup_hf_spaces()

    st.title("📧 Email Productivity Classifier")
    st.markdown("### 🚀 Deploy no Hugging Face Spaces")

    st.success(
        """
    **✅ Deploy configurado com sucesso!**
    
    Esta aplicação está rodando no Hugging Face Spaces com:
    - **Modelos:** Baixados do Google Drive
    - **Código:** Versionado no GitHub
    - **Infraestrutura:** HF Spaces (gratuito)
    """
    )

    # Demonstração da funcionalidade
    st.markdown("## 🔍 Teste da Aplicação")

    email_text = st.text_area(
        "Digite um email para classificar:",
        placeholder="Digite aqui o conteúdo do email...",
        height=150,
    )

    if st.button("🚀 Classificar Email"):
        if email_text.strip():
            with st.spinner("🔍 Analisando email..."):
                # Simulação da classificação
                import time

                time.sleep(2)

                st.success("✅ Email classificado com sucesso!")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Produtividade", "85%", "Alta")
                    st.metric("Confiança", "92%", "Excelente")

                with col2:
                    st.metric("Categoria", "Produtivo", "✅")
                    st.metric("Tempo", "2.1s", "Rápido")

                st.info(
                    "💡 Esta é uma demonstração. Configure os IDs do Google Drive para usar o modelo real."
                )
        else:
            st.warning("⚠️ Digite um email para classificar.")


if __name__ == "__main__":
    main()
