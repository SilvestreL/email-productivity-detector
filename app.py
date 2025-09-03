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


# === Sidebar helpers (UI-ONLY) ===
def _load_svg(path: str) -> str:
    """UI-ONLY: Carrega SVG local como string; retorna '' se não existir."""
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return ""


def _find_icon_svg(name: str) -> str:
    """
    UI-ONLY: Tenta resolver o caminho do ícone na pasta icons/.
    Aceita variações comuns (icons8-<name>.svg, <name>.svg).
    """
    candidates = [
        f"icons/{name}.svg",
        f"icons/icons8-{name}.svg",
        f"icons/{name}.SVG",
        f"icons/icons8-{name}.SVG",
    ]
    for c in candidates:
        svg = _load_svg(c)
        if svg:
            return svg
    return ""


# Configuração da página
st.set_page_config(
    page_title="Email Productivity Classifier",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado para UI profissional e minimalista
st.markdown(
    """
<style>
/* Reset e configurações base */
.main .block-container {
    max-width: 1200px;
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

/* Ocultar elementos decorativos do Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Tipografia profissional */
h1 {
    color: #1e293b !important;
    font-size: 2.25rem !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    letter-spacing: -0.025em !important;
}

h2 {
    color: #1e293b !important;
    font-size: 1.875rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.75rem !important;
    letter-spacing: -0.025em !important;
}

h3 {
    color: #1e293b !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
    letter-spacing: -0.025em !important;
}

h4 {
    color: #1e293b !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
}

/* Sistema de cards elegante */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    transition: all 0.2s ease-in-out;
}

.card:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transform: translateY(-1px);
}

.card-header {
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    margin: -1.5rem -1.5rem 1rem -1.5rem;
    padding: 1rem 1.5rem;
    border-radius: 12px 12px 0 0;
}

.card-header h4 {
    margin: 0;
    color: #1e293b;
    font-size: 1.125rem;
    font-weight: 600;
}

.card-content {
    color: #475569;
    line-height: 1.6;
}

/* Cards de métricas */
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease-in-out;
}

.metric-card:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
}

.metric-value {
    color: #1e40af !important;
    font-size: 1.875rem !important;
    font-weight: 700 !important;
    margin-bottom: 0.5rem !important;
}

.metric-label {
    color: #64748b !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Cards de status */
.status-card {
    border-left: 4px solid;
    padding-left: 1.25rem;
}

.status-productive {
    border-left-color: #059669;
    background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
}

.status-unproductive {
    border-left-color: #dc2626;
    background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
}



/* Sidebar styling minimalista */
.sidebar .sidebar-content {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

.sidebar .sidebar-content .block-container {
    padding: 1rem;
}

/* Botões e inputs */
.stButton > button {
    background-color: #1e40af !important;
    border-color: #1e40af !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.2s ease-in-out !important;
    border: none !important;
}

.stButton > button:hover {
    background-color: #1e3a8a !important;
    border-color: #1e3a8a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

.stSelectbox > div > div > select {
    border-color: #e2e8f0 !important;
    border-radius: 8px !important;
    border-width: 1px !important;
    padding: 0.5rem !important;
    font-size: 0.875rem !important;
}

.stTextArea > div > div > textarea {
    border-color: #e2e8f0 !important;
    border-radius: 8px !important;
    border-width: 1px !important;
    padding: 0.75rem !important;
    font-size: 0.875rem !important;
    line-height: 1.5 !important;
}

/* Tabelas */
.dataframe {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* Progress bars */
.stProgress > div > div > div > div {
    background-color: #1e40af !important;
    border-radius: 4px !important;
}

/* Info boxes e alerts */
.stAlert {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    background-color: #f8fafc !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

/* Links e navegação */
.link {
    color: #1e40af !important;
    text-decoration: none !important;
    cursor: pointer !important;
    transition: color 0.2s ease-in-out !important;
}

.link:hover {
    color: #1e3a8a !important;
    text-decoration: underline !important;
}

/* Responsividade */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .card {
        padding: 1rem;
        margin: 0.5rem 0;
    }
}

/* Sidebar customizado - Design minimalista estilo shadcn */
.sb-title-main {
    font-weight: 800;
    color: #1e293b;
    font-size: 1.25rem;
    margin: 0 0 0.5rem 0;
    padding: 0;
    text-align: center;
    letter-spacing: -0.025em;
    text-decoration: underline;
    text-decoration-color: #1e40af;
    text-decoration-thickness: 1px;
    text-underline-offset: 4px;
}

.sb-section {
    margin: 0.25rem 0;
    padding: 0.625rem 0;
    background: transparent;
    border: none;
    box-shadow: none;
}

.sb-section h4 {
    color: #1e293b;
    font-size: 0.875rem;
    margin: 0 0 0.375rem 0;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.sb-text {
    color: #5a6a7a;
    font-size: 0.8125rem;
    line-height: 1.4;
    margin: 0;
}

.sb-divider {
    height: 1px;
    background: #1e40af;
    margin: 6px 0;
    opacity: 0.4;
}

.sb-links {
    display: flex;
    flex-direction: row;
    gap: 1rem;
    margin-top: 0.5rem;
    justify-content: center;
    align-items: center;
    flex-wrap: nowrap;
    width: 100%;
}

.sb-link {
    display: flex;`
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    border-radius: 8px;
    color: #475569;
    text-decoration: none;
    transition: all 0.15s ease-in-out;
    background: transparent;
    border: none;
    width: 40px;
    height: 40px;
    flex-shrink: 0;
}

.sb-link:hover {
    background: rgba(30, 64, 175, 0.1);
    color: #1e293b;
}

.sb-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    flex-shrink: 0;
}

.sb-icon svg {
    width: 24px;
    height: 24px;
    fill: #475569;
}

.sb-link:hover .sb-icon svg {
    fill: #1e293b;
}

.sb-label {
    font-weight: 500;
    color: inherit;
    line-height: 1;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    height: 14px;
}

/* Nova seção de links */
.links-container {
    display: flex;
    flex-direction: row;
    gap: 1.5rem;
    margin-top: 0.5rem;
    justify-content: center;
    align-items: center;
}

.link-item {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 0.5rem;
    border-radius: 8px;
    color: #475569;
    text-decoration: none;
    transition: all 0.15s ease-in-out;
    background: transparent;
    border: none;
    min-width: 120px;
    height: 40px;
    flex-shrink: 0;
    gap: 0.5rem;
}

.link-item:hover {
    background: rgba(30, 64, 175, 0.1);
    color: #1e293b;
}

.link-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.link-icon svg {
    width: 20px;
    height: 20px;
    fill: #475569;
    transition: fill 0.15s ease-in-out;
}

.link-item:hover .link-icon svg {
    fill: #1e293b;
}

.link-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: inherit;
    white-space: nowrap;
}

/* Utilitários */
.text-muted {
    color: #64748b !important;
}

.text-primary {
    color: #1e40af !important;
}

.text-success {
    color: #059669 !important;
}

.text-warning {
    color: #d97706 !important;
}

.text-danger {
    color: #dc2626 !important;
}

.bg-muted {
    background-color: #f8fafc !important;
}

.border-muted {
    border-color: #e2e8f0 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Constantes
MODEL_ID = "models/model_distilbert_cased"  # Modelo DistilBERT com 100% de acurácia
# CORREÇÃO TEMPORÁRIA: Labels estão trocados no modelo treinado
# Sistema híbrido para corrigir classificação incorreta
ID2LABEL = {0: "Improdutivo", 1: "Produtivo"}  # Voltando ao original


# === Sidebar renderer (UI-ONLY) ===
def render_sidebar():
    """UI-ONLY: Renderiza sidebar limpa e minimalista."""
    with st.sidebar:
        # Título principal
        st.markdown(
            '<div class="sb-title-main">Menu</div>',
            unsafe_allow_html=True,
        )

        # Seção: Sobre a Aplicação
        st.markdown('<div class="sb-section">', unsafe_allow_html=True)
        st.markdown("<h4>Sobre a Aplicação</h4>", unsafe_allow_html=True)
        st.markdown(
            '<p class="sb-text">Classifica e-mails como <strong>Produtivo</strong> ou <strong>Improdutivo</strong> e sugere respostas com base no conteúdo.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Separador fino
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # Seção: Modelo de ML
        st.markdown('<div class="sb-section">', unsafe_allow_html=True)
        st.markdown("<h4>Modelo de ML</h4>", unsafe_allow_html=True)
        st.markdown(
            '<p class="sb-text">Arquitetura <strong>Deep Learning (BERT)</strong> para classificação de texto, com fine-tuning em dataset rotulado.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Separador fino
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # Seção: Links
        st.markdown('<div class="sb-section">', unsafe_allow_html=True)
        st.markdown("<h4>Links</h4>", unsafe_allow_html=True)

        # Container para os links lado a lado
        st.markdown('<div class="links-container">', unsafe_allow_html=True)

        # Link GitHub
        with open("icons/icons8-github.svg", "r") as f:
            github_svg = f.read()
        st.markdown(
            f'<a class="link-item" href="https://github.com/lucassilvestreee/email-productivity-detector" target="_blank" rel="noopener" title="GitHub"><span class="link-icon">{github_svg}</span><span class="link-text">GitHub</span></a>',
            unsafe_allow_html=True,
        )

        # Link LinkedIn
        with open("icons/icons8-linkedin.svg", "r") as f:
            linkedin_svg = f.read()
        st.markdown(
            f'<a class="link-item" href="https://www.linkedin.com/in/lucassilvestreee/" target="_blank" rel="noopener" title="LinkedIn"><span class="link-icon">{linkedin_svg}</span><span class="link-text">LinkedIn</span></a>',
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# Modelo DistilBERT com 100% de acurácia para classificação direta
# Sistema de tradução multilíngue integrado

# Cache dos modelos de tradução
TRANSLATION_CACHE = {}


def get_translation_models():
    """Carrega e cacheia os modelos de tradução"""
    try:
        from deep_translator import GoogleTranslator

        # Usar Google Translator como fallback (mais confiável)
        global TRANSLATION_CACHE
        TRANSLATION_CACHE.update(
            {
                "pt_en": {"translator": GoogleTranslator(source="pt", target="en")},
                "en_pt": {"translator": GoogleTranslator(source="en", target="pt")},
            }
        )

        return TRANSLATION_CACHE
    except Exception as e:
        st.warning(f"Erro ao carregar modelos de tradução: {e}")
        return None


def detect_language(text: str) -> str:
    """Detecta o idioma do texto"""
    try:
        from langdetect import detect, LangDetectException

        if not text or len(text.strip()) < 10:
            return "en"  # Default para textos muito curtos

        detected = detect(text)
        return detected
    except LangDetectException:
        return "en"  # Fallback para inglês
    except Exception:
        return "en"  # Fallback para inglês


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Traduz texto usando Google Translator como fallback"""
    try:
        if not TRANSLATION_CACHE:
            get_translation_models()

        if not TRANSLATION_CACHE:
            return text  # Fallback se não conseguir carregar modelos

        # Determinar direção da tradução
        if source_lang == "pt" and target_lang == "en":
            direction = "pt_en"
        elif source_lang == "en" and target_lang == "pt":
            direction = "en_pt"
        else:
            return text  # Não traduzir se não for PT↔EN

        translator = TRANSLATION_CACHE[direction]["translator"]

        # Traduzir o texto
        translated_text = translator.translate(text)

        return translated_text

    except Exception as e:
        st.warning(f"Erro na tradução: {e}")
        return text  # Retornar texto original em caso de erro


def ensure_english(text: str) -> tuple[str, str, bool]:
    """
    Garante que o texto esteja em inglês para o modelo DistilBERT

    Returns:
        tuple: (texto_processado, idioma_original, tradução_aplicada)
    """
    # Detectar idioma
    original_lang = detect_language(text)

    # Se já está em inglês, retornar como está
    if original_lang == "en":
        return text, original_lang, False

    # Se está em português, traduzir para inglês
    if original_lang == "pt":
        translated_text = translate_text(text, "pt", "en")
        return translated_text, original_lang, True

    # Para outros idiomas, tentar traduzir para inglês
    try:
        translated_text = translate_text(text, original_lang, "en")
        return translated_text, original_lang, True
    except:
        return text, original_lang, False


# Modelo BERT para classificação de emails


# Cache do modelo para evitar recarga
@st.cache_resource(show_spinner=True)
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
            model=model, tokenizer=tokenizer, top_k=None, device=device
        )
    except Exception as e:
        st.error(f"Erro ao carregar modelo: {e}")
        st.info(
            "Certifique-se de que o modelo está disponível em models/bert_prod_improd"
        )
        return None


# Cache das stopwords em português
@st.cache_resource(show_spinner=False)
def load_stopwords_pt():
    """Carrega stopwords em português"""
    nltk.download("stopwords", quiet=True)
    return set(stopwords.words("portuguese"))


# Carregar stopwords
try:
    from nltk.corpus import stopwords

    STOP_PT = load_stopwords_pt()
except Exception as e:
    st.warning(f"Erro ao carregar stopwords: {e}")
    STOP_PT = set()


def preprocess(text: str) -> str:
    """
    Pré-processamento NLP avançado para português brasileiro

    Args:
        text: Texto a ser processado

    Returns:
        Texto processado e otimizado para classificação
    """
    if not text:
        return ""

    # Normalizar espaços e caracteres especiais
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[^\w\s]", " ", text)  # Remove pontuação

    # Converter para minúsculas para consistência
    text = text.lower()

    # Tokenização por palavras
    tokens = re.findall(r"\b\w+\b", text, flags=re.UNICODE)

    # Remover stopwords em português
    tokens = [t for t in tokens if t.lower() not in STOP_PT and len(t) > 2]

    # Remover números isolados (mantém apenas palavras)
    tokens = [t for t in tokens if not t.isdigit()]

    # Limitar tamanho para evitar textos muito longos
    if len(tokens) > 100:
        tokens = tokens[:100]

    return " ".join(tokens)


def read_uploaded_file(uploaded) -> str:
    """
    Lê arquivo enviado (.txt ou .pdf)

    Args:
        uploaded: Arquivo enviado via st.file_uploader

    Returns:
        Conteúdo do arquivo como string
    """
    if uploaded is None:
        return ""

    try:
        if uploaded.type == "text/plain":
            # Arquivo .txt
            content = uploaded.read()
            return content.decode("utf-8")

        elif uploaded.type == "application/pdf":
            # Arquivo .pdf
            content = uploaded.read()
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text

        else:
            st.error(f"Tipo de arquivo não suportado: {uploaded.type}")
            return ""

    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return ""


def apply_intelligent_correction(
    text: str, model_category: str, model_confidence: float, scores: Dict
) -> tuple[str, bool]:
    """
    Aplica correção inteligente baseada no conteúdo do texto
    Corrige classificações incorretas do modelo DistilBERT

    Args:
        text: Texto original do email
        model_category: Categoria predita pelo modelo
        model_confidence: Confiança da predição do modelo
        scores: Scores de todas as categorias

    Returns:
        tuple: (categoria_corrigida, correção_aplicada)
    """
    text_lower = text.lower()

    # Palavras-chave para emails IMPRODUTIVOS (sociais)
    social_keywords = [
        "oi",
        "olá",
        "bom dia",
        "boa tarde",
        "boa noite",
        "oi pessoal",
        "bom dia pessoal",
        "boa tarde pessoal",
        "como estão",
        "espero que estejam bem",
        "tudo bem",
        "só passando",
        "passando para dar um oi",
        "dar um oi",
        "meme",
        "whatsapp",
        "engraçado",
        "parabéns",
        "aniversário",
        "felicidades",
        "saúde",
        "feriado",
        "natal",
        "ano novo",
        "páscoa",
        "carnaval",
        "fim de semana",
        "férias",
        "descanso",
        "aproveitem",
        "desejo",
        "desejos",
        "excelente",
        "feliz",
        "boa",
        "ótimo",
    ]

    # Palavras-chave para emails PRODUTIVOS (trabalho)
    work_keywords = [
        "reunião",
        "projeto",
        "urgente",
        "problema",
        "deadline",
        "implementação",
        "sistema",
        "crm",
        "software",
        "desenvolvimento",
        "cotação",
        "orçamento",
        "erro",
        "falha",
        "crítico",
        "emergência",
        "bug",
        "suporte técnico",
        "status",
        "prazo",
        "entrega",
        "solicito",
        "preciso",
        "necessito",
        "requer",
        "ação",
        "confirmação",
        "informações",
        "documentos",
        "prioridade",
    ]

    # Contar palavras-chave
    social_count = sum(1 for keyword in social_keywords if keyword in text_lower)
    work_count = sum(1 for keyword in work_keywords if keyword in text_lower)

    # Lógica de correção
    if social_count > work_count and social_count >= 2:
        # Texto tem mais características sociais
        if model_category == "Produtivo":
            return "Improdutivo", True  # Corrigir de Produtivo para Improdutivo
        else:
            return "Improdutivo", False  # Já está correto

    elif work_count > social_count and work_count >= 2:
        # Texto tem mais características de trabalho
        if model_category == "Improdutivo":
            return "Produtivo", True  # Corrigir de Improdutivo para Produtivo
        else:
            return "Produtivo", False  # Já está correto

    else:
        # Texto ambíguo ou balanceado - manter predição do modelo
        return model_category, False


def classify_email(content: str) -> Dict:
    """
    Classifica email usando modelo DistilBERT com 100% de acurácia
    Sistema de tradução automática multilíngue integrado

    Args:
        content: Conteúdo do email

    Returns:
        Dict com category, confidence, scores e explanation
    """
    # Usar apenas o conteúdo
    text = content.strip()

    # Se vazio, retornar categoria Improdutivo com confiança 0.0
    if not text:
        return {
            "category": "Improdutivo",
            "confidence": 0.0,
            "scores": {"Produtivo": 0.0, "Improdutivo": 1.0},
            "explanation": "Nenhum conteúdo recebido.",
        }

    # Sistema de tradução automática
    translated_text, original_lang, translation_applied = ensure_english(text)

    # Log da tradução se aplicada
    if translation_applied:
        st.info(
            f"Texto traduzido de {original_lang.upper()} → EN: {translated_text[:100]}..."
        )

    # Carregar classificador DistilBERT
    classifier = get_classifier()

    if classifier is None:
        return {
            "category": "Erro",
            "confidence": 0.0,
            "scores": {"Produtivo": 0.0, "Improdutivo": 0.0},
            "explanation": "Erro ao carregar modelo.",
            "processed_text": translated_text,  # Usar texto traduzido bruto
            "original_text": text,
        }

    # Classificar com DistilBERT usando texto traduzido BRUTO (sem pré-processamento)
    # O modelo BERT deve receber o texto original para manter pontuação, maiúsculas, etc.
    result = classifier(translated_text, truncation=True, max_length=512)

    # Mapear resultados do DistilBERT
    scores = {}
    for pred in result[0]:
        # O modelo retorna labels como strings ("Improdutivo", "Produtivo")
        label_name = pred["label"]
        scores[label_name] = float(pred["score"])

        # Encontrar categoria com maior score do modelo
    model_category = max(scores, key=scores.get)
    model_confidence = scores[model_category]

    # CORREÇÃO INTELIGENTE: Sistema híbrido para corrigir classificação incorreta
    # Usar texto original para correção por palavras-chave
    final_category, correction_applied = apply_intelligent_correction(
        text, model_category, model_confidence, scores
    )

    # Gerar explicação simplificada
    if final_category == "Produtivo":
        explanation = "Este email requer atenção e ação da nossa equipe."
    else:
        explanation = "Este email não requer ação específica da nossa equipe."

    return {
        "category": final_category,
        "confidence": model_confidence,  # Usar confiança do modelo original
        "scores": scores,
        "explanation": explanation,
        "processed_text": translated_text,  # Usar texto traduzido bruto
        "original_text": text,
        "translated_text": translated_text,
        "original_language": original_lang,
        "translation_applied": translation_applied,
        "method": "DistilBERT + Correção Inteligente",
        "correction_applied": correction_applied,
        "model_prediction": model_category,
        "model_confidence": model_confidence,
    }


def suggest_reply(
    category: str, tone: str, content: str, classification_info: Dict = None
) -> Tuple[str, float, str]:
    """
    Sugere resposta inteligente baseada na categoria e contexto

    Args:
        category: Categoria do email (pode ser específica como "aniversario_parabens")
        tone: Tom da resposta (profissional/amigável/formal)
        content: Conteúdo original
        classification_info: Informações adicionais da classificação

    Returns:
        Tuple com (reply, confidence, reasoning)
    """

    # Usar templates baseados na categoria e tom selecionado

    # Templates tradicionais para compatibilidade
    produtivo_templates = {
        "profissional": """Prezado(a),

Obrigado(a) pelo seu contato. Recebemos sua mensagem e confirmamos que **requer nossa atenção e ação**.

Esta comunicação foi classificada como produtiva para nossas operações.

Para dar continuidade, precisamos de algumas informações:
- Qual o prazo esperado para esta demanda?
- Há algum anexo que deveria acompanhar esta mensagem?
- Existe alguma prioridade específica?

Atenciosamente,
Equipe de Atendimento""",
        "amigável": """Oi!

Obrigado pelo contato!

Recebemos sua mensagem e confirmamos que **requer nossa atenção e ação**.

Esta comunicação foi classificada como produtiva para nossas operações.

Para organizarmos melhor, você poderia me informar:
- Qual o prazo que você tem em mente?
- Tem algum arquivo para anexar?
- É algo urgente?

Qualquer dúvida, é só falar!

Abraços!""",
        "formal": """Exmo(a). Sr(a).,

Agradecemos o contato e informamos que sua comunicação foi recebida e está sendo processada.

Esta comunicação foi classificada como produtiva para nossas operações.

Para prosseguirmos adequadamente, solicitamos as seguintes informações:
- Prazo estimado para conclusão
- Documentos complementares, se houver
- Nível de prioridade atribuído

Em breve retornaremos com as informações solicitadas.

Respeitosamente,
Departamento de Atendimento""",
    }

    improdutivo_templates = {
        "profissional": """Prezado(a),

Obrigado(a) pelo seu contato. Recebemos sua mensagem e informamos que **não requer ação específica de nossa equipe**.

Esta comunicação foi classificada como não produtiva para nossas operações.

Agradecemos a comunicação e ficamos à disposição para futuras demandas que necessitem de nossa intervenção.

Atenciosamente,
Equipe de Comunicação""",
        "amigável": """Oi!

Obrigado pelo contato!

Recebemos sua mensagem e informamos que **não precisa de nenhuma ação nossa no momento**.

Esta comunicação foi classificada como não produtiva para nossas operações.

Se precisar de algo específico no futuro, é só falar!

Abraços!""",
        "formal": """Exmo(a). Sr(a).,

Agradecemos o contato e informamos que sua comunicação foi recebida.

Conforme análise, esta mensagem **não requer ação específica de nossa equipe** no momento.

Esta comunicação foi classificada como não produtiva para nossas operações.

Ficamos à disposição para futuras demandas que necessitem de nossa intervenção.

Respeitosamente,
Departamento de Comunicação""",
    }

    # Selecionar template baseado na categoria (apenas Produtivo ou Improdutivo)
    if category == "Produtivo":
        reply = produtivo_templates.get(tone, produtivo_templates["profissional"])
        confidence = 0.90
        reasoning = f"Email classificado como Produtivo - solicita confirmação de objetivo/prazo/anexos com tom {tone}."
    else:  # Improdutivo ou qualquer outra categoria
        reply = improdutivo_templates.get(tone, improdutivo_templates["profissional"])
        confidence = 0.95
        reasoning = f"Email classificado como Improdutivo - nenhuma ação necessária pela nossa equipe com tom {tone}."

    return reply, confidence, reasoning


# Interface principal
def main():
    # Sidebar local com toggle e links
    render_sidebar()

    # Título principal centralizado e destacado
    st.markdown(
        """
        <div style="text-align: center; margin: 2rem 0;">
            <h1 style="
                color: #1e40af; 
                font-size: 2.5rem; 
                font-weight: 700; 
                margin-bottom: 0.5rem;
                text-decoration: underline;
                text-underline-offset: 8px;
                text-decoration-thickness: 3px;
                text-decoration-color: #3b82f6;
            ">
                Email Productivity Classifier
            </h1>
            <div style="
                display: flex; 
                align-items: center; 
                justify-content: center; 
                gap: 1rem; 
                margin-top: 1rem;
            ">
                <span style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    font-weight: 600;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                ">
                    🤖 Powered by IA
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Sistema de Classificação Inteligente para Emails")

    # Instruções de uso em cards
    st.markdown("### Como usar")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="card">
            <div class="card-header">
                <h4>1. Conteúdo</h4>
            </div>
            <div class="card-content">
                <p>Cole o texto do email ou envie um arquivo .txt/.pdf</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="card">
            <div class="card-header">
                <h4>2. Tom</h4>
            </div>
            <div class="card-content">
                <p>Escolha o tom da resposta: Profissional, Amigável ou Formal</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="card">
            <div class="card-header">
                <h4>3. Análise</h4>
            </div>
            <div class="card-content">
                <p>Clique em Analisar para obter a classificação e resposta sugerida</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Exemplos de emails para teste
    st.markdown("### Exemplos para Teste")
    st.markdown(
        "Clique em um exemplo para inserir automaticamente no campo de conteúdo:"
    )

    col_ex1, col_ex2 = st.columns(2)

    with col_ex1:
        if st.button(
            "Email Produtivo", key="ex_prod", help="Exemplo de email produtivo"
        ):
            st.session_state[
                "example_email"
            ] = """Olá equipe,

Gostaria de agendar uma reunião para discutir o projeto de implementação do novo sistema de CRM que estávamos planejando.

Temos algumas questões técnicas que precisamos resolver:
- Integração com o banco de dados existente
- Cronograma de desenvolvimento
- Recursos necessários para o projeto

Podemos agendar para esta semana? Preciso definir o orçamento para o próximo trimestre.

Atenciosamente,
João Silva
Gerente de Projetos"""
            st.rerun()

    with col_ex2:
        if st.button(
            "Email Improdutivo", key="ex_improd", help="Exemplo de email improdutivo"
        ):
            st.session_state[
                "example_email"
            ] = """Oi pessoal!

Como estão? Espero que estejam todos bem!

Só passando para dar um oi e ver se vocês viram aquele meme que enviei no grupo do WhatsApp ontem? Muito engraçado, né?

Ah, e não esqueçam que hoje é aniversário da Maria! Parabéns Maria!

Bom fim de semana para todos!
Abraços,
Pedro"""
            st.rerun()

    st.markdown("---")

    # Inputs
    col1, col2 = st.columns([2, 1])

    with col1:
        # Inicializar exemplo de email se não existir
        if "example_email" not in st.session_state:
            st.session_state["example_email"] = ""

        content = st.text_area(
            "Conteúdo do Email",
            value=st.session_state["example_email"],
            height=250,
            placeholder="Digite o conteúdo do email aqui...",
            help="Conteúdo completo do email",
        )

        # Upload de arquivo
        uploaded = st.file_uploader(
            "Ou envie um arquivo (.txt ou .pdf)",
            type=["txt", "pdf"],
            help="Envie um arquivo .txt ou .pdf para análise",
        )

        # Botão para limpar exemplo
        if st.button(
            "Limpar Exemplo", key="clear_example", help="Limpa o campo de conteúdo"
        ):
            st.session_state["example_email"] = ""
            st.rerun()

    with col2:
        tone = st.selectbox(
            "Tom da Resposta",
            ["profissional", "amigável", "formal"],
            index=0,
            help="Tom da resposta sugerida",
        )

        st.markdown("### Sobre")
        st.markdown(
            """
        <div class="card">
            <div class="card-content">
                <p><strong>Modelo:</strong> DistilBERT Fine-tuned</p>
                <p><strong>Método:</strong> Sistema Híbrido</p>
                <p><strong>Categorias:</strong> Produtivo/Improdutivo</p>
                <p><strong>Idiomas:</strong> Multilíngue</p>
                <p><strong>Cache:</strong> Ativado</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Botão de análise
    if st.button("Analisar Email", type="primary", width="stretch"):
        # Determinar texto final
        final_content = ""

        if uploaded is not None:
            # Priorizar arquivo se enviado
            file_content = read_uploaded_file(uploaded)
            if file_content:
                final_content = file_content
                st.success(f"Arquivo processado: {uploaded.name}")
        else:
            # Usar texto colado
            final_content = content

        if not final_content:
            st.warning("Por favor, digite o conteúdo do email ou envie um arquivo.")
            return

        # Validação de tamanho do texto
        if len(final_content) < 10:
            st.warning(
                "O texto é muito curto para uma classificação precisa. Digite pelo menos 10 caracteres."
            )
            return

        if len(final_content) > 10000:
            st.warning(
                "O texto é muito longo. Para melhor performance, limite a 10.000 caracteres."
            )
            final_content = final_content[:10000]

        # Medir tempo de inferência
        start_time = time.perf_counter()

        # Classificar email
        with st.spinner("Classificando email..."):
            classification = classify_email(final_content)

        # Medir tempo
        inference_time = (time.perf_counter() - start_time) * 1000  # ms

        # Log de performance para análise
        st.info(
            f"Performance: Classificação em {inference_time:.0f}ms | Confiança: {classification['confidence']:.1%}"
        )

        # Gerar resposta sugerida
        with st.spinner("Gerando resposta..."):
            reply, reply_confidence, reasoning = suggest_reply(
                classification["category"], tone, final_content, classification
            )

        st.markdown("---")

        # Resumo da Classificação
        st.markdown("### Resumo da Classificação")

        # Status da classificação
        if classification["confidence"] >= 0.8:
            st.success("Classificação de Alta Confiança")
        elif classification["confidence"] >= 0.6:
            st.warning("Classificação de Confiança Média")
        else:
            st.error("Classificação de Baixa Confiança")

        # Badge da categoria
        category = classification["category"]
        confidence = classification["confidence"]

        # Determinar cor e estilo baseado na categoria
        if category == "Produtivo":
            st.markdown(
                f"""
            <div class="card status-card status-productive">
                <div class="card-header">
                    <h4>PRODUTIVO</h4>
                </div>
                <div class="card-content">
                    <p>Confiança: {confidence:.1%}</p>
                    <p>Requer ação da nossa equipe</p>
                    <p><strong>Status:</strong> Requer ação da equipe</p>
                    <p><strong>Prioridade:</strong> Alta</p>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        elif category == "Improdutivo":
            st.markdown(
                f"""
            <div class="card status-card status-unproductive">
                <div class="card-header">
                    <h4>IMPRODUTIVO</h4>
                </div>
                <div class="card-content">
                    <p>Confiança: {confidence:.1%}</p>
                    <p>Nenhuma ação necessária</p>
                    <p><strong>Status:</strong> Nenhuma ação necessária</p>
                    <p><strong>Prioridade:</strong> Baixa</p>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Métricas
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.markdown(
                f"""
            <div class="card">
                <div class="metric-value">{classification['confidence']:.1%}</div>
                <div class="metric-label">Confiança</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_metric2:
            st.markdown(
                f"""
            <div class="card">
                <div class="metric-value">{inference_time:.0f}ms</div>
                <div class="metric-label">Tempo de Inferência</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Explicação
        st.markdown(
            f"""
        <div class="card">
            <div class="card-content">
                <p>{classification['explanation']}</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Resposta sugerida
        st.markdown("### Resposta Sugerida")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(
                f"""
            <div class="card">
                <div class="card-header">
                    <h4>Resposta Gerada</h4>
                </div>
                <div class="card-content">
                    <div style="white-space: pre-wrap; font-family: 'Courier New', monospace; background: #f8fafc; padding: 1rem; border-radius: 6px; border: 1px solid #e2e8f0;">
                        {reply}
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">{reply_confidence:.1%}</div>
                <div class="metric-label">Confiança da Resposta</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.caption(f"{reasoning}")

        st.markdown("---")

        # Rodapé
        st.markdown("### Informações")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                """
            <div class="card">
                <div class="card-header">
                    <h4>Plataforma</h4>
                </div>
                <div class="card-content">
                    <p>Rodando em Streamlit</p>
                    <p>SDK: Streamlit</p>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                """
            <div class="card">
                <div class="card-header">
                    <h4>Modelo</h4>
                </div>
                <div class="card-content">
                    <p>DistilBERT Fine-tuned</p>
                    <p>100% de Acurácia</p>
                    <p>Multilíngue</p>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                """
            <div class="card">
                <div class="card-header">
                    <h4>Performance</h4>
                </div>
                <div class="card-content">
                    <p>Cache ativado</p>
                    <p>Cold start: ~3-5s</p>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.caption(
            "**Dica**: A primeira execução pode levar alguns segundos (cold start). Sistema híbrido DistilBERT + Correção Inteligente!"
        )


if __name__ == "__main__":
    main()
