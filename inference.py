import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple, Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model(
    model_dir: str,
) -> Tuple[AutoTokenizer, AutoModelForSequenceClassification]:
    """
    Carrega o tokenizer e modelo do diretório ou Hugging Face Hub

    Args:
        model_dir: Caminho local ou nome do modelo no HF Hub (ex: 'usuario/repositorio')

    Returns:
        Tuple contendo (tokenizer, model)

    Raises:
        Exception: Para erros de carregamento
    """
    try:
        # Verificar se é um modelo do Hugging Face Hub
        if "/" in model_dir and not os.path.exists(model_dir):
            logger.info(f"Carregando modelo do Hugging Face Hub: {model_dir}")

            # Verificar se há token de acesso
            hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

            # Carregar tokenizer
            if hf_token:
                tokenizer = AutoTokenizer.from_pretrained(model_dir, token=hf_token)
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_dir, token=hf_token
                )
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_dir)
                model = AutoModelForSequenceClassification.from_pretrained(model_dir)

        else:
            # Modelo local
            if not os.path.exists(model_dir):
                raise FileNotFoundError(
                    f"Diretório do modelo não encontrado: {model_dir}"
                )

            logger.info(f"Carregando modelo local de: {model_dir}")

            # Carregar tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_dir)

            # Carregar modelo
            model = AutoModelForSequenceClassification.from_pretrained(model_dir)

        logger.info("Modelo carregado com sucesso")

        # Configurar para inferência
        model.eval()

        # Mover para CPU (padrão para Streamlit)
        device = torch.device("cpu")
        model = model.to(device)

        logger.info(f"Modelo configurado para dispositivo: {device}")

        return tokenizer, model

    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {e}")
        raise


def run_inference(
    tokenizer: AutoTokenizer, model: AutoModelForSequenceClassification, text: str
) -> Tuple[str, float, Dict[int, float]]:
    """
    Executa inferência no texto fornecido

    Args:
        tokenizer: Tokenizer carregado
        model: Modelo carregado
        text: Texto para classificar

    Returns:
        Tuple contendo (prediction, confidence, scores)
        - prediction: Classe prevista ("Produtivo" ou "Improdutivo")
        - confidence: Confiança da predição (0-1)
        - scores: Dicionário com scores para cada classe
    """
    try:
        # Mapeamento de IDs para labels
        id2label = {0: "Improdutivo", 1: "Produtivo"}

        # Tokenizar texto
        inputs = tokenizer(
            text, truncation=True, padding=True, max_length=512, return_tensors="pt"
        )

        # Executar inferência
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)

        # Obter predição e confiança
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class].item()

        # Obter scores para todas as classes
        scores = {
            0: probabilities[0][0].item(),  # Improdutivo
            1: probabilities[0][1].item(),  # Produtivo
        }

        # Converter ID para label
        prediction = id2label[predicted_class]

        logger.info(
            f"Classificação concluída: {prediction} (confiança: {confidence:.3f})"
        )

        return prediction, confidence, scores

    except Exception as e:
        logger.error(f"Erro durante inferência: {e}")
        raise


def preprocess_for_inference(text: str) -> str:
    """
    Pré-processa texto para inferência

    Args:
        text: Texto bruto

    Returns:
        Texto pré-processado
    """
    # Remover espaços extras
    text = " ".join(text.split())

    # Limitar tamanho (o modelo tem limite de 512 tokens)
    if len(text) > 2000:  # Aproximadamente 500 tokens
        text = text[:2000] + "..."

    return text
