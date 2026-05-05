import unicodedata

from assistente_tea.services.ia_service import IAService


class DialogoService:
    SAUDACOES = ["oi", "ola", "olá", "bom dia", "boa tarde", "boa noite"]

    COMANDOS_GLOBAIS = {
        "reiniciar": [
            "nova conversa",
            "reiniciar",
            "começar de novo",
            "comecar de novo",
            "zerar",
        ],
        "sair": ["parar", "sair", "cancelar", "voltar", "menu"],
    }

    def _normalizar_texto(self, texto: str) -> str:
        if not texto:
            return ""

        nfkd_form = unicodedata.normalize("NFKD", texto)
        texto_ascii = nfkd_form.encode("ASCII", "ignore").decode("ASCII")

        return texto_ascii.lower().strip()

    def responder(
        self,
        mensagem: str,
        modo: str = "auto",
        contexto: dict | None = None,
        historico: list | None = None,
    ) -> dict:
        mensagem_original = (mensagem or "").strip()
        texto_normalizado = self._normalizar_texto(mensagem_original)
        contexto = contexto or {}
        historico = historico or []

        if not texto_normalizado:
            return self._resposta_inicial()

        if texto_normalizado in self.COMANDOS_GLOBAIS["reiniciar"]:
            return self._resposta_inicial()

        if texto_normalizado in self.COMANDOS_GLOBAIS["sair"]:
            return self._saudacao()

        if texto_normalizado in self.SAUDACOES:
            return self._saudacao()

        fluxo = contexto.get("fluxo")
        etapa = contexto.get("etapa", 0)

        if fluxo:
            return self._continuar_fluxo(
                mensagem_original=mensagem_original,
                texto_normalizado=texto_normalizado,
                fluxo=fluxo,
                etapa=etapa,
                contexto=contexto,
                historico=historico,
            )

        fluxo_identificado = self._identificar_fluxo(texto_normalizado, modo)

        if fluxo_identificado == "sobrecarga":
            return self._iniciar_sobrecarga()

        if fluxo_identificado == "tarefas":
            return self._iniciar_tarefas(mensagem_original)

        if fluxo_identificado == "comunicacao":
            return self._iniciar_comunicacao()

        return self._conversa_simples(mensagem_original, historico)

    def _identificar_fluxo(self, texto: str, modo: str) -> str:
        if modo in ["sobrecarga", "tarefas"]:
            return modo

        if any(
            palavra in texto
            for palavra in [
                "ansioso",
                "ansiedade",
                "sobrecarregado",
                "confuso",
                "nervoso",
                "irritado",
                "cansado",
                "estressado",
            ]
        ):
            return "sobrecarga"

        if any(
            palavra in texto
            for palavra in [
                "preciso",
                "tarefa",
                "estudar",
                "fazer",
                "organizar",
                "trabalho",
                "lista",
                "passo",
            ]
        ):
            return "tarefas"

        if any(
            palavra in texto
            for palavra in [
                "nao entendi",
                "explique",
                "explica",
                "o que significa",
                "duvida",
            ]
        ):
            return "comunicacao"

        return "simples"

    def _resposta_inicial(self) -> dict:
        return {
            "resposta": (
                "Conversa reiniciada.\n\n"
                "Você pode escrever uma mensagem curta.\n\n"
                "Exemplos:\n"
                "- Estou ansioso.\n"
                "- Preciso estudar.\n"
                "- Não entendi uma situação."
            ),
            "contexto": {},
        }

    def _saudacao(self) -> dict:
        return {
            "resposta": (
                "Olá. Estou aqui para ajudar.\n\n"
                "Você pode escrever livremente o que precisa.\n"
                "Eu vou tentar adaptar a resposta ao contexto."
            ),
            "contexto": {},
        }

    def _continuar_fluxo(
        self,
        mensagem_original: str,
        texto_normalizado: str,
        fluxo: str,
        etapa: int,
        contexto: dict,
        historico: list,
    ) -> dict:
        if texto_normalizado in self.COMANDOS_GLOBAIS["sair"]:
            return self._saudacao()

        if texto_normalizado in self.COMANDOS_GLOBAIS["reiniciar"]:
            return self._resposta_inicial()

        if fluxo == "simples":
            return self._conversa_simples(mensagem_original, historico)

        if fluxo == "sobrecarga":
            return self._continuar_sobrecarga(mensagem_original, etapa)

        if fluxo == "tarefas":
            return self._continuar_tarefas(
                mensagem_original, texto_normalizado, etapa, contexto
            )

        if fluxo == "comunicacao":
            return self._continuar_comunicacao(mensagem_original, etapa)

        return self._conversa_simples(mensagem_original, historico)

    def _conversa_simples(self, mensagem: str, historico: list | None = None) -> dict:
        try:
            ia_service = IAService()
            resposta_ia = ia_service.gerar_resposta_ia(
                mensagem_usuario=mensagem,
                historico=historico or [],
            )

            return {
                "resposta": resposta_ia,
                "contexto": {
                    "fluxo": "simples",
                    "etapa": 1,
                    "mensagem_original": mensagem,
                },
            }

        except Exception:
            return {
                "resposta": (
                    "Entendi.\n\n"
                    "Vou responder de forma simples.\n\n"
                    "1. Podemos organizar isso em partes menores.\n"
                    "2. Você pode me dizer o que quer resolver primeiro."
                ),
                "contexto": {
                    "fluxo": "simples",
                    "etapa": 1,
                    "mensagem_original": mensagem,
                },
            }

    def _iniciar_sobrecarga(self) -> dict:
        return {
            "resposta": (
                "Entendi. Vamos reduzir a quantidade de informação.\n\n"
                "Primeiro: respire devagar por alguns segundos.\n\n"
                "Agora me diga em poucas palavras:\n"
                "o que está incomodando mais neste momento?"
            ),
            "contexto": {
                "fluxo": "sobrecarga",
                "etapa": 1,
            },
        }

    def _continuar_sobrecarga(self, mensagem_original: str, etapa: int) -> dict:
        if etapa == 1:
            return {
                "resposta": (
                    "Entendi.\n\n"
                    f"O incômodo principal é: {mensagem_original}\n\n"
                    "Ação simples:\n"
                    "reduza uma coisa que aumenta esse incômodo, se for possível.\n\n"
                    "Depois responda: melhorou um pouco?"
                ),
                "contexto": {
                    "fluxo": "sobrecarga",
                    "etapa": 2,
                },
            }

        return {
            "resposta": (
                "Certo.\n\n"
                "Vamos manter simples:\n"
                "1. Continue em um ambiente mais calmo, se possível.\n"
                "2. Faça apenas uma coisa por vez.\n"
                "3. Quando quiser, escreva 'nova conversa' para recomeçar."
            ),
            "contexto": {},
        }

    def _iniciar_tarefas(self, mensagem: str) -> dict:
        return {
            "resposta": (
                "Vamos organizar essa tarefa em partes pequenas.\n\n"
                f"Tarefa: {mensagem}\n\n"
                "Qual é o primeiro passo mais fácil?"
            ),
            "contexto": {
                "fluxo": "tarefas",
                "etapa": 1,
                "tarefa_original": mensagem,
            },
        }

    def _continuar_tarefas(
        self,
        mensagem_original: str,
        texto_normalizado: str,
        etapa: int,
        contexto: dict,
    ) -> dict:
        if etapa == 1:
            return {
                "resposta": (
                    "Ótimo.\n\n"
                    f"Primeiro passo: {mensagem_original}\n\n"
                    "Você consegue fazer isso em até 10 minutos?\n"
                    "Responda: sim ou não."
                ),
                "contexto": {
                    **contexto,
                    "fluxo": "tarefas",
                    "etapa": 2,
                    "primeiro_passo": mensagem_original,
                },
            }

        if etapa == 2 and texto_normalizado in ["sim", "s"]:
            return {
                "resposta": (
                    "Perfeito.\n\n"
                    "Faça apenas esse primeiro passo agora.\n\n"
                    "Quando terminar, escreva: concluído."
                ),
                "contexto": {
                    **contexto,
                    "fluxo": "tarefas",
                    "etapa": 3,
                },
            }

        if etapa == 2 and texto_normalizado in ["nao", "não", "n"]:
            return {
                "resposta": (
                    "Tudo bem.\n\n"
                    "Então vamos reduzir mais.\n\n"
                    "Escreva uma versão menor desse primeiro passo."
                ),
                "contexto": {
                    **contexto,
                    "fluxo": "tarefas",
                    "etapa": 1,
                },
            }

        if etapa == 3 and texto_normalizado in [
            "concluido",
            "concluído",
            "terminei",
            "feito",
        ]:
            return {
                "resposta": (
                    "Muito bem.\n\n"
                    "Você concluiu um passo.\n\n"
                    "Agora escolha:\n"
                    "1. Continuar com outro passo\n"
                    "2. Encerrar por enquanto"
                ),
                "contexto": {
                    **contexto,
                    "fluxo": "tarefas",
                    "etapa": 4,
                },
            }

        if etapa == 4 and texto_normalizado in ["1", "continuar", "outro passo"]:
            return {
                "resposta": "Certo. Qual é o próximo passo mais simples?",
                "contexto": {
                    **contexto,
                    "fluxo": "tarefas",
                    "etapa": 1,
                },
            }

        if etapa == 4 and texto_normalizado in ["2", "encerrar", "parar"]:
            return {
                "resposta": "Certo. Encerramos por enquanto. Bom trabalho.",
                "contexto": {},
            }

        return {
            "resposta": (
                "Não entendi com segurança.\n\n"
                "Responda de forma simples:\n"
                "- sim\n"
                "- não\n"
                "- concluído\n"
                "- nova conversa"
            ),
            "contexto": {
                **contexto,
                "fluxo": "tarefas",
                "etapa": etapa,
            },
        }

    def _iniciar_comunicacao(self) -> dict:
        return {
            "resposta": (
                "Vamos entender a situação com calma.\n\n"
                "Me diga apenas isto:\n"
                "o que aconteceu?"
            ),
            "contexto": {
                "fluxo": "comunicacao",
                "etapa": 1,
            },
        }

    def _continuar_comunicacao(self, mensagem_original: str, etapa: int) -> dict:
        if etapa == 1:
            return {
                "resposta": (
                    "Entendi.\n\n"
                    f"Situação: {mensagem_original}\n\n"
                    "Qual parte você não entendeu?"
                ),
                "contexto": {
                    "fluxo": "comunicacao",
                    "etapa": 2,
                    "situacao": mensagem_original,
                },
            }

        return {
            "resposta": (
                "Certo.\n\n"
                f"Parte confusa: {mensagem_original}\n\n"
                "Uma pergunta direta que você pode usar é:\n\n"
                '"Você pode explicar isso de outro jeito?"'
            ),
            "contexto": {},
        }
