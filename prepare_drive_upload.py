#!/usr/bin/env python3
"""
Script para preparar os arquivos do modelo para upload no Google Drive
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_model_package():
    """Cria um pacote zip com todos os arquivos do modelo"""
    
    # Diretório do modelo
    model_dir = Path("models/model_distilbert_cased")
    
    if not model_dir.exists():
        print("❌ Diretório do modelo não encontrado!")
        return False
    
    # Lista de arquivos essenciais
    essential_files = [
        "model.safetensors",
        "config.json", 
        "tokenizer.json",
        "vocab.txt",
        "special_tokens_map.json",
        "tokenizer_config.json"
    ]
    
    # Verifica quais arquivos existem
    existing_files = []
    for file in essential_files:
        file_path = model_dir / file
        if file_path.exists():
            existing_files.append(file)
            print(f"✅ {file} encontrado")
        else:
            print(f"⚠️  {file} não encontrado")
    
    if not existing_files:
        print("❌ Nenhum arquivo do modelo encontrado!")
        return False
    
    # Cria diretório temporário
    temp_dir = Path("temp_drive_upload")
    temp_dir.mkdir(exist_ok=True)
    
    # Copia arquivos para diretório temporário
    print("\n📁 Preparando arquivos para upload...")
    for file in existing_files:
        src = model_dir / file
        dst = temp_dir / file
        shutil.copy2(src, dst)
        print(f"📋 {file} copiado")
    
    # Cria arquivo de instruções
    instructions = """
# 📧 Email Productivity Classifier - Modelo para Google Drive

## 📋 Instruções de Upload

### 1. **Faça upload dos seguintes arquivos para o Google Drive:**
"""
    
    for file in existing_files:
        instructions += f"- `{file}`\n"
    
    instructions += """
### 2. **Configurações de compartilhamento:**
- Clique com botão direito em cada arquivo
- Selecione "Compartilhar"
- Escolha "Qualquer pessoa com o link pode visualizar"
- Clique em "Concluído"

### 3. **Obtenha os IDs dos arquivos:**
- Abra cada arquivo no Drive
- A URL será: `https://drive.google.com/file/d/ID_DO_ARQUIVO/view`
- Copie o `ID_DO_ARQUIVO` (parte entre /d/ e /view)

### 4. **Configure na aplicação:**
- Use os IDs obtidos no arquivo `drive_model_loader.py`
- Substitua os placeholders pelos IDs reais

### 5. **Arquivos essenciais:**
- `model.safetensors` - Modelo treinado (mais importante)
- `config.json` - Configuração do modelo
- `tokenizer.json` - Tokenizador
- `vocab.txt` - Vocabulário
- `special_tokens_map.json` - Tokens especiais
- `tokenizer_config.json` - Configuração do tokenizador

---
**Status**: ✅ Arquivos preparados para upload no Google Drive
"""
    
    with open(temp_dir / "INSTRUCOES_DRIVE.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print(f"\n📝 Instruções criadas em: {temp_dir}/INSTRUCOES_DRIVE.md")
    
    # Cria arquivo zip
    zip_path = "modelo_para_drive.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in temp_dir.iterdir():
            zipf.write(file, file.name)
    
    print(f"\n📦 Pacote criado: {zip_path}")
    print(f"📁 Arquivos preparados em: {temp_dir}/")
    
    # Mostra tamanho dos arquivos
    total_size = 0
    for file in existing_files:
        file_path = model_dir / file
        size_mb = file_path.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"📊 {file}: {size_mb:.1f} MB")
    
    print(f"\n📊 Tamanho total: {total_size:.1f} MB")
    
    if total_size > 100:
        print("⚠️  ATENÇÃO: Total maior que 100MB!")
        print("💡 Considere fazer upload em partes ou usar compressão")
    
    return True

def cleanup():
    """Remove arquivos temporários"""
    temp_dir = Path("temp_drive_upload")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print("🧹 Arquivos temporários removidos")

if __name__ == "__main__":
    print("🚀 Preparando modelo para upload no Google Drive...")
    print("=" * 60)
    
    if create_model_package():
        print("\n✅ Preparação concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Faça upload dos arquivos para o Google Drive")
        print("2. Configure os IDs no drive_model_loader.py")
        print("3. Faça deploy no Hugging Face Spaces")
        
        # Pergunta se quer limpar
        response = input("\n🧹 Remover arquivos temporários? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            cleanup()
    else:
        print("❌ Falha na preparação!")
