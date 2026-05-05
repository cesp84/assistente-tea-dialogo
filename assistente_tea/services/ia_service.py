import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class IAService:
    def __init__(self):
        # Não levanta erro aqui. Permite inicialização sem chave.
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        self.modelos = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ]

    def _montar_url(self, modelo: str) -> str:
        if not self.api_key:
            raise ValueError("Chave da API não configurada.")
        return (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{modelo}:generateContent?key={self.api_key}"
        )

    def gerar_resposta_ia(
        self, mensagem_usuario: str, historico: list | None = None
    ) -> str:
        # Validação tardia da chave
        if not self.api_key:
            logger.warning("Tentativa de uso de IA sem GEMINI_API_KEY configurada.")
            return self._get_fallback_message()

        prompt = self._montar_prompt(mensagem_usuario, historico or [])

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 800,
                "topK": 40,
                "topP": 0.95,
            },
        }

        for modelo in self.modelos:
            try:
                url = self._montar_url(
                    modelo
                )  # Pode levantar ValueError se chave sumir dinamicamente
                logger.info("Chamando Gemini com modelo: %s", modelo)

                response = requests.post(
                    url,
                    json=payload,
                    timeout=20,
                )

                if response.status_code == 200:
                    return self._extrair_resposta(response.json(), modelo)

                logger.warning(
                    "Falha no Gemini. Modelo: %s | Status: %s | Resposta: %s",
                    modelo,
                    response.status_code,
                    response.text[
                        :200
                    ],  # Limita log para evitar vazamento de dados sensíveis no log
                )

            except requests.Timeout:
                logger.warning("Tempo limite ao chamar Gemini. Modelo: %s", modelo)

            except requests.RequestException as e:
                logger.error(
                    "Erro de conexão com Gemini. Modelo: %s | Erro: %s",
                    modelo,
                    e,
                    exc_info=True,
                )

            except ValueError:
                # Captura erro de chave ausente na montagem da URL
                break

            except Exception as e:
                logger.error(
                    "Erro inesperado no Gemini. Modelo: %s | Erro: %s",
                    modelo,
                    e,
                    exc_info=True,
                )

        return self._get_fallback_message()

    def _get_fallback_message(self) -> str:
        return (
            "O serviço de IA está instável agora.\n\n"
            "Vamos continuar de forma simples.\n"
            "O que aconteceu primeiro?"
        )

    def _extrair_resposta(self, data: dict, modelo: str) -> str:
        try:
            candidate = data["candidates"][0]
            parts = candidate.get("content", {}).get("parts", [])

            resposta = "\n".join(
                part.get("text", "") for part in parts if part.get("text")
            ).strip()

            finish_reason = candidate.get("finishReason")

            if finish_reason == "MAX_TOKENS" or len(resposta) < 30:
                logger.warning(
                    "Resposta incompleta do Gemini. Modelo: %s | FinishReason: %s",
                    modelo,
                    finish_reason,
                )
                return (
                    "Entendi.\n\n"
                    "Podemos dividir isso em partes pequenas.\n"
                    "O que aconteceu primeiro?"
                )

            if resposta.endswith(("Você pode", "Você pode ", "Certo.")):
                logger.warning("Resposta possivelmente truncada. Modelo: %s", modelo)
                return (
                    "Entendi.\n\n"
                    "Podemos conversar com calma.\n"
                    "O que você quer me contar primeiro?"
                )

            return resposta

        except Exception as e:
            logger.error(
                "Erro ao extrair resposta do Gemini. Modelo: %s | Erro: %s",
                modelo,
                e,
                exc_info=True,
            )
            return (
                "Não consegui entender a resposta da IA agora.\n\n"
                "Vamos continuar de forma simples.\n"
                "O que você quer resolver primeiro?"
            )

    def _montar_prompt(self, mensagem_usuario: str, historico: list) -> str:
        base = (
            "Você é um assistente conversacional para apoio comunicacional de pessoas com TEA.\n"
            "Seu papel é conversar de forma guiada, clara, previsível e segura.\n\n"
            "Regras obrigatórias:\n"
            "1. Responda em português do Brasil.\n"
            "2. Use linguagem literal, simples e direta.\n"
            "3. Não use metáforas, ironias ou duplo sentido.\n"
            "4. Não faça diagnóstico.\n"
            "5. Não substitua profissional de saúde.\n"
            "6. Não suponha sentimentos que o usuário não informou.\n"
            "7. Use apenas as informações dadas pelo usuário.\n"
            "8. Sempre finalize a resposta completa.\n"
            "9. Não termine com frase aberta ou incompleta.\n"
            "10. Nunca atribua emoções ao usuário sem confirmação explícita.\n"
            "11. Analise a mensagem com atenção antes de responder.\n"
            "12. Evite conclusões rápidas.\n"
            "13. Se houver dúvida, peça mais informação.\n"
            "14. Priorize clareza e precisão.\n"
            "15. Se houver múltiplas interpretações, escolha a mais neutra.\n\n"
            "Modos de resposta (escolha automaticamente):\n"
            "- Curta: até 2 frases. Para respostas diretas.\n"
            "- Guiada: 3 frases com uma pergunta final. Para continuar conversa.\n"
            "- Explicativa: explicar em passos simples (máx. 5 itens).\n\n"
            "Escolha do modo:\n"
            "- Pergunta simples → Curta\n"
            "- Conversa aberta → Guiada\n"
            "- Pedido de explicação → Explicativa\n"
            "- Dúvida → Guiada\n\n"
            "Estilo de conversa:\n"
            "- Comece com validação neutra (ex: 'Entendi.').\n"
            "- Use frases curtas.\n"
            "- Use estrutura previsível.\n"
            "- Faça apenas UMA pergunta por vez.\n"
            "- Se a mensagem for vaga, peça esclarecimento.\n"
            "- Divida assuntos em partes pequenas.\n"
            "- Sugira sempre um primeiro passo simples.\n"
            "- Reduza informações se houver risco de sobrecarga.\n\n"
            "Formato padrão (quando aplicável):\n"
            "1. Validação curta.\n"
            "2. Orientação simples.\n"
            "3. Pergunta clara.\n\n"
            "Exemplo:\n"
            "Entendi.\n"
            "Podemos organizar isso em uma parte pequena.\n"
            "Qual é a primeira coisa que você quer resolver?\n\n"
        )
        # base = (
        #     "Você é um assistente conversacional para apoio comunicacional de pessoas com TEA.\n"
        #     "Responda em português do Brasil.\n"
        #     "Use linguagem literal, simples e direta.\n"
        #     "Não use metáforas, ironias ou duplo sentido.\n"
        #     "Não faça diagnóstico nem substitua profissional de saúde.\n"
        #     "Não suponha sentimentos que o usuário não informou.\n"
        #     "Se houver dúvida, peça mais informação.\n"
        #     "Faça apenas uma pergunta por vez.\n"
        #     "Responda de forma curta, completa e previsível.\n"
        # )

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
