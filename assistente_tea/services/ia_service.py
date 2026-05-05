import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class IAService:
    def __init__(self):
        # Verifica se a chave foi carregada corretamente
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY não encontrada nas configurações. Verifique o arquivo 'chave' e o settings.py."
            )

        self.client = openai.OpenAI(api_key=api_key)

    def gerar_resposta_ia(self, mensagem_usuario: str, historico: list = None) -> str:
        """
        Gera uma resposta empática, clara e literal, adequada para TEA.
        Recebe o histórico recente para manter o contexto.
        """
        # Prompt de Sistema: Define a personalidade do assistente
        system_prompt = (
            "Você é um assistente virtual projetado para ajudar pessoas no Espectro Autista (TEA). "
            "Suas respostas devem ser:\n"
            "1. Claras, diretas e literais (evite metáforas, ironia ou duplo sentido).\n"
            "2. Empáticas, mas calmas e previsíveis.\n"
            "3. Curtas (máximo 3-4 frases).\n"
            "4. Estruturadas (use listas se necessário).\n"
            "5. Nunca julgue. Valide os sentimentos do usuário.\n"
            "Se o usuário parecer sobrecarregado, sugira pausas ou redução de estímulos.\n"
            "Mantenha o contexto da conversa anterior."
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Adiciona histórico recente para contexto (últimas 5 interações completas)
        if historico:
            # Limita a 10 mensagens (5 pares de user/assistant) para controlar custo e token
            recent_history = historico[-10:]
            messages.extend(recent_history)

        # Adiciona a mensagem atual do usuário
        messages.append({"role": "user", "content": mensagem_usuario})

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Ou "gpt-4o-mini" para melhor custo-benefício
                messages=messages,
                temperature=0.3,  # Baixa temperatura para consistência/previsibilidade
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()

        except openai.AuthenticationError:
            logger.error("Erro de autenticação na OpenAI. Verifique a API Key.")
            return "Houve um problema técnico com minha configuração. Por favor, avise o administrador."

        except openai.RateLimitError:
            logger.warning("Limite de taxa da OpenAI atingido.")
            return "Estou um pouco ocupado agora. Por favor, tente novamente em alguns segundos."

        except openai.APIConnectionError:
            logger.error("Erro de conexão com a API da OpenAI.")
            return (
                "Não consegui me conectar ao meu cérebro agora. Vamos tentar de novo?"
            )

        except Exception as e:
            logger.error(f"Erro inesperado na IA: {e}", exc_info=True)
            return "Tive dificuldade em processar sua mensagem agora. Vamos tentar de novo?"
