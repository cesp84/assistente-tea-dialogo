import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)


class IAService:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não configurada no settings.py.")

        print("Modelo Gemini em uso: gemini-2.5-flash")

        self.url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={self.api_key}"
        )

    def gerar_resposta_ia(
        self, mensagem_usuario: str, historico: list | None = None
    ) -> str:
        prompt = self._montar_prompt(mensagem_usuario, historico or [])

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 180,
            },
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=20,
            )

            if response.status_code != 200:
                logger.warning(
                    "Erro ao chamar Gemini. Status: %s | Resposta: %s",
                    response.status_code,
                    response.text,
                )
                return (
                    "Não consegui gerar uma resposta pela IA agora.\n\n"
                    "Vou responder de forma simples:\n"
                    "me diga o que você precisa resolver primeiro."
                )

            data = response.json()

            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

        except requests.Timeout:
            logger.warning("Tempo limite ao chamar Gemini.")
            return "A resposta demorou mais que o esperado. Tente novamente."

        except requests.RequestException as e:
            logger.error("Erro de conexão com Gemini: %s", e, exc_info=True)
            return "Não consegui conectar ao serviço de IA agora. Tente novamente."

        except Exception as e:
            logger.error(
                "Erro inesperado ao processar resposta do Gemini: %s", e, exc_info=True
            )
            return (
                "Tive dificuldade para processar a resposta agora.\n\n"
                "Podemos tentar de novo com uma mensagem mais curta."
            )

    def _montar_prompt(self, mensagem_usuario: str, historico: list) -> str:
        base = (
            "Você é um assistente virtual para apoio comunicacional de pessoas com TEA.\n"
            "Use o histórico recente apenas para manter contexto.\n"
            "Não diga que possui memória permanente.\n"
            "Não faça diagnóstico.\n"
            "Não substitua profissional de saúde.\n"
            "Responda em português do Brasil.\n"
            "Use linguagem clara, direta e literal.\n"
            "Use frases curtas.\n"
            "Evite metáforas, ironias e duplo sentido.\n"
            "Se a pessoa parecer sobrecarregada, reduza a quantidade de informação.\n"
            "Responda com no máximo 4 frases ou uma lista curta.\n\n"
        )
        contexto = ""

        if historico:
            mensagens_formatadas = []

            for item in historico[-6:]:
                role = item.get("role", "user")
                content = item.get("content", "")

                if role == "assistant":
                    papel = "Assistente"
                else:
                    papel = "Usuário"

                mensagens_formatadas.append(f"{papel}: {content}")

            contexto = "\n".join(mensagens_formatadas)

        return (
            f"{base}"
            f"Histórico recente:\n{contexto}\n\n"
            f"Mensagem atual do usuário:\n{mensagem_usuario}\n\n"
            "Resposta:"
        )
