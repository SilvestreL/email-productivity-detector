"""
API REST para Email Productivity Classifier
AutoU - Teste Técnico
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import joblib
import pandas as pd
import numpy as np
import sys
import os
import io
import traceback

# Adiciona o diretório src ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from response_generator import ResponseGenerator
from file_processor import FileProcessor

# Configuração da API
app = FastAPI(
    title="Email Productivity Classifier API",
    description="API para classificação de emails em produtivos ou improdutivos com geração de respostas automáticas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic
class EmailRequest(BaseModel):
    """Modelo para requisição de classificação de email"""

    content: str
    subject: Optional[str] = None
    sender: Optional[str] = None


class EmailResponse(BaseModel):
    """Modelo para resposta da classificação"""

    is_productive: bool
    confidence: float
    probabilities: Dict[str, float]
    response_type: str
    detected_categories: List[str]
    suggested_response: str
    processing_time: float


class HealthResponse(BaseModel):
    """Modelo para resposta de health check"""

    status: str
    model_loaded: bool
    version: str
    uptime: float


class BatchRequest(BaseModel):
    """Modelo para classificação em lote"""

    emails: List[EmailRequest]


class BatchResponse(BaseModel):
    """Modelo para resposta de classificação em lote"""

    results: List[EmailResponse]
    total_processed: int
    processing_time: float


# Variáveis globais
model = None
response_generator = None
file_processor = None
start_time = None


def load_model():
    """Carrega o modelo treinado"""
    global model, response_generator, file_processor, start_time
    try:
        # Carrega o modelo
        model_path = os.path.join(
            os.path.dirname(__file__), "..", "models", "email_spam_pipeline.joblib"
        )
        model = joblib.load(model_path)

        # Inicializa os componentes
        response_generator = ResponseGenerator()
        file_processor = FileProcessor()

        print("✅ Modelo carregado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {str(e)}")
        return False


def classify_email(content: str) -> Dict[str, Any]:
    """Classifica um email e retorna os resultados"""
    try:
        # Faz a predição
        prediction = model.predict([content])[0]
        probabilities = model.predict_proba([content])[0]

        # Converte para formato legível
        is_productive = prediction == 1
        confidence = max(probabilities)

        # Gera resposta automática
        response_summary = response_generator.get_response_summary(
            content, is_productive, confidence
        )

        return {
            "is_productive": is_productive,
            "confidence": confidence,
            "probabilities": {
                "improdutivo": float(probabilities[0]),
                "produtivo": float(probabilities[1]),
            },
            "response_type": response_summary["response_type"],
            "detected_categories": response_summary["detected_categories"],
            "suggested_response": response_summary["response"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na classificação: {str(e)}")


# Eventos da aplicação
@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da API"""
    global start_time
    import time

    start_time = time.time()

    if not load_model():
        raise Exception("Falha ao carregar o modelo")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da API"""
    print("🛑 API encerrada")


# Rotas da API
@app.get("/", response_model=Dict[str, str])
async def root():
    """Rota raiz da API"""
    return {
        "message": "Email Productivity Classifier API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check da API"""
    import time

    uptime = time.time() - start_time if start_time else 0

    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        version="1.0.0",
        uptime=uptime,
    )


@app.post("/classify", response_model=EmailResponse)
async def classify_single_email(request: EmailRequest):
    """Classifica um único email"""
    import time

    start_time_classification = time.time()

    try:
        # Valida o conteúdo
        if not request.content or len(request.content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Conteúdo do email deve ter pelo menos 10 caracteres",
            )

        # Classifica o email
        result = classify_email(request.content)

        # Calcula tempo de processamento
        processing_time = time.time() - start_time_classification

        return EmailResponse(**result, processing_time=processing_time)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.post("/classify/batch", response_model=BatchResponse)
async def classify_batch_emails(request: BatchRequest):
    """Classifica múltiplos emails em lote"""
    import time

    start_time_batch = time.time()

    try:
        results = []

        for email_request in request.emails:
            # Valida o conteúdo
            if not email_request.content or len(email_request.content.strip()) < 10:
                results.append(
                    EmailResponse(
                        is_productive=False,
                        confidence=0.0,
                        probabilities={"improdutivo": 1.0, "produtivo": 0.0},
                        response_type="erro",
                        detected_categories=["erro_validação"],
                        suggested_response="Erro: Conteúdo inválido",
                        processing_time=0.0,
                    )
                )
                continue

            # Classifica o email
            result = classify_email(email_request.content)
            results.append(EmailResponse(**result, processing_time=0.0))

        # Calcula tempo total
        total_processing_time = time.time() - start_time_batch

        return BatchResponse(
            results=results,
            total_processed=len(results),
            processing_time=total_processing_time,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro no processamento em lote: {str(e)}"
        )


@app.post("/classify/file")
async def classify_file(
    file: UploadFile = File(...), include_response: bool = Form(True)
):
    """Classifica email a partir de arquivo (.txt ou .pdf)"""
    import time

    start_time_file = time.time()

    try:
        # Valida o arquivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Arquivo não fornecido")

        # Lê o conteúdo do arquivo
        file_content = await file.read()

        # Processa o arquivo
        success, extracted_text, file_name = file_processor.process_uploaded_file(
            type("MockFile", (), {"content": file_content, "name": file.filename})()
        )

        if not success:
            raise HTTPException(
                status_code=400, detail=f"Erro ao processar arquivo: {extracted_text}"
            )

        # Valida o conteúdo extraído
        is_valid, validation_message = file_processor.validate_email_content(
            extracted_text
        )
        if not is_valid:
            raise HTTPException(
                status_code=400, detail=f"Conteúdo inválido: {validation_message}"
            )

        # Classifica o email
        result = classify_email(extracted_text)

        # Calcula tempo de processamento
        processing_time = time.time() - start_time_file

        # Informações do arquivo
        file_info = file_processor.get_file_info(file_name, extracted_text)

        response_data = {
            "file_info": {
                "name": file_name,
                "size": len(file_content),
                "word_count": file_info["word_count"],
                "line_count": file_info["line_count"],
            },
            "classification": {
                "is_productive": result["is_productive"],
                "confidence": result["confidence"],
                "probabilities": result["probabilities"],
            },
            "processing_time": processing_time,
        }

        # Adiciona resposta automática se solicitado
        if include_response:
            response_data["response"] = {
                "type": result["response_type"],
                "categories": result["detected_categories"],
                "suggested_response": result["suggested_response"],
            }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar arquivo: {str(e)}"
        )


@app.get("/model/info")
async def get_model_info():
    """Retorna informações sobre o modelo"""
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Modelo não carregado")

        # Informações básicas do modelo
        model_info = {
            "type": type(model).__name__,
            "features": getattr(model, "n_features_in_", "N/A"),
            "classes": (
                getattr(model, "classes_", []).tolist()
                if hasattr(model, "classes_")
                else []
            ),
            "loaded": True,
        }

        return model_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao obter informações do modelo: {str(e)}"
        )


@app.post("/test")
async def test_classification():
    """Rota de teste com exemplo"""
    test_email = {
        "content": "Olá, estou com um problema técnico no sistema. Não consigo fazer login e preciso de ajuda urgente.",
        "subject": "Problema Técnico",
        "sender": "usuario@empresa.com",
    }

    try:
        result = classify_email(test_email["content"])

        return {
            "test_email": test_email,
            "classification": result,
            "message": "Teste realizado com sucesso!",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no teste: {str(e)}")


# Tratamento de erros
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc),
            "type": type(exc).__name__,
        },
    )


if __name__ == "__main__":
    # Executa a API
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
