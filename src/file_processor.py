"""
Processador de Arquivos para Upload de Emails
"""

import os
import PyPDF2
import io
from typing import Optional, Tuple
import streamlit as st

class FileProcessor:
    """Processa arquivos de email (.txt e .pdf)"""
    
    def __init__(self):
        self.supported_extensions = ['.txt', '.pdf']
    
    def extract_text_from_txt(self, file_content: bytes) -> str:
        """Extrai texto de arquivo .txt"""
        try:
            # Tenta diferentes encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    text = file_content.decode(encoding)
                    return text.strip()
                except UnicodeDecodeError:
                    continue
            
            # Se nenhum encoding funcionar, usa utf-8 com tratamento de erros
            return file_content.decode('utf-8', errors='ignore').strip()
            
        except Exception as e:
            st.error(f"Erro ao processar arquivo .txt: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extrai texto de arquivo .pdf"""
        try:
            # Cria um buffer de bytes
            pdf_file = io.BytesIO(file_content)
            
            # Lê o PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extrai texto de todas as páginas
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            st.error(f"Erro ao processar arquivo .pdf: {str(e)}")
            return ""
    
    def process_uploaded_file(self, uploaded_file) -> Tuple[bool, str, str]:
        """
        Processa arquivo enviado pelo usuário
        
        Returns:
            Tuple[bool, str, str]: (sucesso, texto_extraído, nome_arquivo)
        """
        if uploaded_file is None:
            return False, "", ""
        
        # Verifica extensão do arquivo
        file_name = uploaded_file.name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        if file_extension not in self.supported_extensions:
            st.error(f"Formato de arquivo não suportado. Use: {', '.join(self.supported_extensions)}")
            return False, "", file_name
        
        try:
            # Lê o conteúdo do arquivo
            file_content = uploaded_file.read()
            
            # Extrai texto baseado na extensão
            if file_extension == '.txt':
                extracted_text = self.extract_text_from_txt(file_content)
            elif file_extension == '.pdf':
                extracted_text = self.extract_text_from_pdf(file_content)
            else:
                st.error("Formato de arquivo não suportado")
                return False, "", file_name
            
            # Verifica se o texto foi extraído com sucesso
            if not extracted_text:
                st.warning("Não foi possível extrair texto do arquivo. Verifique se o arquivo contém texto legível.")
                return False, "", file_name
            
            return True, extracted_text, file_name
            
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {str(e)}")
            return False, "", file_name
    
    def validate_email_content(self, text: str) -> Tuple[bool, str]:
        """
        Valida se o texto extraído parece ser um email
        
        Returns:
            Tuple[bool, str]: (é_válido, mensagem)
        """
        if not text or len(text.strip()) < 10:
            return False, "O arquivo não contém texto suficiente para análise."
        
        # Verifica se tem características básicas de email
        text_lower = text.lower()
        
        # Palavras comuns em emails
        email_indicators = [
            'from:', 'to:', 'subject:', 'date:', 'sent:', 'received:',
            'de:', 'para:', 'assunto:', 'data:', 'enviado:', 'recebido:',
            'olá', 'oi', 'prezado', 'caro', 'atenciosamente', 'obrigado'
        ]
        
        has_email_indicators = any(indicator in text_lower for indicator in email_indicators)
        
        if not has_email_indicators:
            return False, "O arquivo não parece conter um email válido. Verifique se o conteúdo está correto."
        
        return True, "Arquivo processado com sucesso!"
    
    def get_file_info(self, file_name: str, text: str) -> dict:
        """Retorna informações sobre o arquivo processado"""
        return {
            "file_name": file_name,
            "file_size": len(text),
            "word_count": len(text.split()),
            "line_count": len(text.split('\n')),
            "has_attachments": "attachment" in text.lower() or "anexo" in text.lower()
        }
