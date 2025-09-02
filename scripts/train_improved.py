#!/usr/bin/env python3
"""
Script de treinamento melhorado baseado na solução que funcionou
Adaptado para nosso projeto de classificação de emails
"""

import os
import time
import json
import torch
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
    get_linear_schedule_with_warmup,
)
from torch.optim import AdamW
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch.cuda.amp import GradScaler, autocast

# Configurações
MODEL_NAME = "neuralmind/bert-base-portuguese-cased"
DATASET_PATH = "data/processed"
OUTPUT_DIR = "models/email-prod-improd-ptbr-bert"
MAX_LENGTH = 256
BATCH_SIZE = 8
LEARNING_RATE = 0.0001  # Mesmo LR da solução que funcionou
NUM_EPOCHS = 3  # Mesmo número de épocas
WARMUP_STEPS = 0  # Mesmo warmup da solução

# Configurar dispositivo
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🖥️ Dispositivo: {device}")


def compute_metrics(y_true, y_pred):
    """Computa métricas de avaliação"""
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted'
    )
    return f1, recall, precision, accuracy


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


def create_dataloader(dataset, tokenizer, batch_size=8, shuffle=True):
    """Cria DataLoader personalizado"""
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding=True,
            max_length=MAX_LENGTH,
        )
    
    # Tokenizar
    dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text", "label_text"],
    )
    
    # Renomear coluna
    dataset = dataset.rename_column("label", "labels")
    
    # Criar DataLoader
    from torch.utils.data import DataLoader
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=DataCollatorWithPadding(tokenizer=tokenizer)
    )
    
    return dataloader


def train_epoch(model, dataloader, optimizer, scheduler, scaler, epoch):
    """Treina uma época do modelo"""
    t0 = time.time()
    
    print("")
    print('======== Epoch {:} / {:} ========'.format(epoch + 1, NUM_EPOCHS))
    
    total_loss = 0
    total_f1 = 0
    total_recall = 0
    total_precision = 0
    total_acc = 0
    
    model.train()  # coloca o modelo no modo de treino
    
    for i, batch in enumerate(dataloader):  # itera nos batches de treino
        
        if i % 50 == 0 and not i == 0:  # reportar o progresso a cada 50 batches
            print('  Batch {:>5,}  of  {:>5,}.'.format(i, len(dataloader)))
        
        # Mover para dispositivo
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device).long()
        
        # Limpar gradientes
        optimizer.zero_grad()
        
        # Forward pass
        if device.type == 'cuda':
            with autocast():
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                loss = outputs.loss
                logits = outputs.logits
        else:
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss
            logits = outputs.logits
        
        total_loss += loss.item()
        
        # Backward pass
        if device.type == 'cuda':
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()
        
        scheduler.step()  # update the learning rate
        
        # Calcular métricas
        logits = logits.detach().cpu().numpy()
        rounded_preds = np.argmax(logits, axis=1).flatten()
        
        f1, recall, precision, acc = compute_metrics(
            labels.detach().cpu().numpy(), rounded_preds
        )
        total_f1 += f1
        total_recall += recall
        total_precision += precision
        total_acc += acc
    
    # Calcular médias
    avg_train_loss = total_loss / len(dataloader)
    avg_train_f1 = total_f1 / len(dataloader)
    avg_train_recall = total_recall / len(dataloader)
    avg_train_precision = total_precision / len(dataloader)
    avg_train_acc = total_acc / len(dataloader)
    
    training_time = str(timedelta(seconds=int(round(time.time() - t0))))
    
    print("")
    print("Summary Results")
    print("epoch | loss | acc | recall | f1 | precision | training time")
    print(f"{epoch+1:5d} | {avg_train_loss:.5f} | {avg_train_acc:.5f} | {avg_train_recall:.5f} | {avg_train_f1:.5f} | {avg_train_precision:.5f} | {training_time}")
    
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    
    return {
        'loss': avg_train_loss,
        'accuracy': avg_train_acc,
        'f1': avg_train_f1,
        'precision': avg_train_precision,
        'recall': avg_train_recall
    }


def evaluate_model(model, dataloader):
    """Avalia o modelo"""
    print("📊 Avaliando modelo...")
    
    model.eval()
    total_loss = 0
    total_f1 = 0
    total_recall = 0
    total_precision = 0
    total_acc = 0
    
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device).long()
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            logits = outputs.logits
            
            total_loss += loss.item()
            
            # Calcular métricas
            logits = logits.detach().cpu().numpy()
            rounded_preds = np.argmax(logits, axis=1).flatten()
            
            f1, recall, precision, acc = compute_metrics(
                labels.detach().cpu().numpy(), rounded_preds
            )
            total_f1 += f1
            total_recall += recall
            total_precision += precision
            total_acc += acc
    
    # Calcular médias
    avg_loss = total_loss / len(dataloader)
    avg_f1 = total_f1 / len(dataloader)
    avg_recall = total_recall / len(dataloader)
    avg_precision = total_precision / len(dataloader)
    avg_acc = total_acc / len(dataloader)
    
    print(f"📊 Métricas de avaliação:")
    print(f"  - Loss: {avg_loss:.5f}")
    print(f"  - Accuracy: {avg_acc:.5f}")
    print(f"  - F1: {avg_f1:.5f}")
    print(f"  - Precision: {avg_precision:.5f}")
    print(f"  - Recall: {avg_recall:.5f}")
    
    return {
        'loss': avg_loss,
        'accuracy': avg_acc,
        'f1': avg_f1,
        'precision': avg_precision,
        'recall': avg_recall
    }


def main():
    """Função principal"""
    print("🚀 Iniciando treinamento melhorado...")
    
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
        label2id={"Improdutivo": 0, "Produtivo": 1}
    )
    
    # Mover modelo para dispositivo
    model = model.to(device)
    
    # Carregar datasets
    train_dataset, val_dataset, test_dataset = load_datasets()
    
    # Criar DataLoaders
    print("🔄 Criando DataLoaders...")
    train_dataloader = create_dataloader(train_dataset, tokenizer, BATCH_SIZE, shuffle=True)
    val_dataloader = create_dataloader(val_dataset, tokenizer, BATCH_SIZE, shuffle=False)
    test_dataloader = create_dataloader(test_dataset, tokenizer, BATCH_SIZE, shuffle=False)
    
    # Configurar otimizador e scheduler
    print("⚙️ Configurando otimizador...")
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    
    total_steps = len(train_dataloader) * NUM_EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=WARMUP_STEPS,
        num_training_steps=total_steps
    )
    
    # Configurar scaler para GPU
    scaler = GradScaler() if device.type == 'cuda' else None
    
    print(f"📊 Configuração:")
    print(f"  - Épocas: {NUM_EPOCHS}")
    print(f"  - Batch size: {BATCH_SIZE}")
    print(f"  - Learning rate: {LEARNING_RATE}")
    print(f"  - Total steps: {total_steps}")
    print(f"  - Dispositivo: {device}")
    
    # Treinar
    print("🚀 Iniciando treinamento...")
    training_metrics = []
    
    for epoch in range(NUM_EPOCHS):
        print('Training...')
        epoch_metrics = train_epoch(model, train_dataloader, optimizer, scheduler, scaler, epoch)
        training_metrics.append(epoch_metrics)
    
    # Avaliar no conjunto de validação
    val_metrics = evaluate_model(model, val_dataloader)
    
    # Avaliar no conjunto de teste
    test_metrics = evaluate_model(model, test_dataloader)
    
    # Salvar modelo
    print("💾 Salvando modelo...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    # Salvar métricas
    metrics = {
        "training_metrics": training_metrics,
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
        "config": {
            "model_name": MODEL_NAME,
            "max_length": MAX_LENGTH,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "num_epochs": NUM_EPOCHS,
            "device": str(device)
        }
    }
    
    with open(f"{OUTPUT_DIR}/training_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print("✅ Treinamento concluído com sucesso!")
    print(f"📁 Modelo salvo em: {OUTPUT_DIR}")
    print(f"📊 Métricas finais no teste:")
    print(f"  - Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"  - F1: {test_metrics['f1']:.4f}")
    print(f"  - Precision: {test_metrics['precision']:.4f}")
    print(f"  - Recall: {test_metrics['recall']:.4f}")
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Treinamento concluído com sucesso!")
    else:
        print("💥 Treinamento falhou. Verifique os logs acima.")
