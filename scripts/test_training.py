#!/usr/bin/env python3
"""
Script de teste rápido para verificar se o treinamento funciona
Usa um dataset menor e configurações mínimas
"""

import os
import torch
from pathlib import Path
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
from datasets import Dataset
import json

# Configurações mínimas para teste
MODEL_NAME = "neuralmind/bert-base-portuguese-cased"
DATASET_PATH = "data/processed"
OUTPUT_DIR = "models/test-model"
MAX_LENGTH = 128  # Reduzido para teste
BATCH_SIZE = 4  # Muito pequeno para teste
LEARNING_RATE = 2e-5
NUM_EPOCHS = 1  # Apenas 1 época para teste
EVAL_STEPS = 10  # Muito frequente para teste
SAVE_STEPS = 20  # Muito frequente para teste


def create_test_dataset():
    """Cria um dataset pequeno para teste"""
    print("🧪 Criando dataset de teste...")

    # Carregar apenas algumas amostras
    with open(f"{DATASET_PATH}/train.json", "r") as f:
        data = json.load(f)

    # Usar apenas 100 amostras para teste
    test_data = data[:100]

    # Converter para Dataset
    dataset = Dataset.from_list(test_data)

    print(f"📊 Dataset de teste criado: {len(dataset)} amostras")
    return dataset


def test_training():
    """Testa o treinamento com configurações mínimas"""
    print("🚀 Iniciando teste de treinamento...")

    # Verificar se dataset existe
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Dataset não encontrado em {DATASET_PATH}")
        return False

    # Criar diretório de saída
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Carregar modelo e tokenizer
    print("🤖 Carregando modelo...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2,
        id2label={0: "Improdutivo", 1: "Produtivo"},
        label2id={"Improdutivo": 0, "Produtivo": 1},
    )

    # Criar dataset de teste
    dataset = create_test_dataset()

    # Renomear coluna
    dataset = dataset.rename_column("label", "labels")

    # Tokenizar
    print("🔄 Tokenizando dataset...")

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding=True,
            max_length=MAX_LENGTH,
        )

    dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text", "label_text"],
    )

    # Configurar trainer
    print("⚙️ Configurando trainer...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=1,
        report_to=None,
        seed=42,
    )

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        eval_dataset=dataset,  # Usar mesmo dataset para teste
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    # Testar treinamento
    print("🚀 Iniciando treinamento de teste...")
    try:
        train_result = trainer.train()
        print("✅ Treinamento de teste concluído com sucesso!")
        print(f"📊 Loss final: {train_result.training_loss:.4f}")
        return True
    except Exception as e:
        print(f"❌ Erro no treinamento: {e}")
        return False


if __name__ == "__main__":
    success = test_training()
    if success:
        print("🎉 Teste de treinamento passou! O treinamento completo deve funcionar.")
    else:
        print("💥 Teste de treinamento falhou. Verifique os logs acima.")
