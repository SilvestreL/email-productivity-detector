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

# Configurações otimizadas para treinamento completo
MODEL_NAME = "neuralmind/bert-base-portuguese-cased"
DATASET_PATH = "data/processed"
OUTPUT_DIR = "models/email-prod-improd-ptbr-bert"
MAX_LENGTH = 256  # Reduzido para eficiência
BATCH_SIZE = 8  # Otimizado para CPU
LEARNING_RATE = 2e-5
NUM_EPOCHS = 2  # Reduzido para teste mais rápido
EVAL_STEPS = 50  # Frequente para monitoramento
SAVE_STEPS = 100  # Frequente para checkpoints


def load_datasets():
    """Carrega datasets completos"""
    print("📁 Carregando datasets...")

    # Carregar splits
    with open(f"{DATASET_PATH}/train.json", "r") as f:
        train_data = json.load(f)
    with open(f"{DATASET_PATH}/validation.json", "r") as f:
        val_data = json.load(f)
    with open(f"{DATASET_PATH}/test.json", "r") as f:
        test_data = json.load(f)

    # Converter para Dataset
    train_dataset = Dataset.from_list(train_data)
    val_dataset = Dataset.from_list(val_data)
    test_dataset = Dataset.from_list(test_data)

    print(f"📊 Datasets carregados:")
    print(f"  - Treino: {len(train_dataset)} amostras")
    print(f"  - Validação: {len(val_dataset)} amostras")
    print(f"  - Teste: {len(test_dataset)} amostras")

    return train_dataset, val_dataset, test_dataset


def train_model():
    """Executa o treinamento completo"""
    print("🚀 Iniciando treinamento completo...")

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

    # Carregar datasets
    train_dataset, val_dataset, test_dataset = load_datasets()

    # Renomear colunas
    train_dataset = train_dataset.rename_column("label", "labels")
    val_dataset = val_dataset.rename_column("label", "labels")
    test_dataset = test_dataset.rename_column("label", "labels")

    # Tokenizar
    print("🔄 Tokenizando datasets...")

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding=True,
            max_length=MAX_LENGTH,
        )

    train_dataset = train_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text", "label_text"],
    )
    val_dataset = val_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text", "label_text"],
    )
    test_dataset = test_dataset.map(
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
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=2,
        report_to=None,
        seed=42,
    )

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    # Treinar
    print("🚀 Iniciando treinamento...")
    try:
        train_result = trainer.train()
        print("✅ Treinamento concluído com sucesso!")
        print(f"📊 Loss final: {train_result.training_loss:.4f}")

        # Salvar modelo
        print("💾 Salvando modelo...")
        trainer.save_model()
        tokenizer.save_pretrained(OUTPUT_DIR)

        # Avaliar no teste
        print("📊 Avaliando no conjunto de teste...")
        eval_result = trainer.evaluate(test_dataset)
        print(f"📊 Métricas no teste: {eval_result}")

        return True
    except Exception as e:
        print(f"❌ Erro no treinamento: {e}")
        return False


if __name__ == "__main__":
    success = train_model()
    if success:
        print("🎉 Treinamento concluído com sucesso!")
        print(f"📁 Modelo salvo em: {OUTPUT_DIR}")
    else:
        print("💥 Treinamento falhou. Verifique os logs acima.")
