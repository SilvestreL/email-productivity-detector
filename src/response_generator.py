"""
Gerador de Respostas Automáticas para Emails
"""

import re
from typing import Dict, List, Tuple


class ResponseGenerator:
    """Gera respostas automáticas baseadas na classificação do email"""

    def __init__(self):
        # Templates de respostas para emails produtivos
        self.productive_templates = {
            "suporte_tecnico": {
                "keywords": [
                    "problema",
                    "erro",
                    "bug",
                    "não funciona",
                    "falha",
                    "suporte",
                    "ajuda",
                ],
                "response": """Olá,

Obrigado por entrar em contato conosco. Sua solicitação foi registrada e será analisada pela nossa equipe técnica.

Número do ticket: #{ticket_id}
Prioridade: {priority}

Nossa equipe entrará em contato em até 24 horas úteis.

Atenciosamente,
Equipe de Suporte Técnico""",
            },
            "status_requisicao": {
                "keywords": [
                    "status",
                    "andamento",
                    "progresso",
                    "quando",
                    "prazo",
                    "situação",
                ],
                "response": """Prezado(a),

Agradecemos seu contato. Sua requisição está sendo processada e encontra-se atualmente em {status}.

Previsão de conclusão: {deadline}

Em caso de dúvidas, não hesite em nos contatar.

Atenciosamente,
Equipe de Atendimento""",
            },
            "duvida_sistema": {
                "keywords": [
                    "como",
                    "dúvida",
                    "pergunta",
                    "funciona",
                    "utilizar",
                    "usar",
                ],
                "response": """Olá,

Obrigado pela sua pergunta. Para ajudá-lo(a) da melhor forma, nossa equipe especializada irá analisar sua dúvida e retornar com uma resposta detalhada.

Tempo estimado de resposta: 2-4 horas úteis.

Enquanto isso, você pode consultar nossa base de conhecimento: {knowledge_base_url}

Atenciosamente,
Equipe de Suporte""",
            },
            "solicitacao_arquivo": {
                "keywords": ["arquivo", "documento", "relatório", "enviar", "preciso"],
                "response": """Prezado(a),

Recebemos sua solicitação de arquivo/documento. Nossa equipe irá preparar e enviar o material solicitado.

Prazo para envio: {deadline}

Em caso de urgência, entre em contato pelo telefone: {phone}

Atenciosamente,
Equipe de Documentação""",
            },
            "agendamento": {
                "keywords": [
                    "reunião",
                    "agendar",
                    "marcar",
                    "encontro",
                    "call",
                    "videoconferência",
                ],
                "response": """Olá,

Obrigado pelo interesse em agendar uma reunião. Nossa equipe irá entrar em contato para confirmar a data e horário mais adequados.

Opções de horário disponíveis:
- Segunda a Sexta: 9h às 18h
- Sábado: 9h às 12h

Aguarde nosso contato em breve.

Atenciosamente,
Equipe de Agendamento""",
            },
            "padrao": {
                "response": """Prezado(a),

Obrigado por entrar em contato conosco. Sua mensagem foi recebida e será analisada pela equipe responsável.

Tempo estimado de resposta: 24 horas úteis.

Em caso de urgência, entre em contato pelo telefone: {phone}

Atenciosamente,
Equipe de Atendimento"""
            },
        }

        # Templates de respostas para emails improdutivos
        self.unproductive_templates = {
            "felicitacoes": {
                "keywords": [
                    "parabéns",
                    "felicitações",
                    "feliz",
                    "natal",
                    "ano novo",
                    "páscoa",
                ],
                "response": """Olá,

Obrigado pelas suas felicitações! É muito gratificante receber mensagens como a sua.

Desejamos a você e sua equipe muito sucesso e realizações.

Atenciosamente,
Equipe {company_name}""",
            },
            "agradecimento": {
                "keywords": ["obrigado", "agradeço", "valeu", "thanks", "gratidão"],
                "response": """Olá,

Obrigado pelo seu agradecimento! É um prazer poder ajudá-lo(a).

Ficamos à disposição para futuras colaborações.

Atenciosamente,
Equipe {company_name}""",
            },
            "spam": {
                "keywords": ["free", "win", "prize", "urgent", "limited", "offer"],
                "response": """Esta mensagem foi identificada como não produtiva e não requer resposta.

Se você acredita que esta classificação está incorreta, entre em contato conosco.

Atenciosamente,
Sistema de Filtros""",
            },
            "padrao": {
                "response": """Olá,

Obrigado por sua mensagem. Após análise, identificamos que este contato não requer uma ação específica de nossa equipe.

Em caso de dúvidas ou necessidade de suporte, não hesite em nos contatar.

Atenciosamente,
Equipe de Atendimento"""
            },
        }

    def analyze_email_content(self, text: str) -> Dict:
        """Analisa o conteúdo do email para identificar o tipo"""
        text_lower = text.lower()

        # Conta palavras-chave
        keyword_counts = {}

        # Analisa emails produtivos
        for category, template in self.productive_templates.items():
            if category == "padrao":
                continue
            count = sum(1 for keyword in template["keywords"] if keyword in text_lower)
            if count > 0:
                keyword_counts[category] = count

        # Analisa emails improdutivos
        for category, template in self.unproductive_templates.items():
            if category == "padrao":
                continue
            count = sum(1 for keyword in template["keywords"] if keyword in text_lower)
            if count > 0:
                keyword_counts[category] = count

        return keyword_counts

    def generate_response(
        self, text: str, is_productive: bool, confidence: float
    ) -> str:
        """Gera resposta automática baseada na classificação"""

        if is_productive:
            # Email produtivo - gera resposta específica
            keyword_counts = self.analyze_email_content(text)

            if keyword_counts:
                # Encontra a categoria com mais palavras-chave
                best_category = max(keyword_counts.items(), key=lambda x: x[1])[0]

                if best_category in self.productive_templates:
                    template = self.productive_templates[best_category]["response"]
                    return self._fill_template(template, best_category, confidence)

            # Usa template padrão para produtivo
            return self._fill_template(
                self.productive_templates["padrao"]["response"], "padrao", confidence
            )

        else:
            # Email improdutivo - gera resposta genérica
            keyword_counts = self.analyze_email_content(text)

            if keyword_counts:
                best_category = max(keyword_counts.items(), key=lambda x: x[1])[0]

                if best_category in self.unproductive_templates:
                    template = self.unproductive_templates[best_category]["response"]
                    return self._fill_template(template, best_category, confidence)

            # Usa template padrão para improdutivo
            return self._fill_template(
                self.unproductive_templates["padrao"]["response"], "padrao", confidence
            )

    def _fill_template(self, template: str, category: str, confidence: float) -> str:
        """Preenche o template com informações dinâmicas"""

        # Informações da empresa
        company_info = {
            "company_name": "AutoU",
            "phone": "(11) 99999-9999",
            "knowledge_base_url": "https://help.autou.com.br",
            "ticket_id": f"T{int(confidence * 1000)}",
            "priority": "Média" if confidence < 0.8 else "Alta",
            "status": "Análise",
            "deadline": "24 horas úteis",
        }

        # Substitui placeholders no template
        response = template
        for key, value in company_info.items():
            response = response.replace(f"{{{key}}}", str(value))

        return response

    def get_response_summary(
        self, text: str, is_productive: bool, confidence: float
    ) -> Dict:
        """Retorna resumo da análise e resposta"""

        response = self.generate_response(text, is_productive, confidence)
        keyword_counts = self.analyze_email_content(text)

        return {
            "is_productive": is_productive,
            "confidence": confidence,
            "detected_categories": list(keyword_counts.keys()),
            "response": response,
            "response_type": "Específica" if keyword_counts else "Genérica",
        }
