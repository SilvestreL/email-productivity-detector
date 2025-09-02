# Configuração do Modelo Local
MODEL_CONFIG = {
    "name": "BERT PT-BR Fine-tuned para Classificação de Emails",
    "version": "1.0.0",
    "type": "text-classification",
    "labels": ["Improdutivo", "Produtivo"],
    "language": "pt-BR",
    "framework": "transformers",
    "base_model": "neuralmind/bert-base-portuguese-cased",
    "fine_tuned": True,
    "local_path": "models/bert_prod_improd",
    "performance": {
        "expected_accuracy": ">85%",
        "expected_inference_time": "<100ms",
        "max_text_length": 512
    }
}

# Configurações de cache
CACHE_CONFIG = {
    "model_cache": True,
    "tokenizer_cache": True,
    "max_cache_size": "2GB"
}
