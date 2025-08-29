# backend/main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time

# Baseline local (carrega o seu joblib)
import joblib
from pathlib import Path
import numpy as np

USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
USE_HF = bool(os.getenv("HF_API_TOKEN"))

MODEL_PATH = Path("models/email_spam_pipeline.joblib")
baseline = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

app = FastAPI(title="Email Productivity API")


class EmailIn(BaseModel):
    text: str


def classify_baseline(text: str):
    if not baseline:
        return {"label": "Produtivo", "confidence": 0.50}
    proba = baseline.predict_proba([text])[0]
    idx = int(np.argmax(proba))
    label = baseline.classes_[idx]  # 'produtivo' | 'improdutivo'
    conf = float(proba[idx])
    # Em MAIÚSCULA inicial para exibição
    label_pretty = "Produtivo" if label == "produtivo" else "Improdutivo"
    return {"label": label_pretty, "confidence": conf}


def suggest_reply_rule_based(label: str, text: str):
    if label.lower() == "improdutivo":
        return (
            "Obrigado pelo contato. Esta mensagem parece ser promocional/"
            "não relacionada ao nosso fluxo de trabalho. Não vamos prosseguir."
        )
    else:
        return (
            "Olá! Obrigado pela mensagem. Vamos dar sequência: "
            "poderia confirmar objetivo, prazo e próximos passos? 👍"
        )


# ====== OpenAI (opcional) ======
import requests


def classify_openai(text: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    # Prompt curto para reduzir custo
    system = (
        "Você é um classificador. Responda somente JSON com campos: "
        '{"label":"Produtivo|Improdutivo","confidence":0.0-1.0}. '
        "Considere 'produtivo'=ham (relevante) e 'improdutivo'=spam."
    )
    user = f"Texto: {text}\nClassifique."
    payload = {
        "model": "gpt-4o-mini",  # barato/estável
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 60,
        "temperature": 0.0,
    }
    r = requests.post(
        url, headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=10
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    # Tente extrair JSON simples
    import json, re

    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        return None
    data = json.loads(m.group(0))
    return {
        "label": data.get("label", "Produtivo"),
        "confidence": float(data.get("confidence", 0.5)),
    }


def generate_reply_openai(label: str, text: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    system = "Gere UMA resposta curta e educada em PT-BR adequada ao rótulo (Produtivo/Improdutivo)."
    user = f"Rótulo: {label}\nTexto:\n{text}\nResposta curta:"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 120,
        "temperature": 0.3,
    }
    r = requests.post(
        url, headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=10
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


# ====== Hugging Face Inference API (opcional) ======
def classify_hf_zeroshot(text: str):
    token = os.getenv("HF_API_TOKEN")
    if not token:
        return None
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": ["produtivo", "improdutivo"],
            "multi_label": False,
        },
    }
    r = requests.post(
        url, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=12
    )
    r.raise_for_status()
    data = r.json()
    labels = data["labels"]
    scores = data["scores"]
    idx = int(np.argmax(scores))
    label_raw = labels[idx]
    conf = float(scores[idx])
    label = "Produtivo" if label_raw == "produtivo" else "Improdutivo"
    return {"label": label, "confidence": conf}


@app.post("/classify_and_reply")
def classify_and_reply(inp: EmailIn):
    t0 = time.time()

    # 1) Tenta IA externa (OpenAI > HF). Se falhar, cai no baseline.
    result = None
    if USE_OPENAI:
        try:
            result = classify_openai(inp.text)
        except Exception:
            result = None
    if (result is None) and USE_HF:
        try:
            result = classify_hf_zeroshot(inp.text)
        except Exception:
            result = None
    if result is None:
        result = classify_baseline(inp.text)

    # 2) Geração de resposta
    reply = None
    if USE_OPENAI:
        try:
            reply = generate_reply_openai(result["label"], inp.text)
        except Exception:
            reply = None
    if reply is None:
        reply = suggest_reply_rule_based(result["label"], inp.text)

    elapsed = round(time.time() - t0, 3)
    return {
        "label": result["label"],
        "confidence": result["confidence"],
        "suggested_reply": reply,
        "elapsed_sec": elapsed,
    }
