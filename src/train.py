# src/train.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os
import re


def load_and_prepare_data():
    """Carrega e prepara os dados do dataset"""
    print("📊 Carregando dataset...")

    # Carrega o dataset
    df = pd.read_csv("data/spam.csv", encoding="latin-1")

    # Renomeia as colunas para facilitar o uso
    df.columns = ["label", "message", "col3", "col4", "col5"]

    # Remove colunas desnecessárias
    df = df[["label", "message"]]

    # Remove linhas com valores nulos
    df = df.dropna()

    # Converte labels para binário (ham=0, spam=1)
    df["label_binary"] = (df["label"] == "spam").astype(int)

    # Adiciona features de engenharia
    df = add_text_features(df)

    print(f"✅ Dataset carregado: {len(df)} mensagens")
    print(f"📈 Distribuição: {df['label'].value_counts().to_dict()}")

    return df


def add_text_features(df):
    """Adiciona features de engenharia para melhorar a classificação"""

    # Converte para minúsculas
    df["message_lower"] = df["message"].str.lower()

    # Conta caracteres especiais
    df["exclamation_count"] = df["message"].str.count("!")
    df["question_count"] = df["message"].str.count(r"\?")
    df["uppercase_count"] = df["message"].str.count(r"[A-Z]")
    df["digit_count"] = df["message"].str.count(r"\d")
    df["url_count"] = df["message"].str.count(r"http|www|\.com|\.org|\.net")

    # Palavras-chave suspeitas
    spam_keywords = [
        "free",
        "win",
        "winner",
        "won",
        "prize",
        "cash",
        "money",
        "urgent",
        "limited",
        "offer",
        "discount",
        "sale",
        "buy",
        "click",
        "call",
        "text",
        "sms",
        "claim",
        "congratulations",
        "selected",
        "exclusive",
        "guaranteed",
        "risk-free",
        "act now",
        "limited time",
        "special offer",
        "amazing",
        "incredible",
        "unbelievable",
    ]

    for keyword in spam_keywords:
        df[f"has_{keyword}"] = (
            df["message_lower"].str.contains(keyword, regex=False).astype(int)
        )

    # Comprimento da mensagem
    df["message_length"] = df["message"].str.len()
    df["word_count"] = df["message"].str.split().str.len()

    # Proporção de maiúsculas
    df["uppercase_ratio"] = df["uppercase_count"] / df["message_length"].replace(0, 1)

    # Combina features em uma string para o TF-IDF
    df["message_enhanced"] = (
        df["message"]
        + " "
        + df["exclamation_count"].astype(str)
        + " exclamation "
        + df["question_count"].astype(str)
        + " question "
        + df["uppercase_count"].astype(str)
        + " uppercase "
        + df["digit_count"].astype(str)
        + " digit "
        + df["url_count"].astype(str)
        + " url"
    )

    return df


def create_pipeline():
    """Cria o pipeline de ML com TF-IDF + Logistic Regression melhorado"""
    print("🔧 Criando pipeline de ML...")

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=8000,
                    stop_words="english",
                    ngram_range=(1, 3),
                    min_df=1,
                    max_df=0.9,
                    lowercase=True,
                    strip_accents="unicode",
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    random_state=42, max_iter=2000, C=0.5, class_weight="balanced"
                ),
            ),
        ]
    )

    return pipeline


def train_model(df, pipeline):
    """Treina o modelo"""
    print("🚀 Iniciando treinamento...")

    # Separa features e target
    X = df["message_enhanced"]
    y = df["label_binary"]

    # Divide em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"📚 Treino: {len(X_train)} mensagens")
    print(f"🧪 Teste: {len(X_test)} mensagens")

    # Treina o modelo
    pipeline.fit(X_train, y_train)

    # Faz predições
    y_pred = pipeline.predict(X_test)

    # Avalia o modelo
    accuracy = accuracy_score(y_test, y_pred)
    print(f"🎯 Acurácia: {accuracy:.4f}")

    # Relatório detalhado
    print("\n📊 Relatório de Classificação:")
    print(
        classification_report(y_test, y_pred, target_names=["Produtivo", "Improdutivo"])
    )

    # Matriz de confusão
    print("\n🔍 Matriz de Confusão:")
    cm = confusion_matrix(y_test, y_pred)
    print("          Predito")
    print("          Produtivo  Improdutivo")
    print(f"Real Produtivo    {cm[0,0]:>8}  {cm[0,1]:>10}")
    print(f"     Improdutivo  {cm[1,0]:>8}  {cm[1,1]:>10}")

    return pipeline, accuracy


def save_model(pipeline, accuracy):
    """Salva o modelo treinado"""
    print("💾 Salvando modelo...")

    # Cria diretório se não existir
    os.makedirs("models", exist_ok=True)

    # Salva o pipeline
    model_path = "models/email_spam_pipeline.joblib"
    joblib.dump(pipeline, model_path)

    print(f"✅ Modelo salvo em: {model_path}")
    print(f"🎯 Acurácia do modelo: {accuracy:.4f}")

    return model_path


def main():
    """Função principal"""
    print("🤖 Email Productivity Classifier - Treinamento")
    print("=" * 50)

    try:
        # Carrega e prepara os dados
        df = load_and_prepare_data()

        # Cria o pipeline
        pipeline = create_pipeline()

        # Treina o modelo
        pipeline, accuracy = train_model(df, pipeline)

        # Salva o modelo
        model_path = save_model(pipeline, accuracy)

        print("\n🎉 Treinamento concluído com sucesso!")
        print(f"📁 Modelo salvo em: {model_path}")
        print("🚀 Agora você pode rodar: streamlit run src/app_streamlit.py")

    except Exception as e:
        print(f"❌ Erro durante o treinamento: {str(e)}")
        raise


if __name__ == "__main__":
    main()
