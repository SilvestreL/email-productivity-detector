import re
import io
import logging
from typing import Union
import pdfplumber
from pdfminer.high_level import extract_text as pdfminer_extract_text

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_text(text: str) -> str:
    """
    Pré-processa texto para classificação
    
    Args:
        text: Texto bruto
        
    Returns:
        Texto pré-processado
    """
    try:
        if not text or not isinstance(text, str):
            return ""
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover caracteres especiais e números excessivos
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remover espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        
        # Remover quebras de linha excessivas
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Limpar espaços no início e fim
        text = text.strip()
        
        # Limitar tamanho para o modelo
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        logger.info(f"Texto pré-processado: {len(text)} caracteres")
        return text
        
    except Exception as e:
        logger.error(f"Erro no pré-processamento: {e}")
        return text if text else ""

def parse_file(file) -> str:
    """
    Extrai texto de arquivo .txt ou .pdf
    
    Args:
        file: Arquivo carregado via Streamlit
        
    Returns:
        String com o texto extraído
        
    Raises:
        ValueError: Se o tipo de arquivo não for suportado
        Exception: Para outros erros de processamento
    """
    try:
        file_extension = file.name.lower().split('.')[-1]
        
        if file_extension == 'txt':
            # Arquivo de texto
            content = file.read()
            if isinstance(content, bytes):
                text = content.decode("utf-8", errors="ignore")
            else:
                text = str(content)
            
            logger.info(f"Arquivo .txt processado: {len(text)} caracteres")
            return text
            
        elif file_extension == 'pdf':
            # Arquivo PDF
            try:
                # Tentar com pdfplumber primeiro
                with pdfplumber.open(file) as pdf:
                    text_parts = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    
                    if text_parts:
                        text = '\n'.join(text_parts)
                        logger.info(f"PDF processado com pdfplumber: {len(text)} caracteres")
                        return text
                    else:
                        raise Exception("Nenhum texto extraído com pdfplumber")
                        
            except Exception as pdfplumber_error:
                logger.warning(f"pdfplumber falhou, tentando pdfminer: {pdfplumber_error}")
                
                # Fallback para pdfminer
                try:
                    file.seek(0)  # Resetar posição do arquivo
                    text = pdfminer_extract_text(file)
                    
                    if text:
                        logger.info(f"PDF processado com pdfminer: {len(text)} caracteres")
                        return text
                    else:
                        raise Exception("Nenhum texto extraído com pdfminer")
                        
                except Exception as pdfminer_error:
                    logger.error(f"pdfminer também falhou: {pdfminer_error}")
                    raise Exception("Não foi possível extrair texto do PDF com nenhum método")
        
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {file_extension}")
            
    except Exception as e:
        logger.error(f"Erro ao processar arquivo: {e}")
        raise

def suggest_reply(prediction: str, original_text: str) -> str:
    """
    Gera resposta sugerida baseada na classificação
    
    Args:
        prediction: Classe prevista ("Produtivo" ou "Improdutivo")
        original_text: Texto original do e-mail
        
    Returns:
        String com a resposta sugerida
    """
    try:
        if prediction == "Produtivo":
            # Template para e-mails produtivos
            reply = generate_productive_reply(original_text)
        else:
            # Template para e-mails improdutivos
            reply = generate_unproductive_reply(original_text)
        
        logger.info(f"Resposta sugerida gerada para classe: {prediction}")
        return reply
        
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {e}")
        return "Erro ao gerar resposta sugerida."

def generate_productive_reply(text: str) -> str:
    """
    Gera resposta para e-mails produtivos
    
    Args:
        text: Texto original do e-mail
        
    Returns:
        Resposta sugerida
    """
    # Identificar tipo de solicitação baseado em palavras-chave
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['reunião', 'meeting', 'agenda', 'horário']):
        return """Obrigado pelo contato. Sua solicitação de reunião está sendo analisada pela equipe.

Prazo para resposta: 24 horas úteis.

Em caso de urgência, entre em contato pelo telefone: (11) 9999-9999."""
    
    elif any(word in text_lower for word in ['proposta', 'orçamento', 'cotação', 'preço']):
        return """Obrigado pelo interesse. Sua solicitação de proposta está sendo processada.

Prazo para resposta: 48 horas úteis.

Nossa equipe comercial entrará em contato em breve."""
    
    elif any(word in text_lower for word in ['problema', 'erro', 'bug', 'falha', 'suporte']):
        return """Obrigado pelo reporte. Sua solicitação de suporte foi registrada.

Número do ticket: #SUP-{timestamp}

Prazo para primeira resposta: 4 horas úteis.
Prazo para resolução: 24 horas úteis."""
    
    elif any(word in text_lower for word in ['parceria', 'colaboração', 'projeto']):
        return """Obrigado pela proposta de parceria. Sua iniciativa está sendo avaliada pela diretoria.

Prazo para resposta: 72 horas úteis.

Entraremos em contato para agendar uma reunião de alinhamento."""
    
    else:
        # Resposta genérica para e-mails produtivos
        return """Obrigado pelo contato. Sua mensagem foi recebida e está sendo analisada pela equipe responsável.

Prazo para resposta: 24 horas úteis.

Em caso de urgência, entre em contato pelo telefone: (11) 9999-9999."""

def generate_unproductive_reply(text: str) -> str:
    """
    Gera resposta para e-mails improdutivos
    
    Args:
        text: Texto original do e-mail
        
    Returns:
        Resposta sugerida
    """
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['aniversário', 'parabéns', 'felicidades']):
        return """Obrigado pelas felicitações! Apreciamos muito o carinho da equipe.

No momento, não há ação necessária de nossa parte.

Agradecemos o contato e desejamos um excelente dia!"""
    
    elif any(word in text_lower for word in ['feriado', 'férias', 'descanso', 'aproveitem']):
        return """Obrigado pelos votos de boas férias! A equipe agradece a consideração.

No momento, não há ação necessária de nossa parte.

Desejamos a todos um excelente período de descanso!"""
    
    elif any(word in text_lower for word in ['bom dia', 'boa tarde', 'boa noite', 'olá']):
        return """Obrigado pela saudação! A equipe agradece o contato cordial.

No momento, não há ação necessária de nossa parte.

Desejamos um excelente dia de trabalho!"""
    
    else:
        # Resposta genérica para e-mails improdutivos
        return """Agradecemos sua mensagem. No momento, não há ação necessária de nossa parte.

Obrigado pelo contato e desejamos um excelente dia!"""

def extract_keywords(text: str, max_keywords: int = 5) -> list:
    """
    Extrai palavras-chave do texto para análise
    
    Args:
        text: Texto para análise
        max_keywords: Número máximo de palavras-chave
        
    Returns:
        Lista de palavras-chave
    """
    try:
        # Remover stopwords básicas
        stopwords = {
            'a', 'o', 'e', 'é', 'de', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'na',
            'se', 'que', 'por', 'mais', 'as', 'como', 'mas', 'foi', 'ele', 'das', 'tem',
            'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está',
            'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era',
            'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas', 'meu', 'minha', 'teu',
            'tua', 'nosso', 'nossa', 'deles', 'delas', 'esta', 'estes', 'estas', 'aquele',
            'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos',
            'estão', 'estava', 'estávamos', 'estavam', 'estive', 'esteve', 'estivemos',
            'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos',
            'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem',
            'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve',
            'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam',
            'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem',
            'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos',
            'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi',
            'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse',
            'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos',
            'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'têm',
            'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram',
            'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos',
            'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos',
            'terão', 'teria', 'teríamos', 'teriam'
        }
        
        # Limpar texto
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filtrar palavras
        filtered_words = [word for word in words if len(word) > 3 and word not in stopwords]
        
        # Contar frequência
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Ordenar por frequência e retornar top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:max_keywords]]
        
        return keywords
        
    except Exception as e:
        logger.error(f"Erro ao extrair palavras-chave: {e}")
        return []
