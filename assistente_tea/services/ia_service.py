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
                "maxOutputTokens": 400,
                "topK": 40,
                "topP": 0.95,
            },
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=20,
            )

            if response.status_code == 503:
                logger.warning("Gemini indisponível (alta demanda): %s", response.text)
                return (
                    "O serviço de IA está indisponível agora.\n\n"
                    "Vamos continuar de forma simples:\n"
                    "me diga o que você quer resolver primeiro."
                )

            if response.status_code != 200:
                logger.warning(
                    "Erro ao chamar Gemini. Status: %s | Resposta: %s",
                    response.status_code,
                    response.text,
                )
                return "Não consegui gerar resposta agora. Tente novamente."

            data = response.json()
            resposta = data["candidates"][0]["content"]["parts"][0]["text"].strip()

            if len(resposta) < 20 or resposta.endswith(
                ("Você pode", "Você pode ", "Certo.")
            ):
                return (
                    "Posso te ajudar melhor com mais detalhes.\n\n"
                    "O que aconteceu no seu dia?"
                )

            return resposta

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
            "Você é um assistente conversacional para apoio comunicacional de pessoas com TEA.\n"
            "Seu papel é conversar de forma guiada, clara e previsível.\n\n"
            "Regras obrigatórias:\n"
            "1. Responda em português do Brasil.\n"
            "2. Use linguagem literal, simples e direta.\n"
            "3. Não use metáforas, ironias ou duplo sentido.\n"
            "4. Não faça diagnóstico.\n"
            "5. Não substitua profissional de saúde.\n"
            "6. Não suponha sentimentos que o usuário não informou.\n"
            "7. Use apenas as informações dadas pelo usuário.\n"
            "8. Responda com no máximo 5 frases.\n"
            "9. Sempre finalize a resposta completa.\n\n"
            "Estilo de conversa guiada:\n"
            "- Comece validando a mensagem de forma neutra.\n"
            "- Organize a resposta em passos pequenos quando útil.\n"
            "- Faça apenas UMA pergunta por vez.\n"
            "- Se a mensagem for vaga, peça esclarecimento.\n"
            "- Se o usuário pedir ajuda para melhorar, pergunte primeiro o que ele quer melhorar.\n"
            "- Se o usuário falar sobre rotina, ajude a dividir em partes.\n"
            "- Se o usuário falar sobre tarefa, sugira um primeiro passo simples.\n"
            "- Se o usuário parecer sobrecarregado, reduza a quantidade de informação.\n\n"
            "Formato preferencial da resposta:\n"
            "1. Uma frase curta de acolhimento neutro.\n"
            "2. Uma orientação simples.\n"
            "3. Uma pergunta clara para continuar a conversa.\n\n"
            "Exemplo de boa resposta:\n"
            "Entendi.\n"
            "Vamos organizar isso em uma parte pequena.\n"
            "Qual é a primeira coisa que você quer resolver?\n\n"
        )

        contexto = ""

        if historico:
            mensagens_formatadas = []

            for item in historico[-6:]:
                role = item.get("role", "user")
                content = item.get("content", "")

                papel = "Assistente" if role == "assistant" else "Usuário"
                mensagens_formatadas.append(f"{papel}: {content}")

            contexto = "\n".join(mensagens_formatadas)

        return (
            f"{base}"
            f"Histórico recente:\n{contexto}\n\n"
            f"Mensagem atual do usuário:\n{mensagem_usuario}\n\n"
            "Resposta:"
        )
