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

# Configuração da página
st.set_page_config(
    page_title="Email Productivity Classifier",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Constantes
MODEL_ID = "models/bert_prod_improd"  # Troque pelo seu modelo no Hub
ID2LABEL = {0: "Improdutivo", 1: "Produtivo"}


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


# Instanciar classificador inteligente
smart_classifier = SmartEmailClassifier()


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
    Pré-processamento NLP para português brasileiro

    Args:
        text: Texto a ser processado

    Returns:
        Texto processado
    """
    if not text:
        return ""

    # Normalizar espaços
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenização simples por palavras
    tokens = re.findall(r"\w+|\S", text, flags=re.UNICODE)

    # Remover stopwords (case-insensitive)
    tokens = [t for t in tokens if t.lower() not in STOP_PT]

    # Opcional: stemming leve com RSLP
    # from nltk.stem import RSLPStemmer
    # stemmer = RSLPStemmer()
    # tokens = [stemmer.stem(t) if t.isalpha() else t for t in tokens]

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
    Classifica email usando classificador inteligente (BERT + palavras-chave)

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

    # Pré-processar texto
    processed_text = preprocess(text)

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

    # Predição do modelo BERT
    model_prediction = {"category": bert_category, "confidence": bert_confidence}

    # Usar classificador inteligente para correção
    smart_result = smart_classifier.smart_classify(text, model_prediction)

    # Determinar categoria final
    final_category = smart_result["category"]
    final_confidence = smart_result["confidence"]
    method_used = smart_result["method"]
    correction_applied = smart_result["correction_applied"]

    # Gerar explicação inteligente
    if correction_applied:
        explanation = f"Classificação inteligente: {final_category} (corrigido de {bert_category}) com {final_confidence:.2%}."
    else:
        explanation = (
            f"Modelo BERT classificou como {final_category} com {final_confidence:.2%}."
        )

    return {
        "category": final_category,
        "confidence": final_confidence,
        "scores": scores,
        "explanation": explanation,
        "processed_text": processed_text,
        "original_text": text,
        "method": method_used,
        "correction_applied": correction_applied,
        "bert_prediction": bert_category,
        "smart_category": final_category,
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

    # Se temos informações de classificação inteligente, usar o classificador
    if classification_info and hasattr(smart_classifier, "get_smart_response"):
        try:
            reply = smart_classifier.get_smart_response(classification_info, tone)
            confidence = 0.95
            reasoning = f"Resposta inteligente para categoria '{category}' com tom {tone} - gerada automaticamente."
            return reply, confidence, reasoning
        except Exception as e:
            st.warning(f"Erro ao gerar resposta inteligente: {e}")
            # Continuar com templates tradicionais

    # Templates tradicionais para compatibilidade
    produtivo_templates = {
        "profissional": """Prezado(a),

Obrigado(a) pelo seu contato. Recebemos sua mensagem e confirmamos que requer nossa atenção.

Para dar continuidade, precisamos de algumas informações:
- Qual o prazo esperado para esta demanda?
- Há algum anexo que deveria acompanhar esta mensagem?
- Existe alguma prioridade específica?

Atenciosamente,
Equipe de Atendimento""",
        "amigável": """Oi!

Obrigado pelo contato! 😊 

Recebemos sua mensagem e vamos dar a atenção necessária.

Para organizarmos melhor, você poderia me informar:
- Qual o prazo que você tem em mente?
- Tem algum arquivo para anexar?
- É algo urgente?

Qualquer dúvida, é só falar!

Abraços!""",
        "formal": """Exmo(a). Sr(a).,

Agradecemos o contato e informamos que sua comunicação foi recebida e está sendo processada.

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

Obrigado(a) pelo seu contato. Recebemos sua mensagem e informamos que não requer ação específica de nossa parte.

Agradecemos a comunicação e ficamos à disposição para futuras demandas que necessitem de nossa intervenção.

Atenciosamente,
Equipe de Comunicação""",
        "amigável": """Oi!

Obrigado pelo contato! 😊 

Recebemos sua mensagem e entendemos que não precisa de nenhuma ação nossa no momento.

Se precisar de algo específico no futuro, é só falar!

Abraços!""",
        "formal": """Exmo(a). Sr(a).,

Agradecemos o contato e informamos que sua comunicação foi recebida.

Conforme análise, esta mensagem não requer ação específica de nosso departamento no momento.

Ficamos à disposição para futuras demandas que necessitem de nossa intervenção.

Respeitosamente,
Departamento de Comunicação""",
    }

    # Selecionar template baseado na categoria
    if category in ["Produtivo", "solicitacao_acao", "problema_urgencia"]:
        reply = produtivo_templates.get(tone, produtivo_templates["profissional"])
        confidence = 0.90
        reasoning = f"Resposta automática para email {category} com tom {tone} - solicita confirmação de objetivo/prazo/anexos."
    else:
        reply = improdutivo_templates.get(tone, improdutivo_templates["profissional"])
        confidence = 0.95
        reasoning = f"Resposta automática para email {category} com tom {tone} - agradece e indica que não requer ação."

    return reply, confidence, reasoning


# Interface principal
def main():
    st.title("🧠 Email Intelligence Classifier")
    st.subheader(
        "Classificação Inteligente de Emails + Respostas Automáticas Contextuais"
    )

    # Instruções de uso
    st.markdown("### 📋 Como usar (3 passos)")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            """
        **1️⃣ Envie arquivo ou cole texto**
        - Upload .txt/.pdf ou
        - Cole o conteúdo do email
        """
        )

    with col2:
        st.info(
            """
        **2️⃣ Escolha o tom da resposta**
        - Profissional
        - Amigável  
        - Formal
        """
        )

    with col3:
        st.info(
            """
        **3️⃣ Clique em Analisar**
        - Veja classificação inteligente
        - Receba resposta contextual
        """
        )

    st.markdown("---")

    # Inputs
    col1, col2 = st.columns([2, 1])

    with col1:
        content = st.text_area(
            "📄 Conteúdo do Email",
            height=250,
            placeholder="Digite o conteúdo do email aqui...",
            help="Conteúdo completo do email",
        )

        # Upload de arquivo
        uploaded = st.file_uploader(
            "📁 Ou envie um arquivo (.txt ou .pdf)",
            type=["txt", "pdf"],
            help="Envie um arquivo .txt ou .pdf para análise",
        )

    with col2:
        tone = st.selectbox(
            "🎭 Tom da Resposta",
            ["profissional", "amigável", "formal"],
            index=0,
            help="Tom da resposta sugerida",
        )

        st.markdown("### ℹ️ Sobre")
        st.info(
            """
            **Modelo**: BERT PT-BR Fine-tuned + Classificador Inteligente  
            **Método**: Text Classification + Palavras-chave  
            **Categorias**: Produtivo/Improdutivo + Específicas  
            **Cache**: Ativado
            **NLP**: Stopwords PT-BR + Regras Inteligentes
            """
        )

    st.markdown("---")

    # Botão de análise
    if st.button("🔍 Analisar Email", type="primary", use_container_width=True):
        # Determinar texto final
        final_content = ""

        if uploaded is not None:
            # Priorizar arquivo se enviado
            file_content = read_uploaded_file(uploaded)
            if file_content:
                final_content = file_content
                st.success(f"✅ Arquivo processado: {uploaded.name}")
        else:
            # Usar texto colado
            final_content = content

        if not final_content:
            st.warning("⚠️ Por favor, digite o conteúdo do email ou envie um arquivo.")
            return

        # Medir tempo de inferência
        start_time = time.perf_counter()

        # Classificar email
        with st.spinner("🤖 Classificando email..."):
            classification = classify_email(final_content)

        # Medir tempo
        inference_time = (time.perf_counter() - start_time) * 1000  # ms

        # Gerar resposta sugerida
        with st.spinner("💬 Gerando resposta..."):
            reply, reply_confidence, reasoning = suggest_reply(
                classification["category"], tone, final_content, classification
            )

        st.markdown("---")

        # Resultados em duas colunas
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 📊 Resumo")

            # Badge da categoria
            category = classification["category"]
            confidence = classification["confidence"]

            # Determinar cor e ícone baseado na categoria
            if category in [
                "aniversario_parabens",
                "agradecimento",
                "informacao_geral",
                "feriado_datas_especiais",
                "saudacoes_sociais",
            ]:
                st.info(
                    f"🎉 **{category.upper().replace('_', ' ')}** - {confidence:.1%}"
                )
            elif category in [
                "solicitacao_acao",
                "problema_urgencia",
                "lembrete_agendamento",
            ]:
                st.success(
                    f"✅ **{category.upper().replace('_', ' ')}** - {confidence:.1%}"
                )
            elif category == "Produtivo":
                st.success(f"✅ **PRODUTIVO** - {confidence:.1%}")
            elif category == "Improdutivo":
                st.error(f"🚨 **IMPRODUTIVO** - {confidence:.1%}")
            else:
                st.warning(f"⚠️ **{category.upper()}** - {confidence:.1%}")

            # Mostrar se foi corrigido
            if classification.get("correction_applied"):
                st.info(
                    f"🔧 **Correção Aplicada**: {classification['bert_prediction']} → {classification['smart_category']}"
                )

            # Confiança
            st.metric("Confiança", f"{classification['confidence']:.1%}")

            # Tempo de inferência
            st.metric("Tempo de Inferência", f"{inference_time:.0f}ms")

            # Explicação
            st.info(f"💡 {classification['explanation']}")

        with col2:
            st.markdown("### 📈 Detalhes")

            # Scores brutos
            st.markdown("**Scores Detalhados:**")
            for label, score in classification["scores"].items():
                if label == "Produtivo":
                    st.progress(score, text=f"Produtivo: {score:.1%}")
                else:
                    st.progress(score, text=f"Improdutivo: {score:.1%}")

            # Informações técnicas
            with st.expander("🔧 Informações Técnicas"):
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
        st.markdown("### 💬 Resposta Sugerida")

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
            st.metric("Confiança da Resposta", f"{reply_confidence:.1%}")
            st.caption(f"💭 {reasoning}")

            # Botão para copiar
            if st.button("📋 Copiar Resposta", use_container_width=True):
                st.code(reply, language=None)
                st.success("✅ Resposta copiada! (Use Ctrl+C)")

    st.markdown("---")

    # Rodapé
    st.markdown("### 📋 Informações")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            """
            **🌐 Plataforma**  
            Rodando em Hugging Face Spaces  
            SDK: Streamlit
            """
        )

    with col2:
        st.info(
            """
            **🤖 Modelo**  
            BERT PT-BR Fine-tuned + IA  
            Classificação Inteligente
            """
        )

    with col3:
        st.info(
            """
            **⚡ Performance**  
            Cache ativado  
            Cold start: ~3-5s
            """
        )

    st.caption(
        "💡 **Dica**: A primeira execução pode levar alguns segundos (cold start). Modelo local + classificador inteligente ativado!"
    )


if __name__ == "__main__":
    main()
