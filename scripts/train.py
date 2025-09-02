#!/usr/bin/env python3
"""
Script para treinamento do modelo de classificação de emails
Fine-tuning de BERT para classificação Produtivo/Improdutivo

Melhorias implementadas:
- Configuração de rótulos no modelo para evitar "LABEL_0/1" na inferência
- TrainingArguments otimizados com evaluation por época, scheduler linear e AMP
- Métricas macro (mais justas com desbalanceamento) com zero_division=0
- WeightedTrainer opcional para datasets desbalanceados com class weights
"""

import json
import os
import torch
import logging
import time
import psutil
import gc
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
    DataCollatorWithPadding,
    TrainerCallback,
)
from datasets import Dataset, load_dataset
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)
import numpy as np
import pandas as pd
from huggingface_hub import HfApi, login
import warnings

warnings.filterwarnings("ignore")

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("training.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class TrainingStage:
    """Enum para rastrear stages do treinamento"""

    INIT = "INIT"
    LOADING_MODEL = "LOADING_MODEL"
    LOADING_DATA = "LOADING_DATA"
    PREPARING_DATA = "PREPARING_DATA"
    SETTING_UP_TRAINER = "SETTING_UP_TRAINER"
    TRAINING = "TRAINING"
    EVALUATING = "EVALUATING"
    SAVING = "SAVING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class SystemMonitor:
    """Monitor de recursos do sistema"""

    @staticmethod
    def get_memory_info():
        """Retorna informações de memória"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent,
        }

    @staticmethod
    def get_gpu_info():
        """Retorna informações da GPU se disponível"""
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            gpu_allocated = torch.cuda.memory_allocated(0)
            gpu_cached = torch.cuda.memory_reserved(0)
            return {
                "available": True,
                "name": torch.cuda.get_device_name(0),
                "total_gb": round(gpu_memory / (1024**3), 2),
                "allocated_gb": round(gpu_allocated / (1024**3), 2),
                "cached_gb": round(gpu_cached / (1024**3), 2),
                "free_gb": round((gpu_memory - gpu_allocated) / (1024**3), 2),
            }
        return {"available": False}

    @staticmethod
    def log_system_status(stage: str):
        """Log do status do sistema"""
        memory = SystemMonitor.get_memory_info()
        gpu = SystemMonitor.get_gpu_info()

        logger.info(f"🖥️ [{stage}] Sistema:")
        logger.info(
            f"   RAM: {memory['used_gb']:.1f}GB/{memory['total_gb']:.1f}GB ({memory['percent']:.1f}%)"
        )

        if gpu["available"]:
            logger.info(f"   GPU: {gpu['name']}")
            logger.info(
                f"   GPU Mem: {gpu['allocated_gb']:.1f}GB/{gpu['total_gb']:.1f}GB (Livre: {gpu['free_gb']:.1f}GB)"
            )
        else:
            logger.info("   GPU: Não disponível")

    @staticmethod
    def cleanup_memory():
        """Limpa memória e executa garbage collection"""
        logger.info("🧹 Limpando memória...")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("   ✅ Cache da GPU limpo")
        logger.info("   ✅ Garbage collection executado")


class WeightedTrainer(Trainer):
    """Trainer customizado com suporte a class weights para datasets desbalanceados"""

    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        if self.class_weights is not None:
            import torch.nn.functional as F
            import torch

            w = torch.tensor(
                self.class_weights, device=logits.device, dtype=logits.dtype
            )
            loss = F.cross_entropy(logits, labels, weight=w)
        else:
            loss = torch.nn.functional.cross_entropy(logits, labels)

        return (loss, outputs) if return_outputs else loss


# Configurações
MODEL_NAME = "neuralmind/bert-base-portuguese-cased"  # BERT em português
DATASET_PATH = "data/processed"
OUTPUT_DIR = "models/email-prod-improd-ptbr-bert"
HUB_MODEL_ID = "SEU_USUARIO/email-prod-improd-ptbr-bert"  # Troque pelo seu username
MAX_LENGTH = 512
BATCH_SIZE = 8  # Reduzido para evitar problemas de memória
LEARNING_RATE = 2e-5
NUM_EPOCHS = 2  # Reduzido para teste mais rápido
EVAL_STEPS = 50  # Reduzido para mais feedback
SAVE_STEPS = 100  # Reduzido para mais checkpoints
WARMUP_STEPS = 50  # Reduzido


class ProgressCallback(TrainerCallback):
    """Callback para monitorar progresso do treinamento com logs detalhados"""

    def __init__(self):
        self.start_time = time.time()
        self.last_log_time = time.time()

    def on_train_begin(self, args, state, control, **kwargs):
        logger.info(f"🚀 [{TrainingStage.TRAINING}] Iniciando treinamento")
        logger.info(f"   Épocas: {args.num_train_epochs}")
        logger.info(f"   Batch size: {args.per_device_train_batch_size}")
        logger.info(f"   Learning rate: {args.learning_rate}")
        SystemMonitor.log_system_status(TrainingStage.TRAINING)

    def on_step_begin(self, args, state, control, **kwargs):
        current_time = time.time()
        if (
            state.global_step % 10 == 0 or (current_time - self.last_log_time) > 30
        ):  # A cada 10 steps ou 30s
            progress = (state.global_step / state.max_steps) * 100
            elapsed = current_time - self.start_time
            eta = (
                (elapsed / state.global_step) * (state.max_steps - state.global_step)
                if state.global_step > 0
                else 0
            )

            logger.info(
                f"🔄 [{TrainingStage.TRAINING}] Step {state.global_step}/{state.max_steps} ({progress:.1f}%)"
            )
            logger.info(f"   Epoch: {state.epoch:.2f}")
            logger.info(f"   Tempo decorrido: {elapsed/60:.1f}min")
            logger.info(f"   ETA: {eta/60:.1f}min")

            # Log de memória a cada 50 steps
            if state.global_step % 50 == 0:
                SystemMonitor.log_system_status(TrainingStage.TRAINING)

            self.last_log_time = current_time

    def on_evaluate(self, args, state, control, **kwargs):
        logger.info(
            f"📊 [{TrainingStage.EVALUATING}] Avaliação concluída no step {state.global_step}"
        )
        SystemMonitor.log_system_status(TrainingStage.EVALUATING)

    def on_save(self, args, state, control, **kwargs):
        logger.info(
            f"💾 [{TrainingStage.SAVING}] Checkpoint salvo no step {state.global_step}"
        )
        SystemMonitor.log_system_status(TrainingStage.SAVING)

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            # Log das métricas de treinamento
            if "loss" in logs:
                logger.info(f"📈 Loss: {logs['loss']:.4f}")
            if "learning_rate" in logs:
                logger.info(f"📈 Learning Rate: {logs['learning_rate']:.2e}")

    def on_train_end(self, args, state, control, **kwargs):
        total_time = time.time() - self.start_time
        logger.info(
            f"✅ [{TrainingStage.COMPLETED}] Treinamento concluído em {total_time/60:.1f} minutos"
        )
        SystemMonitor.log_system_status(TrainingStage.COMPLETED)


@dataclass
class ModelConfig:
    """Configuração do modelo"""

    model_name: str = MODEL_NAME
    max_length: int = MAX_LENGTH
    num_labels: int = 2
    id2label: Dict[int, str] = field(
        default_factory=lambda: {0: "Improdutivo", 1: "Produtivo"}
    )
    label2id: Dict[str, int] = field(
        default_factory=lambda: {"Improdutivo": 0, "Produtivo": 1}
    )


class EmailClassifierTrainer:
    """Classe para treinamento do classificador de emails"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.trainer = None

    def load_tokenizer_and_model(self):
        """Carrega tokenizer e modelo"""
        logger.info(
            f"🤖 [{TrainingStage.LOADING_MODEL}] Carregando modelo: {self.config.model_name}"
        )
        SystemMonitor.log_system_status(TrainingStage.LOADING_MODEL)

        try:
            start_time = time.time()

            # Tokenizer
            logger.info("   Carregando tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            logger.info("   ✅ Tokenizer carregado")

            # Modelo
            logger.info("   Carregando modelo...")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.config.model_name,
                num_labels=self.config.num_labels,
                id2label=self.config.id2label,
                label2id=self.config.label2id,
            )

            # Configurar rótulos no modelo para evitar "LABEL_0/1" na inferência
            self.model.config.label2id = self.config.label2id
            self.model.config.id2label = self.config.id2label

            load_time = time.time() - start_time
            logger.info(f"   ✅ Modelo carregado em {load_time:.1f}s")

            # Log de informações do modelo
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(
                p.numel() for p in self.model.parameters() if p.requires_grad
            )
            logger.info(f"   📊 Parâmetros totais: {total_params:,}")
            logger.info(f"   📊 Parâmetros treináveis: {trainable_params:,}")

            SystemMonitor.log_system_status(TrainingStage.LOADING_MODEL)
            SystemMonitor.cleanup_memory()

        except Exception as e:
            logger.error(f"❌ [{TrainingStage.ERROR}] Erro ao carregar modelo: {e}")
            SystemMonitor.cleanup_memory()
            raise

    def load_dataset(self) -> Tuple[Dataset, Dataset, Dataset]:
        """Carrega dataset preparado"""
        logger.info(
            f"📁 [{TrainingStage.LOADING_DATA}] Carregando dataset de {DATASET_PATH}"
        )
        SystemMonitor.log_system_status(TrainingStage.LOADING_DATA)

        try:
            start_time = time.time()

            # Carregar splits
            logger.info("   Carregando split de treino...")
            train_data = self._load_json_dataset(f"{DATASET_PATH}/train.json")
            logger.info(f"   ✅ Treino: {len(train_data)} amostras")

            logger.info("   Carregando split de validação...")
            val_data = self._load_json_dataset(f"{DATASET_PATH}/validation.json")
            logger.info(f"   ✅ Validação: {len(val_data)} amostras")

            logger.info("   Carregando split de teste...")
            test_data = self._load_json_dataset(f"{DATASET_PATH}/test.json")
            logger.info(f"   ✅ Teste: {len(test_data)} amostras")

            # Converter para Dataset do Hugging Face
            logger.info("   Convertendo para Dataset do Hugging Face...")
            train_dataset = Dataset.from_list(train_data)
            val_dataset = Dataset.from_list(val_data)
            test_dataset = Dataset.from_list(test_data)

            load_time = time.time() - start_time
            logger.info(f"   ✅ Dataset convertido em {load_time:.1f}s")

            # Log de distribuição de classes
            train_labels = [item["label"] for item in train_data]
            val_labels = [item["label"] for item in val_data]
            test_labels = [item["label"] for item in test_data]

            logger.info(f"📊 [{TrainingStage.LOADING_DATA}] Distribuição de classes:")
            logger.info(
                f"   Treino: {dict(zip(*np.unique(train_labels, return_counts=True)))}"
            )
            logger.info(
                f"   Validação: {dict(zip(*np.unique(val_labels, return_counts=True)))}"
            )
            logger.info(
                f"   Teste: {dict(zip(*np.unique(test_labels, return_counts=True)))}"
            )

            SystemMonitor.log_system_status(TrainingStage.LOADING_DATA)

            return train_dataset, val_dataset, test_dataset

        except Exception as e:
            logger.error(f"❌ [{TrainingStage.ERROR}] Erro ao carregar dataset: {e}")
            raise

    def _load_json_dataset(self, path: str) -> List[Dict]:
        """Carrega dataset de arquivo JSON"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def tokenize_function(self, examples):
        """Função de tokenização"""
        return self.tokenizer(
            examples["text"],
            truncation=True,
            padding=True,
            max_length=self.config.max_length,
        )

    def prepare_datasets(self, train_dataset, val_dataset, test_dataset):
        """Prepara datasets para treinamento"""
        logger.info(f"🔄 [{TrainingStage.PREPARING_DATA}] Tokenizando datasets...")
        SystemMonitor.log_system_status(TrainingStage.PREPARING_DATA)

        try:
            start_time = time.time()

            # Renomear coluna label para labels (requerido pelo Hugging Face)
            logger.info("   Renomeando colunas...")
            train_dataset = train_dataset.rename_column("label", "labels")
            val_dataset = val_dataset.rename_column("label", "labels")
            test_dataset = test_dataset.rename_column("label", "labels")
            logger.info("   ✅ Colunas renomeadas")

            # Tokenizar (manter coluna labels)
            logger.info("   Tokenizando dataset de treino...")
            train_dataset = train_dataset.map(
                self.tokenize_function,
                batched=True,
                remove_columns=["text", "label_text"],
            )
            logger.info(f"   ✅ Treino tokenizado: {len(train_dataset)} amostras")

            logger.info("   Tokenizando dataset de validação...")
            val_dataset = val_dataset.map(
                self.tokenize_function,
                batched=True,
                remove_columns=["text", "label_text"],
            )
            logger.info(f"   ✅ Validação tokenizada: {len(val_dataset)} amostras")

            logger.info("   Tokenizando dataset de teste...")
            test_dataset = test_dataset.map(
                self.tokenize_function,
                batched=True,
                remove_columns=["text", "label_text"],
            )
            logger.info(f"   ✅ Teste tokenizado: {len(test_dataset)} amostras")

            tokenize_time = time.time() - start_time
            logger.info(f"   ✅ Tokenização concluída em {tokenize_time:.1f}s")

            # Log de informações dos datasets tokenizados
            logger.info(
                f"📊 [{TrainingStage.PREPARING_DATA}] Informações dos datasets:"
            )
            logger.info(
                f"   Treino: {train_dataset.num_rows} amostras, {len(train_dataset.column_names)} colunas"
            )
            logger.info(
                f"   Validação: {val_dataset.num_rows} amostras, {len(val_dataset.column_names)} colunas"
            )
            logger.info(
                f"   Teste: {test_dataset.num_rows} amostras, {len(test_dataset.column_names)} colunas"
            )

            SystemMonitor.log_system_status(TrainingStage.PREPARING_DATA)
            SystemMonitor.cleanup_memory()

            return train_dataset, val_dataset, test_dataset

        except Exception as e:
            logger.error(f"❌ [{TrainingStage.ERROR}] Erro ao preparar datasets: {e}")
            SystemMonitor.cleanup_memory()
            raise

    def compute_metrics(self, eval_pred):
        """Computa métricas de avaliação com média macro (mais justa com desbalanceamento)"""
        logits, y_true = eval_pred
        y_pred = logits.argmax(axis=1)

        # Métricas com média macro e zero_division=0 para evitar warnings
        acc = accuracy_score(y_true, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="macro", zero_division=0
        )

        return {"accuracy": acc, "precision": p, "recall": r, "f1": f1}

    def setup_trainer(self, train_dataset, val_dataset, use_class_weights=False):
        """Configura o trainer"""
        logger.info(f"⚙️ [{TrainingStage.SETTING_UP_TRAINER}] Configurando trainer...")
        SystemMonitor.log_system_status(TrainingStage.SETTING_UP_TRAINER)

        # Argumentos de treinamento otimizados
        training_args = TrainingArguments(
            output_dir=OUTPUT_DIR,
            num_train_epochs=3,  # Aumentado para melhor convergência
            per_device_train_batch_size=8,
            per_device_eval_batch_size=16,
            gradient_accumulation_steps=2,
            learning_rate=2e-5,
            weight_decay=0.01,
            lr_scheduler_type="linear",  # Scheduler linear
            warmup_ratio=0.06,  # Warmup como proporção
            eval_strategy="epoch",  # Avaliação por época
            save_strategy="epoch",  # Salvamento por época
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            fp16=torch.cuda.is_available(),  # AMP quando disponível
            gradient_checkpointing=True,  # Para economizar memória
            report_to=None,
            seed=42,
            data_seed=42,
            save_total_limit=2,
            logging_steps=50,
        )

        # Data collator
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)

        # Callbacks
        callbacks = [
            EarlyStoppingCallback(early_stopping_patience=3),
            ProgressCallback(),
        ]

        # Calcular class weights se solicitado
        trainer_class = Trainer
        trainer_kwargs = {}

        if use_class_weights:
            print("⚖️ Calculando class weights para dataset desbalanceado...")
            counts = np.bincount(train_dataset["labels"])
            freq = counts / counts.sum()
            class_weights = 1.0 / (freq + 1e-9)
            class_weights = class_weights / class_weights.sum() * len(counts)

            trainer_class = WeightedTrainer
            trainer_kwargs = {"class_weights": class_weights.tolist()}
            print(f"📊 Class weights: {class_weights.tolist()}")

        # Trainer
        self.trainer = trainer_class(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
            callbacks=callbacks,
            **trainer_kwargs,
        )

        logger.info(f"✅ [{TrainingStage.SETTING_UP_TRAINER}] Trainer configurado")
        logger.info(f"   Tipo: {trainer_class.__name__}")
        logger.info(f"   Épocas: {training_args.num_train_epochs}")
        logger.info(f"   Batch size: {training_args.per_device_train_batch_size}")
        logger.info(f"   Learning rate: {training_args.learning_rate}")
        logger.info(f"   Output dir: {training_args.output_dir}")
        SystemMonitor.log_system_status(TrainingStage.SETTING_UP_TRAINER)

    def train(self):
        """Executa o treinamento"""
        logger.info(f"🚀 [{TrainingStage.TRAINING}] Iniciando treinamento...")
        logger.info(f"📊 Configuração:")
        logger.info(f"  - Épocas: {self.trainer.args.num_train_epochs}")
        logger.info(f"  - Batch size: {self.trainer.args.per_device_train_batch_size}")
        logger.info(f"  - Learning rate: {self.trainer.args.learning_rate}")
        logger.info(f"  - Max length: {self.config.max_length}")
        logger.info(f"  - Evaluation strategy: {self.trainer.args.eval_strategy}")
        logger.info(f"  - Save strategy: {self.trainer.args.save_strategy}")

        SystemMonitor.log_system_status(TrainingStage.TRAINING)

        try:
            # Treinar
            logger.info("🔄 Iniciando loop de treinamento...")
            train_result = self.trainer.train()

            # Salvar modelo
            logger.info(f"💾 [{TrainingStage.SAVING}] Salvando modelo...")
            self.trainer.save_model()
            self.tokenizer.save_pretrained(OUTPUT_DIR)
            logger.info("✅ Modelo salvo com sucesso")

            logger.info("✅ Treinamento concluído!")
            logger.info(f"📊 Métricas finais de treinamento:")
            for key, value in train_result.metrics.items():
                logger.info(f"  - {key}: {value:.4f}")

            return train_result

        except Exception as e:
            logger.error(f"❌ [{TrainingStage.ERROR}] Erro durante treinamento: {e}")
            logger.error(f"   Tipo do erro: {type(e).__name__}")
            logger.error(f"   Detalhes: {str(e)}")
            SystemMonitor.log_system_status(TrainingStage.ERROR)
            raise

    def evaluate(self, test_dataset):
        """Avalia o modelo no conjunto de teste"""
        logger.info(
            f"📊 [{TrainingStage.EVALUATING}] Avaliando modelo no conjunto de teste..."
        )
        logger.info(f"   Dataset de teste: {len(test_dataset)} amostras")
        SystemMonitor.log_system_status(TrainingStage.EVALUATING)

        try:
            # Avaliar
            eval_result = self.trainer.evaluate(test_dataset)

            logger.info("✅ Avaliação concluída!")
            logger.info(f"📊 Métricas no conjunto de teste:")
            for key, value in eval_result.items():
                if isinstance(value, float):
                    logger.info(f"  - {key}: {value:.4f}")

            return eval_result

        except Exception as e:
            logger.error(f"❌ [{TrainingStage.ERROR}] Erro durante avaliação: {e}")
            logger.error(f"   Tipo do erro: {type(e).__name__}")
            logger.error(f"   Detalhes: {str(e)}")
            SystemMonitor.log_system_status(TrainingStage.ERROR)
            raise

    def predict_sample(self, text: str) -> Dict:
        """Faz predição em uma amostra"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=self.config.max_length,
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        predicted_id = torch.argmax(predictions, dim=-1).item()
        confidence = predictions[0][predicted_id].item()
        predicted_label = self.config.id2label[predicted_id]

        return {
            "text": text,
            "predicted_label": predicted_label,
            "confidence": confidence,
            "scores": {
                self.config.id2label[i]: predictions[0][i].item()
                for i in range(self.config.num_labels)
            },
        }


def upload_to_hub(model_path: str, hub_model_id: str):
    """Faz upload do modelo para o Hugging Face Hub"""
    print(f"☁️ Fazendo upload para {hub_model_id}...")

    try:
        api = HfApi()
        api.create_repo(repo_id=hub_model_id, exist_ok=True)
        api.upload_folder(
            folder_path=model_path,
            repo_id=hub_model_id,
            commit_message="Upload do modelo fine-tuned para classificação de emails",
        )
        print(f"✅ Modelo enviado para: https://huggingface.co/{hub_model_id}")
    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        print("💡 Certifique-se de estar logado no Hugging Face Hub:")
        print("   huggingface-cli login")


def main():
    """Função principal"""
    logger.info(
        f"🚀 [{TrainingStage.INIT}] Iniciando treinamento do classificador de emails..."
    )
    SystemMonitor.log_system_status(TrainingStage.INIT)

    try:
        # Verificar se dataset existe
        if not os.path.exists(DATASET_PATH):
            logger.error(
                f"❌ [{TrainingStage.ERROR}] Dataset não encontrado em {DATASET_PATH}"
            )
            logger.error("💡 Execute primeiro: python scripts/prepare_dataset.py")
            return

        # Verificar GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🖥️ Dispositivo: {device}")

        if torch.cuda.is_available():
            logger.info(f"   GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"   CUDA Version: {torch.version.cuda}")
        else:
            logger.warning("   ⚠️ GPU não disponível, usando CPU")

        # Configuração
        logger.info("⚙️ Criando configuração do modelo...")
        config = ModelConfig()
        logger.info(f"   Modelo: {config.model_name}")
        logger.info(f"   Max length: {config.max_length}")
        logger.info(f"   Labels: {config.id2label}")

        # Inicializar trainer
        logger.info("🏗️ Inicializando trainer...")
        trainer = EmailClassifierTrainer(config)

        # Carregar modelo e tokenizer
        trainer.load_tokenizer_and_model()

        # Carregar datasets
        train_dataset, val_dataset, test_dataset = trainer.load_dataset()

        # Preparar datasets
        train_dataset, val_dataset, test_dataset = trainer.prepare_datasets(
            train_dataset, val_dataset, test_dataset
        )

        # Configurar trainer (com class weights se dataset estiver desbalanceado)
        # Para ativar class weights, mude para: trainer.setup_trainer(train_dataset, val_dataset, use_class_weights=True)
        trainer.setup_trainer(train_dataset, val_dataset, use_class_weights=False)

        # Treinar
        train_result = trainer.train()

        # Avaliar
        eval_result = trainer.evaluate(test_dataset)

        # Teste com amostras
        logger.info("\n🧪 Testando modelo com amostras...")
        test_samples = [
            "Preciso de uma reunião para discutir o projeto da próxima semana",
            "Obrigado pelo email, vou verificar e retornar em breve",
            "Promoção imperdível! Desconto de 50% apenas hoje!",
            "Envio em anexo o relatório mensal solicitado",
        ]

        for sample in test_samples:
            result = trainer.predict_sample(sample)
            logger.info(
                f"📧 '{sample[:50]}...' → {result['predicted_label']} ({result['confidence']:.2%})"
            )

        # Salvar métricas
        logger.info("💾 Salvando métricas...")
        metrics_path = Path(OUTPUT_DIR) / "training_metrics.json"
        metrics = {
            "training_metrics": train_result.metrics,
            "evaluation_metrics": eval_result,
            "model_config": {
                "model_name": config.model_name,
                "max_length": config.max_length,
                "num_labels": config.num_labels,
                "id2label": config.id2label,
                "label2id": config.label2id,
            },
            "training_config": {
                "batch_size": trainer.trainer.args.per_device_train_batch_size,
                "learning_rate": trainer.trainer.args.learning_rate,
                "num_epochs": trainer.trainer.args.num_train_epochs,
                "max_length": config.max_length,
            },
        }

        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

        logger.info(f"📊 Métricas salvas em: {metrics_path}")

        # Upload para Hub (opcional)
        if HUB_MODEL_ID != "SEU_USUARIO/email-prod-improd-ptbr-bert":
            upload_to_hub(OUTPUT_DIR, HUB_MODEL_ID)
        else:
            logger.info(
                "💡 Para fazer upload para o Hub, configure HUB_MODEL_ID no script"
            )

        logger.info("\n✅ Treinamento concluído com sucesso!")
        logger.info(f"📁 Modelo salvo em: {OUTPUT_DIR}")
        logger.info(f"🔗 Para usar no app.py, configure MODEL_ID = '{HUB_MODEL_ID}'")

    except Exception as e:
        logger.error(f"❌ [{TrainingStage.ERROR}] Erro crítico durante execução: {e}")
        logger.error(f"   Tipo do erro: {type(e).__name__}")
        logger.error(f"   Detalhes: {str(e)}")
        SystemMonitor.log_system_status(TrainingStage.ERROR)

        # Tentar salvar logs de erro
        try:
            error_log_path = Path(OUTPUT_DIR) / "error_log.json"
            error_log = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": time.time(),
                "system_info": {
                    "memory": SystemMonitor.get_memory_info(),
                    "gpu": SystemMonitor.get_gpu_info(),
                },
            }
            with open(error_log_path, "w", encoding="utf-8") as f:
                json.dump(error_log, f, ensure_ascii=False, indent=2)
            logger.info(f"📝 Log de erro salvo em: {error_log_path}")
        except:
            pass

        raise


if __name__ == "__main__":
    main()
