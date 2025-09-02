#!/usr/bin/env python3
"""
Script para aplicar oversampling no dataset real de emails
"""

import os
import sys
import pandas as pd
import numpy as np
from collections import Counter

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_email_dataset():
    """
    Carrega o dataset de emails (ajuste o caminho conforme necessário)
    """
    
    print("🔍 CARREGANDO DATASET DE EMAILS")
    print("=" * 50)
    
    # Possíveis caminhos para o dataset
    possible_paths = [
        "../data/emails_dataset.csv",
        "../data/dataset.csv",
        "../data/emails.csv",
        "../data/training_data.csv"
    ]
    
    dataset_path = None
    for path in possible_paths:
        if os.path.exists(path):
            dataset_path = path
            break
    
    if dataset_path:
        print(f"✅ Dataset encontrado: {dataset_path}")
        df = pd.read_csv(dataset_path)
        
        # Verificar estrutura
        print(f"📊 Estrutura do dataset:")
        print(f"   Colunas: {list(df.columns)}")
        print(f"   Linhas: {len(df)}")
        
        return df, dataset_path
    else:
        print("❌ Dataset não encontrado nos caminhos padrão")
        print("💡 Caminhos verificados:")
        for path in possible_paths:
            print(f"   - {path}")
        
        print(f"\n🔧 Para usar seu próprio dataset:")
        print(f"   1. Coloque o arquivo .csv na pasta data/")
        print(f"   2. Ou especifique o caminho completo")
        
        return None, None

def analyze_email_balance(df: pd.DataFrame):
    """
    Analisa o balanceamento do dataset de emails
    """
    
    print(f"\n🔍 ANALISANDO BALANCEAMENTO")
    print("=" * 50)
    
    # Identificar coluna de label
    label_columns = [col for col in df.columns if 'label' in col.lower() or 'class' in col.lower() or 'target' in col.lower()]
    
    if label_columns:
        label_column = label_columns[0]
        print(f"🏷️  Coluna de label identificada: {label_column}")
    else:
        # Tentar identificar automaticamente
        for col in df.columns:
            unique_values = df[col].nunique()
            if unique_values <= 5:  # Provavelmente é a label
                label_column = col
                print(f"🏷️  Coluna de label inferida: {label_column} (valores únicos: {unique_values})")
                break
        else:
            print("❌ Não foi possível identificar a coluna de label")
            print(f"   Colunas disponíveis: {list(df.columns)}")
            return None, None
    
    # Analisar valores únicos
    unique_labels = df[label_column].unique()
    print(f"   Valores únicos: {unique_labels}")
    
    # Contar classes
    class_counts = df[label_column].value_counts()
    print(f"\n📊 DISTRIBUIÇÃO DAS CLASSES:")
    
    for label, count in class_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   Label {label}: {count} amostras ({percentage:.1f}%)")
    
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
        print(f"   💡 Recomendado aplicar oversampling")
    elif imbalance_ratio > 1.5:
        print(f"   ⚠️  DATASET LEVEMENTE DESBALANCEADO")
        print(f"   💡 Pode se beneficiar de oversampling")
    else:
        print(f"   ✅ DATASET BALANCEADO")
        print(f"   💡 Oversampling pode não ser necessário")
    
    return df, label_column, class_counts

def apply_random_oversampling(df: pd.DataFrame, label_column: str):
    """
    Aplica Random Oversampling para balancear o dataset
    """
    
    print(f"\n🔄 APLICANDO RANDOM OVERSAMPLING")
    print("=" * 50)
    
    # Contar classes
    class_counts = df[label_column].value_counts()
    majority_class = class_counts.max()
    minority_class = class_counts.min()
    
    print(f"   Classe majoritária: {majority_class} amostras")
    print(f"   Classe minoritária: {minority_class} amostras")
    print(f"   Amostras a adicionar: {majority_class - minority_class}")
    
    # Encontrar classe minoritária
    minority_label = class_counts.idxmin()
    
    # Filtrar exemplos da classe minoritária
    minority_samples = df[df[label_column] == minority_label]
    
    # Calcular quantas amostras precisamos duplicar
    samples_needed = majority_class - minority_class
    
    if samples_needed > 0:
        # Duplicar amostras aleatoriamente
        additional_samples = minority_samples.sample(n=samples_needed, replace=True, random_state=42)
        
        # Combinar dataset original com amostras duplicadas
        balanced_df = pd.concat([df, additional_samples], ignore_index=True)
        
        # Embaralhar o dataset final
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print(f"   ✅ Oversampling aplicado!")
        print(f"   Dataset final: {len(balanced_df)} amostras")
        
        # Verificar novo balanceamento
        new_counts = balanced_df[label_column].value_counts()
        print(f"   Nova distribuição:")
        for label, count in new_counts.items():
            percentage = (count / len(balanced_df)) * 100
            print(f"     Label {label}: {count} amostras ({percentage:.1f}%)")
        
        return balanced_df
    else:
        print(f"   ✅ Dataset já está balanceado!")
        return df

def save_balanced_dataset(df: pd.DataFrame, output_path: str, method: str, original_path: str):
    """
    Salva dataset balanceado
    """
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar dataset
    df.to_csv(output_path, index=False)
    print(f"   💾 Dataset salvo: {output_path}")
    
    # Salvar informações do balanceamento
    info_path = output_path.replace('.csv', '_info.txt')
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(f"Dataset Balanceado - Método: {method}\n")
        f.write(f"Data: {pd.Timestamp.now()}\n")
        f.write(f"Dataset original: {original_path}\n")
        f.write(f"Total de amostras: {len(df)}\n")
        f.write(f"Distribuição das classes:\n")
        class_counts = df.iloc[:, -1].value_counts()  # Assumir que a última coluna é a label
        for label, count in class_counts.items():
            percentage = (count / len(df)) * 100
            f.write(f"  Label {label}: {count} amostras ({percentage:.1f}%)\n")
    
    print(f"   📝 Informações salvas: {info_path}")

def main():
    """
    Função principal
    """
    
    print("🚀 APLICANDO OVERSAMPLING NO DATASET DE EMAILS")
    print("=" * 60)
    
    # 1. Carregar dataset
    df, dataset_path = load_email_dataset()
    
    if df is None:
        print("❌ Não foi possível carregar o dataset")
        return
    
    # 2. Analisar balanceamento
    df, label_column, class_counts = analyze_email_balance(df)
    
    if df is None:
        print("❌ Erro na análise do balanceamento")
        return
    
    # 3. Aplicar oversampling
    print(f"\n{'='*60}")
    print(f"🔧 APLICANDO RANDOM OVERSAMPLING")
    print(f"{'='*60}")
    
    balanced_df = apply_random_oversampling(df, label_column)
    
    # 4. Salvar dataset balanceado
    if balanced_df is not None:
        output_path = f"../data/balanced_emails_dataset.csv"
        save_balanced_dataset(balanced_df, output_path, "random_oversampling", dataset_path)
        
        print(f"\n🎯 RESUMO FINAL")
        print(f"{'='*60}")
        print(f"✅ Oversampling aplicado com sucesso!")
        print(f"📊 Dataset original: {len(df)} amostras")
        print(f"📊 Dataset balanceado: {len(balanced_df)} amostras")
        print(f"💾 Arquivo salvo: {output_path}")
        
        print(f"\n💡 PRÓXIMOS PASSOS:")
        print(f"   1. Use o dataset balanceado para retreinar o modelo")
        print(f"   2. O modelo deve ter melhor performance na classe minoritária")
        print(f"   3. Avalie métricas como F1-Score, Precision e Recall")
        
        print(f"\n🔧 Para retreinar o modelo:")
        print(f"   - Copie o arquivo: {output_path}")
        print(f"   - Use no script de treinamento")
        print(f"   - Ajuste hiperparâmetros se necessário")
    
    return balanced_df

if __name__ == "__main__":
    main()
