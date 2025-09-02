#!/usr/bin/env python3
"""
Script para preparar dataset de emails para treinamento
Converte spam.csv em dataset formatado para fine-tuning
"""

import pandas as pd
import json
import os
import torch
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from transformers import TrainingArguments, DataCollatorWithPadding
from transformers.trainer_callback import EarlyStoppingCallback
from typing import Dict, List, Tuple

# Configurações
DATASET_PATH = "data/spam.csv"
OUTPUT_DIR = "data/processed"
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

# Mapeamento de labels
LABEL_MAPPING = {
    "spam": "Improdutivo",  # spam = improdutivo
    "ham": "Produtivo",  # ham = produtivo
}

# Labels numéricos para o modelo
ID2LABEL = {0: "Improdutivo", 1: "Produtivo"}
LABEL2ID = {"Improdutivo": 0, "Produtivo": 1}

# Configurações de treinamento
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    gradient_accumulation_steps=2,
    learning_rate=2e-5,
    weight_decay=0.01,
    max_grad_norm=1.0,
    lr_scheduler_type="linear",
    warmup_ratio=0.06,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    fp16=torch.cuda.is_available(),
    gradient_checkpointing=True,
    report_to=None,
    seed=42,
    data_seed=42,
)

# Data collator (será inicializado com tokenizer posteriormente)
# data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)


# Callbacks
class ProgressCallback:
    """Callback para mostrar progresso do treinamento"""

    pass


class EpochSummaryCallback:
    """Callback para resumo de cada época"""

    pass


callbacks = [
    EarlyStoppingCallback(
        early_stopping_patience=2
    ),  # pode reduzir p/ 2 se fizer epoch=3
    ProgressCallback(),
    EpochSummaryCallback(),
]


def load_spam_dataset(path: str) -> pd.DataFrame:
    """
    Carrega dataset de spam e converte para classificação de produtividade

    Args:
        path: Caminho para o arquivo spam.csv

    Returns:
        DataFrame com colunas ['text', 'label', 'label_id']
    """
    print(f"📁 Carregando dataset de {path}...")

    # Carregar CSV com tratamento de encoding
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(path, encoding="latin-1")
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="cp1252")

    # Verificar colunas disponíveis
    print(f"📊 Colunas disponíveis: {list(df.columns)}")
    print(f"📊 Shape: {df.shape}")
    print(f"📊 Primeiras linhas:")
    print(df.head())

    # Mapear labels (assumindo coluna 'label' ou 'v1')
    if "label" in df.columns:
        label_col = "label"
    elif "v1" in df.columns:
        label_col = "v1"
    else:
        raise ValueError(
            f"Coluna de label não encontrada. Colunas disponíveis: {list(df.columns)}"
        )

    # Mapear labels de spam/ham para produtivo/improdutivo
    df["label"] = df[label_col].map(LABEL_MAPPING)

    # Remover linhas com labels não mapeados
    df = df.dropna(subset=["label"])

    # Mapear para IDs numéricos
    df["label_id"] = df["label"].map(LABEL2ID)

    # Selecionar coluna de texto (assumindo 'text' ou 'v2')
    if "text" in df.columns:
        text_col = "text"
    elif "v2" in df.columns:
        text_col = "v2"
    else:
        raise ValueError(
            f"Coluna de texto não encontrada. Colunas disponíveis: {list(df.columns)}"
        )

    # Criar dataset final
    dataset = df[[text_col, "label", "label_id"]].copy()
    dataset.columns = ["text", "label", "label_id"]

    # Limpar dados
    dataset = dataset.dropna()
    dataset = dataset[dataset["text"].str.len() > 10]  # Remover textos muito curtos

    print(f"✅ Dataset carregado: {len(dataset)} amostras")
    print(f"📊 Distribuição de labels:")
    print(dataset["label"].value_counts())

    return dataset


def split_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Divide dataset em treino, validação e teste

    Args:
        df: DataFrame com dados

    Returns:
        Tupla com (train_df, val_df, test_df)
    """
    print(f"🔄 Dividindo dataset...")

    # Primeiro split: treino vs (val + test)
    train_df, temp_df = train_test_split(
        df, test_size=(VAL_RATIO + TEST_RATIO), random_state=42, stratify=df["label_id"]
    )

    # Segundo split: validação vs teste
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(TEST_RATIO / (VAL_RATIO + TEST_RATIO)),
        random_state=42,
        stratify=temp_df["label_id"],
    )

    print(f"📊 Divisão:")
    print(f"  - Treino: {len(train_df)} amostras")
    print(f"  - Validação: {len(val_df)} amostras")
    print(f"  - Teste: {len(test_df)} amostras")

    return train_df, val_df, test_df


def save_huggingface_format(df: pd.DataFrame, split_name: str, output_dir: str):
    """
    Salva dataset no formato Hugging Face Datasets

    Args:
        df: DataFrame com dados
        split_name: Nome do split (train, validation, test)
        output_dir: Diretório de saída
    """
    output_path = Path(output_dir) / f"{split_name}.json"

    # Converter para formato JSON
    data = []
    for _, row in df.iterrows():
        data.append(
            {"text": row["text"], "label": row["label_id"], "label_text": row["label"]}
        )

    # Salvar JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvo: {output_path} ({len(data)} amostras)")


def save_model_config(output_dir: str):
    """
    Salva configuração do modelo

    Args:
        output_dir: Diretório de saída
    """
    config = {
        "id2label": ID2LABEL,
        "label2id": LABEL2ID,
        "num_labels": len(ID2LABEL),
        "model_type": "bert",
        "task": "text-classification",
    }

    config_path = Path(output_dir) / "model_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"⚙️ Configuração salva: {config_path}")


def process_sms_dataset(path: str):
    """
    Processa dataset SMS com mapeamento ham=0, spam=1 e divisão treino/teste

    Args:
        path: Caminho para o arquivo spam.csv

    Returns:
        Tupla com (features_train, features_test, labels_train, labels_test, couvec)
    """
    print("📱 Processando dataset SMS...")

    # Carregar dataset
    try:
        sms = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            sms = pd.read_csv(path, encoding="latin-1")
        except UnicodeDecodeError:
            sms = pd.read_csv(path, encoding="cp1252")

    # Mapear labels: ham=0, spam=1
    if "v1" in sms.columns:
        sms["label"] = sms["v1"].map({"ham": 0, "spam": 1})
    elif "label" in sms.columns:
        sms["label"] = sms["label"].map({"ham": 0, "spam": 1})
    else:
        raise ValueError("Coluna de label não encontrada")

    # Selecionar coluna de mensagem
    if "v2" in sms.columns:
        sms["message"] = sms["v2"]
    elif "text" in sms.columns:
        sms["message"] = sms["text"]
    else:
        raise ValueError("Coluna de texto não encontrada")

    print("📊 Distribuição de labels:")
    print(sms.label.value_counts())

    # Dividir em treino e teste (80/20)
    features_train, features_test, labels_train, labels_test = train_test_split(
        sms.message, sms.label, test_size=0.2, random_state=42, stratify=sms.label
    )

    # Criar CountVectorizer
    couvec = CountVectorizer()
    couvec.fit(features_train)

    # Informações sobre características
    trained_features = couvec.get_feature_names_out()
    print(f"📊 Número de características vetorizadas: {len(trained_features)}")
    print(f"📊 Exemplos de características treinadas: {trained_features[1:10]}")

    return features_train, features_test, labels_train, labels_test, couvec


def main():
    """Função principal"""
    print("🚀 Preparando dataset para treinamento...")

    # Criar diretório de saída
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Carregar dataset
    dataset = load_spam_dataset(DATASET_PATH)

    # Dividir dataset
    train_df, val_df, test_df = split_dataset(dataset)

    # Salvar splits
    save_huggingface_format(train_df, "train", OUTPUT_DIR)
    save_huggingface_format(val_df, "validation", OUTPUT_DIR)
    save_huggingface_format(test_df, "test", OUTPUT_DIR)

    # Salvar configuração
    save_model_config(OUTPUT_DIR)

    # Salvar dataset completo para referência
    dataset_path = Path(OUTPUT_DIR) / "dataset_info.json"
    info = {
        "total_samples": len(dataset),
        "train_samples": len(train_df),
        "validation_samples": len(val_df),
        "test_samples": len(test_df),
        "labels": list(ID2LABEL.values()),
        "label_distribution": dataset["label"].value_counts().to_dict(),
    }

    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"📋 Informações do dataset: {dataset_path}")

    print("✅ Dataset preparado com sucesso!")
    print(f"📁 Arquivos salvos em: {OUTPUT_DIR}")
    print("\n📊 Resumo:")
    print(f"  - Total: {len(dataset)} amostras")
    print(f"  - Treino: {len(train_df)} amostras")
    print(f"  - Validação: {len(val_df)} amostras")
    print(f"  - Teste: {len(test_df)} amostras")
    print(f"  - Labels: {list(ID2LABEL.values())}")

    # Processar dataset SMS com as novas configurações
    print("\n🔄 Processando dataset SMS com configurações adicionais...")
    features_train, features_test, labels_train, labels_test, couvec = (
        process_sms_dataset(DATASET_PATH)
    )

    print("✅ Processamento SMS concluído!")


if __name__ == "__main__":
    main()
