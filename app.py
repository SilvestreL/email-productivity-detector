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
    page_icon="📧",  # UI-ONLY: manter ícone para identificação da aba
    layout="wide",
    initial_sidebar_state="expanded",  # UI-ONLY: começar com sidebar expandida
)

# CSS customizado para UI profissional
st.markdown(
    """
<style>
/* Reset e configurações base */
.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Ocultar elementos decorativos do Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* Removido: header {visibility: hidden;} para permitir toggle do sidebar */

/* Tipografia profissional */
h1 {
    color: #2E3A46 !important;
    font-size: 32px !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
}

h2 {
    color: #2E3A46 !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    margin-bottom: 0.75rem !important;
}

h3 {
    color: #2E3A46 !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
}

/* Cards e containers */
.card {
    background: #F8F9FA;
    border: 1px solid #EAEAEA;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.metric-card {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.metric-value {
    color: #1A3A6E !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
}

.metric-label {
    color: #5A6A7A !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

/* Sidebar styling */
.sidebar .sidebar-content {
    border-right: 1px solid #EAEAEA;
}

/* Botões e inputs */
.stButton > button {
    background-color: #1A3A6E !important;
    border-color: #1A3A6E !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
}

.stButton > button:hover {
    background-color: rgba(26,58,110,0.9) !important;
    border-color: rgba(26,58,110,0.9) !important;
}

.stSelectbox > div > div > select {
    border-color: #EAEAEA !important;
    border-radius: 6px !important;
}

.stTextArea > div > div > textarea {
    border-color: #EAEAEA !important;
    border-radius: 6px !important;
}

/* Links e navegação */
.link {
    color: #1A3A6E !important;
    text-decoration: underline !important;
    cursor: pointer !important;
}

.link:hover {
    background-color: rgba(26,58,110,0.08) !important;
    text-decoration: none !important;
}

/* Tabelas */
.dataframe {
    border: 1px solid #EAEAEA !important;
    border-radius: 8px !important;
}

/* Progress bars */
.stProgress > div > div > div > div {
    background-color: #1A3A6E !important;
}

/* Info boxes */
.stAlert {
    border: 1px solid #EAEAEA !important;
    border-radius: 8px !important;
    background-color: #F8F9FA !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #F8F9FA !important;
    border: 1px solid #EAEAEA !important;
    border-radius: 6px !important;
}

/* Responsividade */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

/* === Sidebar (UI-ONLY) === */
section[data-testid="stSidebar"]{
    background:#FFFFFF;
    border-right:1px solid #EAEAEA;
}

/* Garantir que o botão de toggle do sidebar seja visível */
button[data-testid="baseButton-secondary"] {
    visibility: visible !important;
    display: block !important;
}


.sb-wrap{ padding:12px 10px; }
.sb-header{ display:flex; align-items:center; justify-content:space-between; gap:8px; }
.sb-title{ font-weight:700; color:#2E3A46; font-size:15px; margin:0; }
.sb-toggle{ border:1px solid #EAEAEA; border-radius:8px; padding:6px 10px; cursor:pointer; background:#FFFFFF; }
.sb-section{ margin-top:14px; }
.sb-section h4{ color:#2E3A46; font-size:14px; margin:0 0 8px 0; }
.sb-text{ color:#5A6A7A; font-size:13px; line-height:1.45; margin:0; }
.sb-links{ display:flex; flex-direction:column; gap:6px; margin-top:6px; }
.sb-link{ display:flex; align-items:center; gap:10px; padding:8px 10px; border-radius:10px; color:#2E3A46; text-decoration:none; }
.sb-link:hover{ background:rgba(26,58,110,0.08); }
.sb-icon{ display:inline-flex; width:18px; height:18px; }
.sb-label{ display:inline-block; }
.sb-divider{ height:1px; background:#EAEAEA; margin:12px 0; }
/* collapsed */
.sb-collapsed .sb-label{ display:none; }
.sb-collapsed section[data-testid="stSidebar"]{ width:74px !important; }
/* dark theme */
.theme-dark section[data-testid="stSidebar"]{ background:#0F1A2B; border-right:1px solid #1E2A3C; }
.theme-dark .sb-title, .theme-dark .sb-text, .theme-dark .sb-link{ color:#E6EAF0; }
.theme-dark .sb-link:hover{ background:#142544; }
</style>
""",
    unsafe_allow_html=True,
)

# Constantes

# Constantes
# Constantes
MODEL_ID = "models/bert_prod_improd"  # Troque pelo seu modelo no Hub
ID2LABEL = {0: "Improdutivo", 1: "Produtivo"}


# === Sidebar renderer (UI-ONLY) ===
def render_sidebar():
    """UI-ONLY: Renderiza sidebar com toggle, explicação, modelo e links."""
    # Estado: tema e colapso
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    if "sb_collapsed" not in st.session_state:
        st.session_state["sb_collapsed"] = False

    collapsed = st.session_state["sb_collapsed"]

    # Botão de toggle no topo da sidebar
    with st.sidebar:
        # wrapper com classe condicional
        wrapper_class = "sb-wrap sb-collapsed" if collapsed else "sb-wrap"
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)

        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.markdown(
                '<div class="sb-header"><span class="sb-title">Menu</span></div>',
                unsafe_allow_html=True,
            )
        with col_b:
            # Espaço para balancear o layout
            st.markdown("&nbsp;", unsafe_allow_html=True)

        # === Seção: Sobre a Aplicação ===
        st.markdown('<div class="sb-section">', unsafe_allow_html=True)
        st.markdown("<h4>Sobre a Aplicação</h4>", unsafe_allow_html=True)
        st.markdown(
            '<p class="sb-text sb-label">Classifica e-mails como <strong>Produtivo</strong> ou <strong>Improdutivo</strong> e sugere respostas com base no conteúdo. Interface simples para análise, histórico e métricas.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # === Seção: Modelo de ML ===
        st.markdown('<div class="sb-section">', unsafe_allow_html=True)
        st.markdown("<h4>Modelo de ML</h4>", unsafe_allow_html=True)
        st.markdown(
            '<p class="sb-text sb-label">Arquitetura <strong>Deep Learning (BERT)</strong> para classificação de texto, com fine-tuning em dataset rotulado. Métricas (accuracy, precision, recall, f1) disponíveis na interface.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # === Seção: Links (SVG inline) ===
        github_svg = _find_icon_svg("github")
        linkedin_svg = _find_icon_svg("linkedin")
        docs_svg = _find_icon_svg("document")

        st.markdown('<div class="sb-section">', unsafe_allow_html=True)
        st.markdown("<h4>Links</h4>", unsafe_allow_html=True)

        gh_html = f'<a class="sb-link" href="https://github.com/seu-repo" target="_blank" rel="noopener" aria-label="GitHub"><span class="sb-icon">{github_svg}</span><span class="sb-label">GitHub</span></a>'
        li_html = f'<a class="sb-link" href="https://www.linkedin.com/in/seu-perfil" target="_blank" rel="noopener" aria-label="LinkedIn"><span class="sb-icon">{linkedin_svg}</span><span class="sb-label">LinkedIn</span></a>'
        dc_html = f'<a class="sb-link" href="https://seu-dominio/docs" target="_blank" rel="noopener" aria-label="Documentação"><span class="sb-icon">{docs_svg}</span><span class="sb-label">Documentação</span></a>'

        st.markdown('<div class="sb-links">', unsafe_allow_html=True)
        st.markdown(gh_html, unsafe_allow_html=True)
        st.markdown(li_html, unsafe_allow_html=True)
        st.markdown(dc_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # fecha wrapper
        st.markdown("</div>", unsafe_allow_html=True)


# Classificador Inteligente
class SmartEmailClassifier:
    """
    Classificador inteligente que combina modelo BERT com regras baseadas em palavras-chave
    """

    def __init__(self):
        # Categorias mais granulares
        self.categories = {
            "aniversario_parabens": {
                "keywords": [
                    "aniversário",
                    "parabéns",
                    "felicidades",
                    "saúde",
                    "muitos anos",
                    "feliz aniversário",
                ],
                "priority": 1.0,  # Alta prioridade
                "response_type": "social_greeting",
            },
            "feriado_datas_especiais": {
                "keywords": [
                    "feriado",
                    "feriados",
                    "natal",
                    "ano novo",
                    "páscoa",
                    "carnaval",
                    "sexta-feira",
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
                    "ótima",
                ],
                "priority": 1.0,  # Alta prioridade
                "response_type": "holiday_greeting",
            },
            "saudacoes_sociais": {
                "keywords": [
                    "bom dia",
                    "boa tarde",
                    "boa noite",
                    "olá",
                    "oi",
                    "olá a todos",
                    "oi pessoal",
                    "bom dia a todos",
                    "bom dia equipe",
                    "bom dia pessoal",
                    "apenas para informar",
                    "apenas informando",
                    "só para avisar",
                    "só informando",
                ],
                "priority": 0.95,  # Alta prioridade
                "response_type": "social_greeting",
            },
            "agradecimento": {
                "keywords": [
                    "obrigado",
                    "obrigada",
                    "valeu",
                    "agradeço",
                    "agradecemos",
                    "grato",
                ],
                "priority": 0.9,
                "response_type": "acknowledgment",
            },
            "informacao_geral": {
                "keywords": [
                    "informar",
                    "comunicar",
                    "avisar",
                    "notificar",
                    "divulgar",
                ],
                "priority": 0.8,
                "response_type": "information",
            },
            "solicitacao_acao": {
                "keywords": [
                    "preciso",
                    "solicito",
                    "requer",
                    "necessito",
                    "urgente",
                    "reunião",
                    "projeto",
                ],
                "priority": 0.7,
                "response_type": "action_required",
            },
            "problema_urgencia": {
                "keywords": [
                    "problema",
                    "erro",
                    "falha",
                    "crítico",
                    "emergência",
                    "bug",
                    "sistema",
                ],
                "priority": 0.9,
                "response_type": "urgent_action",
            },
            "lembrete_agendamento": {
                "keywords": [
                    "lembrar",
                    "lembrete",
                    "agenda",
                    "horário",
                    "data",
                    "deadline",
                ],
                "priority": 0.8,
                "response_type": "reminder",
            },
        }

    def classify_with_keywords(self, text: str) -> Tuple[str, float, str]:
        """
        Classifica usando palavras-chave com alta confiança
        """
        text_lower = text.lower()

        # Verificar cada categoria
        for category, config in self.categories.items():
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    confidence = config["priority"]
                    response_type = config["response_type"]
                    return category, confidence, response_type

        # Se não encontrar palavras-chave específicas, retornar None
        return None, 0.0, None

    def smart_classify(self, text: str, model_prediction: Dict) -> Dict:
        """
        Classificação inteligente combinando palavras-chave e modelo BERT
        """

        # Primeiro, verificar se há palavras-chave óbvias
        keyword_category, keyword_confidence, response_type = (
            self.classify_with_keywords(text)
        )

        # Se encontrou categoria por palavras-chave com alta confiança
        if keyword_category and keyword_confidence > 0.8:
            return {
                "category": keyword_category,
                "confidence": keyword_confidence,
                "response_type": response_type,
                "method": "keyword_based",
                "original_model_prediction": model_prediction,
                "correction_applied": True,
            }

        # Se não, usar predição do modelo
        return {
            "category": model_prediction["category"],
            "confidence": model_prediction["confidence"],
            "response_type": "model_based",
            "method": "bert_model",
            "correction_applied": False,
        }

    def get_smart_response(
        self, classification: Dict, tone: str = "profissional"
    ) -> str:
        """
        Gera resposta inteligente baseada na classificação
        """
        category = classification["category"]
        response_type = classification.get("response_type", "default")

        responses = {
            "aniversario_parabens": {
                "profissional": "Obrigado pela mensagem de aniversário! Desejamos muitas felicidades e sucesso.",
                "amigável": "Que legal! Obrigado por compartilhar essa data especial! 🎉 Muitas felicidades!",
                "formal": "Agradecemos a mensagem de aniversário. Desejamos muitas felicidades e prosperidade.",
            },
            "agradecimento": {
                "profissional": "De nada! Ficamos felizes em poder ajudar.",
                "amigável": "Por nada! 😊 Foi um prazer!",
                "formal": "É um prazer poder auxiliar. Ficamos à disposição para futuras demandas.",
            },
            "informacao_geral": {
                "profissional": "Informação recebida e registrada. Obrigado pela comunicação.",
                "amigável": "Ok, anotado! 👍 Obrigado por informar!",
                "formal": "Informação recebida e devidamente registrada. Agradecemos a comunicação.",
            },
            "solicitacao_acao": {
                "profissional": "Solicitação recebida. Vamos analisar e retornar em breve com as informações solicitadas.",
                "amigável": "Beleza! Vou dar uma olhada nisso e te retorno! 😊",
                "formal": "Solicitação recebida e está sendo processada. Retornaremos em breve com as informações solicitadas.",
            },
            "problema_urgencia": {
                "profissional": "Problema identificado. Nossa equipe técnica foi notificada e está trabalhando na solução.",
                "amigável": "Ops! Vou resolver isso rapidinho! 🚀",
                "formal": "Problema identificado e nossa equipe técnica foi imediatamente notificada. Estamos trabalhando na solução.",
            },
            "lembrete_agendamento": {
                "profissional": "Lembrete registrado. Confirmaremos o agendamento em breve.",
                "amigável": "Perfeito! Vou anotar na agenda! 📅",
                "formal": "Lembrete registrado e será confirmado em breve. Agradecemos a comunicação.",
            },
            "feriado_datas_especiais": {
                "profissional": "Obrigado pela mensagem de feriado! Desejamos a todos um excelente descanso e aproveitem bastante!",
                "amigável": "Que ótimo! 🎉 Obrigado por compartilhar essa energia positiva! Aproveitem muito o feriado!",
                "formal": "Agradecemos os votos de feriado. Desejamos a todos um excelente período de descanso e renovação.",
            },
            "saudacoes_sociais": {
                "profissional": "Bom dia! Obrigado pela mensagem. Ficamos à disposição para futuras demandas.",
                "amigável": "Oi! 😊 Obrigado pela mensagem! Tudo bem por aí?",
                "formal": "Bom dia! Agradecemos a comunicação. Ficamos à disposição para futuras demandas.",
            },
        }

        # Retornar resposta baseada na categoria e tom
        if category in responses:
            return responses[category].get(tone, responses[category]["profissional"])

        # Resposta padrão se não encontrar categoria específica
        return "Mensagem recebida. Obrigado pelo contato."


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
            model=model, tokenizer=tokenizer, return_all_scores=True, device=device
        )
    except Exception as e:
        st.error(f"Erro ao carregar modelo: {e}")
        st.info(
            "💡 Certifique-se de que o modelo está disponível em models/bert_prod_improd"
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


def classify_email(content: str) -> Dict:
    """
    Classifica email usando modelo BERT fine-tuned

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

    # Traduzir para inglês se não estiver em inglês
    try:
        from deep_translator import GoogleTranslator

        translated_text = GoogleTranslator(source="auto", target="en").translate(text)
        st.info(f"🌐 Texto traduzido para inglês: {translated_text[:100]}...")
    except Exception as e:
        st.warning(f"⚠️ Erro na tradução: {e}. Usando texto original.")
        translated_text = text

    # Pré-processar texto traduzido
    processed_text = preprocess(translated_text)

    # Carregar classificador BERT
    classifier = get_classifier()

    if classifier is None:
        return {
            "category": "Erro",
            "confidence": 0.0,
            "scores": {"Produtivo": 0.0, "Improdutivo": 0.0},
            "explanation": "Erro ao carregar modelo.",
            "processed_text": processed_text,
            "original_text": text,
            "translated_text": translated_text,
        }

    # Classificar com BERT (limitar tamanho do texto)
    result = classifier(processed_text[:4000])  # Evita textos muito longos

    # Mapear resultados do BERT
    scores = {}
    for pred in result[0]:
        # O modelo retorna labels como strings ("Improdutivo", "Produtivo")
        label_name = pred["label"]
        scores[label_name] = float(pred["score"])

    # Encontrar categoria com maior score do BERT
    bert_category = max(scores, key=scores.get)
    bert_confidence = scores[bert_category]

    # Garantir que a categoria seja apenas "Produtivo" ou "Improdutivo"
    if bert_category not in ["Produtivo", "Improdutivo"]:
        # Mapear para a categoria mais próxima baseado no contexto
        if any(
            word in bert_category.lower()
            for word in [
                "produtivo",
                "productive",
                "work",
                "business",
                "urgent",
                "action",
                "project",
            ]
        ):
            bert_category = "Produtivo"
        else:
            bert_category = "Improdutivo"

    # Validação adicional de confiança
    if bert_confidence < 0.6:
        # Se confiança baixa, usar análise de palavras-chave como fallback
        if any(
            word in text.lower()
            for word in ["reunião", "projeto", "urgente", "problema", "deadline"]
        ):
            bert_category = "Produtivo"
            bert_confidence = max(bert_confidence, 0.7)
        elif any(
            word in text.lower()
            for word in ["oi", "olá", "bom dia", "parabéns", "obrigado"]
        ):
            bert_category = "Improdutivo"
            bert_confidence = max(bert_confidence, 0.7)

    # Gerar explicação detalhada
    if bert_confidence >= 0.8:
        confidence_level = "alta"
    elif bert_confidence >= 0.6:
        confidence_level = "média"
    else:
        confidence_level = "baixa"

    explanation = f"Modelo BERT classificou como {bert_category} com confiança {confidence_level} ({bert_confidence:.1%})."

    # Adicionar contexto baseado no tipo de email
    if bert_category == "Produtivo":
        explanation += " Este email requer atenção e ação da nossa equipe."
    else:
        explanation += " Este email não requer ação específica da nossa equipe."

    return {
        "category": bert_category,
        "confidence": bert_confidence,
        "scores": scores,
        "explanation": explanation,
        "processed_text": processed_text,
        "original_text": text,
        "translated_text": translated_text,
        "method": "BERT",
        "correction_applied": False,
        "bert_prediction": bert_category,
        "smart_category": bert_category,
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

Obrigado pelo contato! 😊 

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

Obrigado pelo contato! 😊 

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
    # UI-ONLY: Sidebar local com toggle e links
    render_sidebar()

    st.title("Email Intelligence Classifier")
    st.subheader(
        "Classificação Inteligente de Emails + Respostas Automáticas Contextuais"
    )

    # Instruções de uso
    st.markdown("### Como usar (3 passos)")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="card">
            <h4>1. Envie arquivo ou cole texto</h4>
            <p style="color: #5A6A7A;">Upload .txt/.pdf ou cole o conteúdo do email</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="card">
            <h4>2. Escolha o tom da resposta</h4>
            <p style="color: #5A6A7A;">Profissional, Amigável ou Formal</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="card">
            <h4>3. Clique em Analisar</h4>
            <p style="color: #5A6A7A;">Veja classificação inteligente e receba resposta contextual</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Exemplos de emails para teste
    st.markdown("### 📧 Exemplos para Teste")
    st.markdown(
        "Clique em um exemplo para inserir automaticamente no campo de conteúdo:"
    )

    col_ex1, col_ex2, col_ex3 = st.columns(3)

    with col_ex1:
        if st.button(
            "📈 Email Produtivo", key="ex_prod", help="Exemplo de email produtivo"
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
            "📉 Email Improdutivo", key="ex_improd", help="Exemplo de email improdutivo"
        ):
            st.session_state[
                "example_email"
            ] = """Oi pessoal!

Como estão? Espero que estejam todos bem! 😊

Só passando para dar um oi e ver se vocês viram aquele meme que enviei no grupo do WhatsApp ontem? Muito engraçado, né? 😂

Ah, e não esqueçam que hoje é aniversário da Maria! Parabéns Maria! 🎉🎂🎈

Bom fim de semana para todos!
Abraços,
Pedro"""
            st.rerun()

    with col_ex3:
        if st.button(
            "📋 Email Neutro", key="ex_neutro", help="Exemplo de email neutro"
        ):
            st.session_state[
                "example_email"
            ] = """Bom dia,

Informo que estarei ausente do escritório amanhã devido a um compromisso médico.

Minhas atividades estão organizadas e não há pendências urgentes.

Retorno na quinta-feira.

Atenciosamente,
Ana Costa
Assistente Administrativa"""
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
            "🗑️ Limpar Exemplo", key="clear_example", help="Limpa o campo de conteúdo"
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
            <p><strong>Modelo:</strong> BERT PT-BR Fine-tuned + Classificador Inteligente</p>
            <p><strong>Método:</strong> Text Classification + Palavras-chave</p>
            <p><strong>Categorias:</strong> Produtivo/Improdutivo + Específicas</p>
            <p><strong>Cache:</strong> Ativado</p>
            <p><strong>NLP:</strong> Stopwords PT-BR + Regras Inteligentes</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Botão de análise
    if st.button(
        "Analisar Email", type="primary", width="stretch"
    ):  # UI-ONLY: troca use_container_width por width='stretch'
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
        f"⚡ Performance: Classificação em {inference_time:.0f}ms | Confiança: {classification['confidence']:.1%}"
    )

    # Gerar resposta sugerida
    with st.spinner("Gerando resposta..."):
        reply, reply_confidence, reasoning = suggest_reply(
            classification["category"], tone, final_content, classification
        )

        st.markdown("---")

            # Resultados em duas colunas
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📊 Resumo da Classificação")
        
        # Status da classificação
        if classification["confidence"] >= 0.8:
            st.success("✅ Classificação de Alta Confiança")
        elif classification["confidence"] >= 0.6:
            st.warning("⚠️ Classificação de Confiança Média")
        else:
            st.error("❌ Classificação de Baixa Confiança")

            # Badge da categoria
            category = classification["category"]
            confidence = classification["confidence"]

            # Determinar cor e estilo baseado na categoria
            if category in [
                "aniversario_parabens",
                "agradecimento",
                "informacao_geral",
                "feriado_datas_especiais",
                "saudacoes_sociais",
            ]:
                st.markdown(
                    f"""
                <div class="card" style="border-left: 4px solid #1A3A6E;">
                    <h4 style="color: #1A3A6E; margin: 0;">{category.upper().replace('_', ' ')}</h4>
                    <p style="color: #5A6A7A; margin: 0.5rem 0 0 0;">Confiança: {confidence:.1%}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            elif category in [
                "solicitacao_acao",
                "problema_urgencia",
                "lembrete_agendamento",
            ]:
                st.markdown(
                    f"""
                <div class="card" style="border-left: 4px solid #2E7D32;">
                    <h4 style="color: #2E7D32; margin: 0;">{category.upper().replace('_', ' ')}</h4>
                    <p style="color: #5A6A7A; margin: 0.5rem 0 0 0;">Confiança: {confidence:.1%}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            elif category == "Produtivo":
                st.markdown(
                    f"""
                <div class="card" style="border-left: 4px solid #2E7D32;">
                    <h4 style="color: #2E7D32; margin: 0;">📈 PRODUTIVO</h4>
                    <p style="color: #5A6A7A; margin: 0.5rem 0 0 0;">Confiança: {confidence:.1%}</p>
                    <p style="color: #2E7D32; margin: 0.5rem 0 0 0; font-weight: 600;">✅ Requer ação da nossa equipe</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            elif category == "Improdutivo":
                st.markdown(
                    f"""
                <div class="card" style="border-left: 4px solid #D32F2F;">
                    <h4 style="color: #D32F2F; margin: 0;">📉 IMPRODUTIVO</h4>
                    <p style="color: #5A6A7A; margin: 0.5rem 0 0 0;">Confiança: {confidence:.1%}</p>
                    <p style="color: #D32F2F; margin: 0.5rem 0 0 0; font-weight: 600;">❌ Nenhuma ação necessária</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="card" style="border-left: 4px solid #FF9800;">
                    <h4 style="color: #FF9800; margin: 0;">{category.upper()}</h4>
                    <p style="color: #5A6A7A; margin: 0.5rem 0 0 0;">Confiança: {confidence:.1%}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            # Mostrar se foi corrigido
            if classification.get("correction_applied"):
                st.markdown(
                    f"""
                <div class="card" style="background-color: rgba(26,58,110,0.05);">
                    <p style="color: #1A3A6E; margin: 0;"><strong>Correção Aplicada:</strong> {classification['bert_prediction']} → {classification['smart_category']}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            # Métricas
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.markdown(
                    f"""
                <div class="metric-card">
                    <div class="metric-value">{classification['confidence']:.1%}</div>
                    <div class="metric-label">Confiança</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col_metric2:
                st.markdown(
                    f"""
                <div class="metric-card">
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
                <p style="color: #5A6A7A; margin: 0;">{classification['explanation']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown("### Detalhes")

            # Scores brutos
            st.markdown("**Scores Detalhados:**")
            for label, score in classification["scores"].items():
                if label == "Produtivo":
                    st.progress(score, text=f"Produtivo: {score:.1%}")
                else:
                    st.progress(score, text=f"Improdutivo: {score:.1%}")

            # Informações técnicas
            with st.expander("Informações Técnicas"):
                tech_info = {
                    "modelo": "BERT Local (Fine-tuned) + Classificador Inteligente",
                    "método": classification.get("method", "text-classification"),
                    "tempo_inferencia_ms": round(inference_time, 2),
                    "scores_completos": classification["scores"],
                    "tamanho_texto_original": len(classification["original_text"]),
                    "tamanho_texto_processado": len(classification["processed_text"]),
                    "modelo_local": MODEL_ID,
                }

                # Adicionar informações de correção se aplicável
                if classification.get("correction_applied"):
                    tech_info.update(
                        {
                            "correcao_aplicada": True,
                            "predicao_bert": classification["bert_prediction"],
                            "categoria_final": classification["smart_category"],
                            "metodo_final": classification["method"],
                        }
                    )

                st.json(tech_info)

        st.markdown("---")

        # Resposta sugerida
        st.markdown("### Resposta Sugerida")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.text_area(
                "Resposta Gerada",
                value=reply,
                height=200,
                disabled=True,
                help="Resposta sugerida baseada na classificação e tom selecionado",
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

            # Botão para copiar
            if st.button(
                "Copiar Resposta", width="content"
            ):  # UI-ONLY: width fixo para botão
                st.code(reply, language=None)
                st.success("Resposta copiada! (Use Ctrl+C)")

    st.markdown("---")

    # Rodapé
    st.markdown("### Informações")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="card">
            <h4>Plataforma</h4>
            <p style="color: #5A6A7A;">Rodando em Hugging Face Spaces</p>
            <p style="color: #5A6A7A;">SDK: Streamlit</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="card">
            <h4>Modelo</h4>
            <p style="color: #5A6A7A;">BERT PT-BR Fine-tuned + IA</p>
            <p style="color: #5A6A7A;">Classificação Inteligente</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="card">
            <h4>Performance</h4>
            <p style="color: #5A6A7A;">Cache ativado</p>
            <p style="color: #5A6A7A;">Cold start: ~3-5s</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.caption(
        "**Dica**: A primeira execução pode levar alguns segundos (cold start). Modelo local + classificador inteligente ativado!"
    )


if __name__ == "__main__":
    main()
