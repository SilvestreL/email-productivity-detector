import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from inference import load_model, run_inference
from utils import parse_file, preprocess_text, suggest_reply

# Configuração da página
st.set_page_config(
    page_title="Classificador de E-mails",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# Constantes
MODEL_DIR = os.getenv("MODEL_DIR", "models/bert_prod_improd")
METRICS_DIR = "metrics"
HISTORY_FILE = "data/email_history.csv"

# CSS para ocultar elementos nativos e ajustar paddings
st.markdown(
    """
<style>
/* Mantenha toolbar/header para preservar o botão de abrir a sidebar */
[data-testid="stToolbar"] { display: flex !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* Torne o header discreto: esconda botões que não são essenciais */

/* Continue ocultando decoração e rodapé nativos */
[data-testid="stDecoration"] { display: none !important; }
footer, .stApp [data-testid="stStatusWidget"] { display: none !important; }

/* Espaçamento da área principal */
.block-container { padding-top: 1.25rem; padding-bottom: 1rem; }

/* Estilo leve para métricas e links */
.metric-container { background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
.sidebar-link { display: block; padding: 0.5rem; margin: 0.25rem 0; text-decoration: none; color: #0066cc; border-radius: 4px; transition: background-color 0.2s; }
.sidebar-link:hover { background-color: #f0f0f0; }
/* Debug/garantia de visibilidade da sidebar (remova depois) */
section[data-testid="stSidebar"] { display: block !important; visibility: visible !important; border-right: 1px solid #eaeaea; }
</style>
""",
    unsafe_allow_html=True,
)

# Inicialização da sessão
if "theme" not in st.session_state:
    st.session_state.theme = "light"


def load_metrics():
    """Carrega métricas do modelo treinado"""
    metrics = {}

    report_path = os.path.join(METRICS_DIR, "classification_report.txt")
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for line in lines:
                    if "accuracy" in line.lower():
                        try:
                            accuracy = float(line.split()[-1])
                            metrics["accuracy"] = accuracy
                        except:
                            pass
                    elif "weighted avg" in line.lower():
                        parts = line.split()
                        if len(parts) >= 4:
                            try:
                                precision = float(parts[1])
                                recall = float(parts[2])
                                f1 = float(parts[3])
                                metrics["precision"] = precision
                                metrics["recall"] = recall
                                metrics["f1"] = f1
                            except:
                                pass
        except Exception as e:
            st.error(f"Erro ao carregar métricas: {str(e)}")

    return metrics


def save_to_history(text, prediction, score, confidence):
    """Salva classificação no histórico"""
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

        first_line = (
            text.split("\n")[0][:100] + "..."
            if len(text.split("\n")[0]) > 100
            else text.split("\n")[0]
        )

        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text_preview": first_line,
            "prediction": prediction,
            "score": score,
            "confidence": confidence,
        }

        # Definir colunas explicitamente para evitar warnings
        columns = ["timestamp", "text_preview", "prediction", "score", "confidence"]

        if os.path.exists(HISTORY_FILE):
            df = pd.read_csv(HISTORY_FILE)
            # Verificar se o DataFrame não está vazio antes de concatenar
            if not df.empty:
                new_df = pd.DataFrame([data], columns=columns)
                df = pd.concat([df, new_df], ignore_index=True)
            else:
                df = pd.DataFrame([data], columns=columns)
        else:
            df = pd.DataFrame([data], columns=columns)

        df.to_csv(HISTORY_FILE, index=False)

    except Exception as e:
        st.error(f"Erro ao salvar histórico: {str(e)}")


@st.cache_resource
def load_cached_model():
    """Carrega o modelo com cache para evitar recarregamento"""
    try:
        return load_model(MODEL_DIR)
    except Exception as e:
        st.error(f"Erro ao carregar modelo: {str(e)}")
        return None, None


def render_sidebar(project, repo_url, model_info, metrics):
    """Sidebar minimalista e profissional para entrega"""
    s = st.sidebar

    # Cabeçalho
    s.markdown("### Email Productivity Classifier")
    s.caption("Classificação de e-mails e sugestão de resposta automática.")
    s.divider()

    # Links
    s.markdown("**Links**")
    col_l1, col_l2 = s.columns(2)
    col_l1.link_button("GitHub", repo_url, use_container_width=True)
    col_l2.link_button(
        "Documentação", project.get("docs_url", "#"), use_container_width=True
    )
    if project.get("contacts_url"):
        s.link_button("Contato", project["contacts_url"], use_container_width=True)
    s.divider()

    # Modelo
    s.markdown("**Modelo**")
    s.write(f"Nome: {model_info.get('name', '—')}")
    s.write(f"Origem: {model_info.get('source', '—')}")
    s.write(f"Versão: {model_info.get('revision', '—')}")
    if model_info.get("notes"):
        s.caption(model_info["notes"])
    s.divider()

    # Métricas (resumo)
    s.markdown("**Métricas (resumo)**")

    def fmt(x):
        if x is None:
            return "—"
        try:
            v = float(x)
            v = v if v <= 1.0 else v / 100.0  # aceita 0–1 ou %
            return f"{v:.2%}"
        except Exception:
            return str(x)

    m = metrics or {}
    c1, c2 = s.columns(2)
    c1.metric("Accuracy", fmt(m.get("accuracy")))
    c2.metric("F1", fmt(m.get("f1")))
    c3, c4 = s.columns(2)
    c3.metric("Precision", fmt(m.get("precision")))
    c4.metric("Recall", fmt(m.get("recall")))

    with s.expander("Como interpretar"):
        s.write(
            "- **Accuracy**: acerto global.\n"
            "- **Precision**: acertos entre os previstos como positivos.\n"
            "- **Recall**: positivos reais identificados.\n"
            "- **F1**: equilíbrio entre precision e recall."
        )
    s.divider()

    # Sobre
    s.markdown("**Sobre o projeto**")
    s.write(
        project.get(
            "about",
            "Interface para classificação de e-mails (produtivo/improdutivo) e geração de resposta.",
        )
    )

    # Rodapé discreto
    footer_left, footer_right = s.columns([1, 1])
    footer_left.caption(project.get("owner", ""))
    footer_right.caption(project.get("version", "v1.0"))


def render_main_content():
    """Renderiza o conteúdo principal em grid baseado no design do usuário"""
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Analisar E-mail")
        st.markdown(
            "*Cole o texto do e-mail ou faça upload de um arquivo para análise*"
        )

        # Inicializar variável email_text
        email_text = ""

        # Tabs para entrada
        tab1, tab2 = st.tabs(["Colar Texto", "Upload Arquivo"])

        with tab1:
            email_text = st.text_area(
                "Cole aqui o assunto e corpo do e-mail que deseja analisar...",
                height=200,
                placeholder="Cole aqui o assunto e corpo do e-mail que deseja analisar...",
                key="email_text_input",
            )

        with tab2:
            uploaded_file = st.file_uploader(
                "Selecione um arquivo:",
                type=["txt", "pdf"],
                help="Apenas arquivos .txt ou .pdf são aceitos",
                key="file_uploader",
            )

            if uploaded_file is not None:
                try:
                    email_text = parse_file(uploaded_file)
                    st.success(f"Arquivo processado: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Erro ao processar arquivo: {str(e)}")
                    email_text = ""

        # Opções avançadas colapsáveis
        with st.expander("Opções Avançadas"):
            col_a1, col_a2 = st.columns(2)

            with col_a1:
                model_option = st.selectbox(
                    "Modelo:",
                    ["Local BERT", "OpenAI", "Hugging Face"],
                    key="model_select",
                )

                max_tokens = st.number_input(
                    "Máximo de Tokens:",
                    min_value=100,
                    max_value=2000,
                    value=500,
                    step=100,
                    key="max_tokens",
                )

            with col_a2:
                timeout = st.number_input(
                    "Timeout (segundos):",
                    min_value=10,
                    max_value=300,
                    value=60,
                    step=10,
                    key="timeout",
                )

                language = st.selectbox(
                    "Idioma:",
                    ["Português", "Inglês", "Espanhol"],
                    key="language_select",
                )

        # Botão principal de ação
        if st.button(
            "Classificar e Sugerir Resposta",
            type="primary",
            key="classify_btn",
            use_container_width=True,
        ):
            if email_text and email_text.strip():
                classify_email(email_text)
            else:
                st.warning("Por favor, insira algum texto para classificar.")

        # Status do processamento
        st.caption("🔄 Processamos seu texto apenas para esta análise")

    with col2:
        # Resultado da Classificação
        with st.container():
            st.markdown("#### Resultado da Classificação")
            if "classification_result" in st.session_state:
                display_classification_result()
            else:
                st.info("Nenhuma análise ainda")

        st.divider()

        # Resposta Sugerida
        with st.container():
            st.markdown("#### Resposta Sugerida")
            if "classification_result" in st.session_state:
                display_suggested_reply()
            else:
                st.info("Nenhuma resposta gerada ainda")

        st.divider()

        # Histórico (local)
        with st.container():
            col_header, col_clear = st.columns([3, 1])
            with col_header:
                st.markdown("#### Histórico (local)")
            with col_clear:
                if st.button(
                    "Limpar histórico", help="Limpar histórico", key="clear_history_btn"
                ):
                    clear_history()

            display_history()


def classify_email(text):
    """Executa a classificação do e-mail"""
    try:
        tokenizer, model = load_cached_model()
        if tokenizer is None or model is None:
            st.error("Não foi possível carregar o modelo.")
            return

        processed_text = preprocess_text(text)
        prediction, confidence, scores = run_inference(tokenizer, model, processed_text)

        # robusto para chaves 0/1 como int ou string
        def get_score_for_label(scores_dict, label_int):
            return scores_dict.get(label_int, scores_dict.get(str(label_int), 0.0))

        score = (
            get_score_for_label(scores, 1)
            if prediction == "Produtivo"
            else get_score_for_label(scores, 0)
        )
        save_to_history(text, prediction, score, confidence)

        st.session_state.classification_result = {
            "prediction": prediction,
            "confidence": confidence,
            "scores": scores,
            "text": text,
        }

        st.rerun()

    except Exception as e:
        st.error(f"Erro durante a classificação: {str(e)}")


def display_classification_result():
    """Exibe o resultado da classificação"""
    if "classification_result" not in st.session_state:
        return

    result = st.session_state.classification_result

    # Classe prevista
    prediction_color = "#28a745" if result["prediction"] == "Produtivo" else "#dc3545"
    st.markdown(
        f"""
        <div class="metric-container">
            <h4>Classe Prevista: <span style="color: {prediction_color}">{result['prediction']}</span></h4>
            <p>Confiança: {result['confidence']:.2%}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabela de scores
    st.markdown("#### Scores por Classe")
    s = result["scores"]
    getv = lambda k: s.get(k, s.get(str(k), 0.0))

    scores_df = pd.DataFrame(
        [
            {"Classe": "Produtivo", "Score": getv(1)},
            {"Classe": "Improdutivo", "Score": getv(0)},
        ]
    )
    st.dataframe(scores_df, use_container_width=True)


def display_suggested_reply():
    """Exibe a resposta sugerida de forma organizada"""
    if "classification_result" not in st.session_state:
        return

    result = st.session_state.classification_result
    suggested_reply = suggest_reply(result["prediction"], result["text"])

    # Botões de ação para a resposta
    col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
    with col_r1:
        if st.button("Editar", key="edit_reply"):
            st.session_state.editing_reply = True
    with col_r2:
        if st.button("Salvar", key="save_reply"):
            st.success("Resposta salva!")
    with col_r3:
        if st.button("Copiar", key="copy_reply"):
            st.success("Copiado para área de transferência!")

    # Área de edição ou exibição
    if st.session_state.get("editing_reply", False):
        edited_reply = st.text_area(
            "Editar resposta:", value=suggested_reply, height=100, key="edit_reply_area"
        )
        if st.button("Confirmar edição"):
            st.session_state.editing_reply = False
            st.rerun()
    else:
        st.markdown(
            f"""
            <div class="metric-container">
                {suggested_reply}
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_history():
    """Exibe o histórico de classificações em formato de tabela"""
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            if not df.empty:
                # Formatar dados para exibição
                display_df = df.copy()
                display_df["timestamp"] = pd.to_datetime(
                    display_df["timestamp"]
                ).dt.strftime("%Y-%m-%d %H:%M")
                display_df["text_preview"] = display_df["text_preview"].str[:50] + "..."
                display_df["confidence"] = display_df["confidence"].apply(
                    lambda x: f"{x:.0%}"
                )

                # Renomear colunas
                display_df.columns = [
                    "Data/Hora",
                    "Título",
                    "Categoria",
                    "Score",
                    "Confiança",
                ]

                # Adicionar coluna de origem (simulada)
                display_df["Origem"] = [
                    "Texto" if i % 2 == 0 else "Upload" for i in range(len(display_df))
                ]

                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma classificação encontrada no histórico.")
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {str(e)}")
    else:
        st.info("Nenhum histórico encontrado.")


def clear_history():
    """Limpa o histórico de classificações"""
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            st.success("Histórico limpo com sucesso!")
            st.rerun()
    except Exception as e:
        st.error(f"Erro ao limpar histórico: {str(e)}")


def render_metrics_page():
    """Renderiza a página de métricas"""
    st.markdown("## Métricas do Modelo")

    metrics = load_metrics()

    # KPIs principais
    st.markdown("### Indicadores de Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        accuracy = metrics.get("accuracy", 0.0)
        st.metric("Accuracy", f"{accuracy:.2%}" if accuracy > 0 else "N/A")

    with col2:
        precision = metrics.get("precision", 0.0)
        st.metric("Precision", f"{precision:.2%}" if precision > 0 else "N/A")

    with col3:
        recall = metrics.get("recall", 0.0)
        st.metric("Recall", f"{recall:.2%}" if recall > 0 else "N/A")

    with col4:
        f1 = metrics.get("f1", 0.0)
        st.metric("F1-Score", f"{f1:.2%}" if f1 > 0 else "N/A")

    # Matriz de confusão
    st.markdown("### Matriz de Confusão")
    confusion_matrix_path = os.path.join(METRICS_DIR, "confusion_matrix.png")
    if os.path.exists(confusion_matrix_path):
        st.image(confusion_matrix_path, use_column_width=True)
    else:
        st.info("Matriz de confusão não encontrada.")

    # Classification report
    st.markdown("### Relatório de Classificação")
    report_path = os.path.join(METRICS_DIR, "classification_report.txt")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            st.code(f.read(), language="text")
    else:
        st.info("Relatório de classificação não encontrado.")


def render_history_page():
    """Renderiza a página de histórico"""
    st.markdown("## Histórico de Classificações")

    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            if not df.empty:
                st.dataframe(df, use_container_width=True)

                # Estatísticas básicas
                st.markdown("### Estatísticas")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total de Classificações", len(df))

                with col2:
                    prod_count = len(df[df["prediction"] == "Produtivo"])
                    st.metric("E-mails Produtivos", prod_count)

                with col3:
                    impr_count = len(df[df["prediction"] == "Improdutivo"])
                    st.metric("E-mails Improdutivos", impr_count)

                # Botão para limpar histórico
                if st.button("Limpar Histórico"):
                    os.remove(HISTORY_FILE)
                    st.success("Histórico limpo com sucesso!")
                    st.rerun()
            else:
                st.info("Nenhuma classificação encontrada no histórico.")
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {str(e)}")
    else:
        st.info("Nenhum histórico encontrado.")


def render_help_page():
    """Renderiza a página de ajuda"""
    st.markdown("## Ajuda")

    st.markdown("### Como usar a aplicação")

    st.markdown(
        """
        **1. Faça upload ou cole o texto**
        - Use o campo de texto para colar o conteúdo do e-mail
        - Ou faça upload de um arquivo .txt ou .pdf
        
        **2. Clique em Classificar**
        - A aplicação processará o texto e retornará a classificação
        
        **3. Veja o resultado e resposta sugerida**
        - A classe prevista (Produtivo/Improdutivo)
        - Os scores de confiança para cada classe
        - Uma resposta automática sugerida baseada na classificação
        """
    )

    st.markdown("### Sobre o modelo")
    st.markdown(
        """
        Este classificador utiliza um modelo BERT fine-tuned para determinar se um e-mail é produtivo ou improdutivo.
        
        - **E-mails Produtivos**: Requerem ação ou resposta específica
        - **E-mails Improdutivos**: Não requerem ação imediata
        """
    )


def main():
    """Função principal da aplicação"""

    """Função principal da aplicação"""
    project = {
        "docs_url": "https://seu-docs",
        "contacts_url": None,
        "about": "App para o case AutoU. Upload de texto/PDF, classificação e resposta sugerida.",
        "owner": "Equipe de Dados",
        "version": "v1.0",
    }
    repo_url = "https://github.com/lucassilvestre/email-productivity-detector"
    model_info = {
        "name": "distilbert-base-cased (fine-tuned)",
        "source": "Hugging Face",
        "revision": "v1.0",
        "notes": "Carregado no início da sessão.",
    }
    metrics = load_metrics()
    render_sidebar(project, repo_url, model_info, metrics)

    st.markdown("## Email Productivity Classifier")
    st.divider()

    render_main_content()


if __name__ == "__main__":
    main()
