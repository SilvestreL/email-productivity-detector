#!/usr/bin/env python3
"""
Script para balancear dataset usando técnicas de oversampling
"""

import os
import sys
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# Tentar importar imbalanced-learn
try:
    from imblearn.over_sampling import SMOTE, ADASYN

    IMBALANCED_LEARN_AVAILABLE = True
except ImportError:
    IMBALANCED_LEARN_AVAILABLE = False
    print("⚠️  imbalanced-learn não disponível. SMOTE e ADASYN não funcionarão.")
    print("💡 Instale com: pip install imbalanced-learn")

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def analyze_dataset_balance(dataset_path: str = None):
    """
    Analisa o balanceamento atual do dataset
    """

    print("🔍 ANALISANDO BALANCEAMENTO DO DATASET")
    print("=" * 60)

    if dataset_path and os.path.exists(dataset_path):
        # Carregar dataset existente
        df = pd.read_csv(dataset_path)
        print(f"📁 Dataset carregado: {dataset_path}")
    else:
        # Dataset de exemplo para demonstração
        print("📊 Criando dataset de exemplo para demonstração...")

        # Simular dataset desbalanceado
        np.random.seed(42)
        n_samples = 1000

        # Classe majoritária (Produtivo) - 80%
        produtivo_samples = n_samples * 0.8
        # Classe minoritária (Improdutivo) - 20%
        improdutivo_samples = n_samples * 0.2

        # Gerar dados sintéticos
        produtivo_data = {
            "text": [
                f"Preciso de uma reunião para discutir o projeto {i}"
                for i in range(int(produtivo_samples))
            ],
            "label": [1] * int(produtivo_samples),  # 1 = Produtivo
        }

        improdutivo_data = {
            "text": [
                f"Bom dia a todos! Apenas para informar {i}"
                for i in range(int(improdutivo_samples))
            ],
            "label": [0] * int(improdutivo_samples),  # 0 = Improdutivo
        }

        # Combinar dados
        df = pd.DataFrame(
            {
                "text": produtivo_data["text"] + improdutivo_data["text"],
                "label": produtivo_data["label"] + improdutivo_data["label"],
            }
        )

        # Embaralhar
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Analisar balanceamento
    print(f"\n📊 ESTATÍSTICAS DO DATASET:")
    print(f"   Total de amostras: {len(df)}")

    # Contar classes
    class_counts = df["label"].value_counts()
    print(f"\n🏷️  DISTRIBUIÇÃO DAS CLASSES:")
    for label, count in class_counts.items():
        percentage = (count / len(df)) * 100
        label_name = "Produtivo" if label == 1 else "Improdutivo"
        print(f"   {label_name} (Label {label}): {count} amostras ({percentage:.1f}%)")

    # Calcular métricas de desbalanceamento
    majority_class = class_counts.max()
    minority_class = class_counts.min()
    imbalance_ratio = majority_class / minority_class

    print(f"\n⚖️  MÉTRICAS DE DESBALANCEAMENTO:")
    print(f"   Razão de desbalanceamento: {imbalance_ratio:.2f}:1")
    print(f"   Classe majoritária: {majority_class} amostras")
    print(f"   Classe minoritária: {minority_class} amostras")

    if imbalance_ratio > 2:
        print(f"   🚨 DATASET DESBALANCEADO! Razão > 2:1")
    elif imbalance_ratio > 1.5:
        print(f"   ⚠️  DATASET LEVEMENTE DESBALANCEADO")
    else:
        print(f"   ✅ DATASET BALANCEADO")

    return df, class_counts


def random_oversampling(df: pd.DataFrame, target_column: str = "label"):
    """
    Aplica Random Oversampling para balancear o dataset
    """

    print(f"\n🔄 APLICANDO RANDOM OVERSAMPLING")
    print("=" * 50)

    # Contar classes
    class_counts = df[target_column].value_counts()
    majority_class = class_counts.max()
    minority_class = class_counts.min()

    print(f"   Classe majoritária: {majority_class} amostras")
    print(f"   Classe minoritária: {minority_class} amostras")
    print(f"   Amostras a adicionar: {majority_class - minority_class}")

    # Encontrar classe minoritária
    minority_label = class_counts.idxmin()

    # Filtrar exemplos da classe minoritária
    minority_samples = df[df[target_column] == minority_label]

    # Calcular quantas amostras precisamos duplicar
    samples_needed = majority_class - minority_class

    # Duplicar amostras aleatoriamente
    if samples_needed > 0:
        # Selecionar amostras aleatoriamente com reposição
        additional_samples = minority_samples.sample(
            n=samples_needed, replace=True, random_state=42
        )

        # Combinar dataset original com amostras duplicadas
        balanced_df = pd.concat([df, additional_samples], ignore_index=True)

        # Embaralhar o dataset final
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

        print(f"   ✅ Oversampling aplicado!")
        print(f"   Dataset final: {len(balanced_df)} amostras")

        # Verificar novo balanceamento
        new_counts = balanced_df[target_column].value_counts()
        print(f"   Nova distribuição:")
        for label, count in new_counts.items():
            percentage = (count / len(balanced_df)) * 100
            label_name = "Produtivo" if label == 1 else "Improdutivo"
            print(f"     {label_name}: {count} amostras ({percentage:.1f}%)")

        return balanced_df
    else:
        print(f"   ✅ Dataset já está balanceado!")
        return df


def smote_oversampling(df: pd.DataFrame, target_column: str = "label"):
    """
    Aplica SMOTE para balancear o dataset (requer imbalanced-learn)
    """

    print(f"\n🔄 APLICANDO SMOTE OVERSAMPLING")
    print("=" * 50)

    if not IMBALANCED_LEARN_AVAILABLE:
        print(f"   ❌ Biblioteca imbalanced-learn não disponível")
        print(f"   💡 Instale com: pip install imbalanced-learn")
        return None

    try:
        # Separar features e target
        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Aplicar SMOTE
        smote = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X, y)

        # Criar novo dataset balanceado
        balanced_df = pd.concat([X_resampled, y_resampled], axis=1)

        print(f"   ✅ SMOTE aplicado com sucesso!")
        print(f"   Dataset final: {len(balanced_df)} amostras")

        # Verificar novo balanceamento
        new_counts = balanced_df[target_column].value_counts()
        print(f"   Nova distribuição:")
        for label, count in new_counts.items():
            percentage = (count / len(balanced_df)) * 100
            label_name = "Produtivo" if label == 1 else "Improdutivo"
            print(f"     {label_name}: {count} amostras ({percentage:.1f}%)")

        return balanced_df

    except Exception as e:
        print(f"   ❌ Erro ao aplicar SMOTE: {e}")
        return None


def adasyn_oversampling(df: pd.DataFrame, target_column: str = "label"):
    """
    Aplica ADASYN para balancear o dataset (requer imbalanced-learn)
    """

    print(f"\n🔄 APLICANDO ADASYN OVERSAMPLING")
    print("=" * 50)

    if not IMBALANCED_LEARN_AVAILABLE:
        print(f"   ❌ Biblioteca imbalanced-learn não disponível")
        print(f"   💡 Instale com: pip install imbalanced-learn")
        return None

    try:
        # Separar features e target
        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Aplicar ADASYN
        adasyn = ADASYN(random_state=42)
        X_resampled, y_resampled = adasyn.fit_resample(X, y)

        # Criar novo dataset balanceado
        balanced_df = pd.concat([X_resampled, y_resampled], axis=1)

        print(f"   ✅ ADASYN aplicado com sucesso!")
        print(f"   Dataset final: {len(balanced_df)} amostras")

        # Verificar novo balanceamento
        new_counts = balanced_df[target_column].value_counts()
        print(f"   Nova distribuição:")
        for label, count in new_counts.items():
            percentage = (count / len(balanced_df)) * 100
            label_name = "Produtivo" if label == 1 else "Improdutivo"
            print(f"     {label_name}: {count} amostras ({percentage:.1f}%)")

        return balanced_df

    except Exception as e:
        print(f"   ❌ Erro ao aplicar ADASYN: {e}")
        return None


def plot_balance_comparison(
    original_counts, balanced_counts, title: str = "Comparação de Balanceamento"
):
    """
    Plota gráfico comparando balanceamento antes e depois
    """

    try:
        # Criar figura
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Gráfico original
        labels = ["Improdutivo", "Produtivo"]
        ax1.pie(original_counts.values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax1.set_title("Antes do Balanceamento")

        # Gráfico balanceado
        ax2.pie(balanced_counts.values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax2.set_title("Depois do Balanceamento")

        plt.suptitle(title)
        plt.tight_layout()

        # Salvar gráfico
        output_path = "balanceamento_comparacao.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"   📊 Gráfico salvo: {output_path}")

        plt.show()

    except Exception as e:
        print(f"   ⚠️  Erro ao gerar gráfico: {e}")


def save_balanced_dataset(df: pd.DataFrame, output_path: str, method: str):
    """
    Salva dataset balanceado
    """

    # Criar diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Salvar dataset
    df.to_csv(output_path, index=False)
    print(f"   💾 Dataset salvo: {output_path}")

    # Salvar informações do balanceamento
    info_path = output_path.replace(".csv", "_info.txt")
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"Dataset Balanceado - Método: {method}\n")
        f.write(f"Data: {pd.Timestamp.now()}\n")
        f.write(f"Total de amostras: {len(df)}\n")
        f.write(f"Distribuição das classes:\n")
        class_counts = df["label"].value_counts()
        for label, count in class_counts.items():
            percentage = (count / len(df)) * 100
            label_name = "Produtivo" if label == 1 else "Improdutivo"
            f.write(f"  {label_name}: {count} amostras ({percentage:.1f}%)\n")

    print(f"   📝 Informações salvas: {info_path}")


def main():
    """
    Função principal
    """

    print("🚀 BALANCEAMENTO DE DATASET COM OVERSAMPLING")
    print("=" * 60)

    # 1. Analisar dataset atual
    df, original_counts = analyze_dataset_balance()

    # 2. Aplicar diferentes técnicas de oversampling
    methods = {
        "random_oversampling": random_oversampling,
        "smote": smote_oversampling,
        "adasyn": adasyn_oversampling,
    }

    results = {}

    for method_name, method_func in methods.items():
        print(f"\n{'='*60}")
        print(f"🔧 APLICANDO: {method_name.upper()}")
        print(f"{'='*60}")

        # Aplicar método
        balanced_df = method_func(df)

        if balanced_df is not None:
            # Salvar resultados
            results[method_name] = balanced_df

            # Salvar dataset
            output_path = f"./data/balanced_dataset_{method_name}.csv"
            save_balanced_dataset(balanced_df, output_path, method_name)

            # Plotar comparação
            new_counts = balanced_df["label"].value_counts()
            plot_balance_comparison(
                original_counts, new_counts, f"Balanceamento - {method_name}"
            )

    # 3. Resumo final
    print(f"\n{'='*60}")
    print("🎯 RESUMO FINAL")
    print(f"{'='*60}")

    print(f"✅ Técnicas aplicadas: {len(results)}")
    print(f"📁 Datasets salvos em: ./data/")

    for method_name, balanced_df in results.items():
        print(f"\n📊 {method_name.upper()}:")
        print(f"   Amostras originais: {len(df)}")
        print(f"   Amostras finais: {len(balanced_df)}")
        print(f"   Arquivo: balanced_dataset_{method_name}.csv")

    print(f"\n💡 PRÓXIMOS PASSOS:")
    print(f"   1. Escolha o método que funcionou melhor")
    print(f"   2. Use o dataset balanceado para retreinar o modelo")
    print(f"   3. Avalie a performance do novo modelo")

    return results


if __name__ == "__main__":
    main()
