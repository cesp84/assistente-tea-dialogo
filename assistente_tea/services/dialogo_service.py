from assistente_tea.models import BaseConhecimento


class DialogoService:
    SAUDACOES = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]

    REINICIAR = [
        "nova conversa",
        "reiniciar",
        "começar de novo",
        "comecar de novo",
        "zerar",
    ]

    def responder(self, mensagem: str, modo: str, contexto: dict | None = None) -> dict:
        mensagem = (mensagem or "").strip()
        texto = mensagem.lower()
        contexto = contexto or {}

        if not mensagem:
            return self._resposta_inicial()

        if texto in self.REINICIAR:
            return self._resposta_inicial()

        if texto in self.SAUDACOES:
            return self._saudacao()

        fluxo = contexto.get("fluxo")
        etapa = contexto.get("etapa", 0)

        registro = self._buscar_base_conhecimento(mensagem)
        if registro:
            return {
                "resposta": (
                    f"{registro.resposta}\n\n"
                    "Quer que eu te ajude mais com isso?\n"
                    "1. Sim\n"
                    "2. Não"
                ),
                "contexto": {
                    "fluxo": "base_conhecimento",
                    "etapa": 1,
                    "categoria": registro.categoria,
                },
            }

        if fluxo:
            return self._continuar_fluxo(mensagem, fluxo, etapa, contexto)

        fluxo_identificado = self._identificar_fluxo(texto, modo)

        if fluxo_identificado == "sobrecarga":
            return self._iniciar_sobrecarga()

        if fluxo_identificado == "tarefas":
            return self._iniciar_tarefas(mensagem)

        if fluxo_identificado == "comunicacao":
            return self._iniciar_comunicacao()

        return self._conversa_simples(mensagem)

    def _buscar_base_conhecimento(self, mensagem: str):
        texto = mensagem.lower()

        registros = BaseConhecimento.objects.filter(ativo=True)

        for registro in registros:
            if registro.gatilho.lower() in texto:
                return registro

        return None

    def _identificar_fluxo(self, texto: str, modo: str) -> str:
        # 🔥 Só força o modo se NÃO for simples
        if modo in ["sobrecarga", "tarefas"]:
            return modo

        # 🔥 Agora ele decide sozinho
        if any(
            p in texto
            for p in [
                "ansioso",
                "ansiedade",
                "sobrecarregado",
                "confuso",
                "nervoso",
                "irritado",
                "cansado",
            ]
        ):
            return "sobrecarga"

        if any(
            p in texto
            for p in [
                "preciso",
                "tarefa",
                "estudar",
                "fazer",
                "organizar",
                "trabalho",
            ]
        ):
            return "tarefas"

        if any(
            p in texto
            for p in [
                "não entendi",
                "nao entendi",
                "explique",
                "explica",
                "o que significa",
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
                "Escolha uma opção:\n"
                "1. Quero conversar de forma simples.\n"
                "2. Estou sobrecarregado.\n"
                "3. Quero organizar uma tarefa.\n"
                "4. Não entendi uma situação."
            ),
            "contexto": {
                "fluxo": "menu_inicial",
                "etapa": 1,
            },
        }

    def _continuar_fluxo(
        self, mensagem: str, fluxo: str, etapa: int, contexto: dict
    ) -> dict:
        if fluxo == "base_conhecimento":
            return self._continuar_base_conhecimento(mensagem)

        if fluxo == "menu_inicial":
            return self._continuar_menu_inicial(mensagem)

        if fluxo == "simples":
            return self._continuar_simples(mensagem)

        if fluxo == "sobrecarga":
            return self._continuar_sobrecarga(mensagem, etapa)

        if fluxo == "tarefas":
            return self._continuar_tarefas(mensagem, etapa, contexto)

        if fluxo == "comunicacao":
            return self._continuar_comunicacao(mensagem, etapa)

        return self._conversa_simples(mensagem)

    def _continuar_base_conhecimento(self, mensagem: str) -> dict:
        texto = mensagem.lower().strip()

        if texto in ["1", "sim", "s"]:
            return {
                "resposta": (
                    "Certo.\n\n"
                    "Você quer:\n"
                    "1. Organizar isso em passos\n"
                    "2. Explicar melhor\n"
                    "3. Criar uma ação prática"
                ),
                "contexto": {
                    "fluxo": "simples",
                    "etapa": 1,
                },
            }

        return {
            "resposta": "Tudo bem. Se precisar, estou aqui.",
            "contexto": {},
        }

    def _continuar_menu_inicial(self, mensagem: str) -> dict:
        texto = mensagem.lower().strip()

        if texto in ["1", "conversar", "conversa simples"]:
            return self._conversa_simples("Quero conversar de forma simples.")

        if texto in ["2", "sobrecarregado", "estou sobrecarregado"]:
            return self._iniciar_sobrecarga()

        if texto in ["3", "tarefa", "organizar tarefa"]:
            return {
                "resposta": "Certo. Qual tarefa você quer organizar?",
                "contexto": {
                    "fluxo": "tarefas",
                    "etapa": 0,
                },
            }

        if texto in ["4", "não entendi", "nao entendi", "situação", "situacao"]:
            return self._iniciar_comunicacao()

        return {
            "resposta": (
                "Não entendi a opção.\n\n"
                "Responda com um número:\n"
                "1. Conversa simples\n"
                "2. Estou sobrecarregado\n"
                "3. Organizar tarefa\n"
                "4. Não entendi uma situação"
            ),
            "contexto": {
                "fluxo": "menu_inicial",
                "etapa": 1,
            },
        }

    def _conversa_simples(self, mensagem: str) -> dict:
        return {
            "resposta": (
                "Entendi.\n\n"
                f"Você disse: {mensagem}\n\n"
                "Como você quer que eu ajude?\n\n"
                "1. Explicar melhor.\n"
                "2. Organizar em passos.\n"
                "3. Criar uma resposta curta."
            ),
            "contexto": {
                "fluxo": "simples",
                "etapa": 1,
                "mensagem_original": mensagem,
            },
        }

    def _continuar_simples(self, mensagem: str) -> dict:
        texto = mensagem.lower().strip()

        if texto in ["1", "explicar", "explicar melhor"]:
            return {
                "resposta": (
                    "Certo. Vou explicar de forma simples.\n\n"
                    "Para eu ajudar melhor, escreva qual parte você quer entender."
                ),
                "contexto": {
                    "fluxo": "comunicacao",
                    "etapa": 1,
                },
            }

        if texto in ["2", "organizar", "organizar em passos"]:
            return {
                "resposta": "Certo. Escreva a tarefa ou assunto que você quer organizar.",
                "contexto": {
                    "fluxo": "tarefas",
                    "etapa": 0,
                },
            }

        if texto in ["3", "resposta curta", "criar resposta curta"]:
            return {
                "resposta": (
                    "Resposta curta sugerida:\n\n"
                    "Entendi. Vou pensar com calma e responder depois."
                ),
                "contexto": {},
            }

        return {
            "resposta": (
                "Escolha uma opção:\n"
                "1. Explicar melhor\n"
                "2. Organizar em passos\n"
                "3. Criar uma resposta curta"
            ),
            "contexto": {
                "fluxo": "simples",
                "etapa": 1,
            },
        }

    def _iniciar_sobrecarga(self) -> dict:
        return {
            "resposta": (
                "Entendi. Vamos reduzir a quantidade de informação.\n\n"
                "Primeiro: respire devagar por alguns segundos.\n\n"
                "Agora escolha:\n"
                "1. Quero silêncio.\n"
                "2. Quero organizar meus pensamentos.\n"
                "3. Quero explicar o que aconteceu."
            ),
            "contexto": {
                "fluxo": "sobrecarga",
                "etapa": 1,
            },
        }

    def _continuar_sobrecarga(self, mensagem: str, etapa: int) -> dict:
        if etapa == 1:
            return {
                "resposta": (
                    "Certo.\n\n"
                    "Agora me diga em poucas palavras:\n"
                    "o que está incomodando mais neste momento?"
                ),
                "contexto": {
                    "fluxo": "sobrecarga",
                    "etapa": 2,
                    "preferencia": mensagem,
                },
            }

        return {
            "resposta": (
                "Entendi.\n\n"
                f"O incômodo principal é: {mensagem}\n\n"
                "Ação simples:\n"
                "reduza uma coisa que aumenta esse incômodo, se for possível.\n\n"
                "Depois responda: melhorou um pouco?"
            ),
            "contexto": {
                "fluxo": "sobrecarga",
                "etapa": 3,
            },
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

    def _continuar_tarefas(self, mensagem: str, etapa: int, contexto: dict) -> dict:
        if etapa == 0:
            return self._iniciar_tarefas(mensagem)

        if etapa == 1:
            return {
                "resposta": (
                    "Ótimo.\n\n"
                    f"Primeiro passo: {mensagem}\n\n"
                    "Você consegue fazer isso em até 10 minutos?\n"
                    "Responda: sim ou não."
                ),
                "contexto": {
                    **contexto,
                    "fluxo": "tarefas",
                    "etapa": 2,
                    "primeiro_passo": mensagem,
                },
            }

        texto = mensagem.lower().strip()

        if texto in ["sim", "s"]:
            return {
                "resposta": (
                    "Perfeito.\n\n"
                    "Faça apenas esse primeiro passo agora.\n\n"
                    "Quando terminar, escreva: concluído."
                ),
                "contexto": {
                    "fluxo": "tarefas",
                    "etapa": 3,
                },
            }

        if texto in ["concluído", "concluido", "terminei", "feito"]:
            return {
                "resposta": (
                    "Muito bem.\n\n"
                    "Agora escolha:\n"
                    "1. Continuar para o próximo passo\n"
                    "2. Encerrar por enquanto"
                ),
                "contexto": {
                    "fluxo": "tarefas_concluidas",
                    "etapa": 1,
                },
            }

        return {
            "resposta": (
                "Tudo bem.\n\n"
                "Então vamos reduzir mais.\n\n"
                "Escreva uma versão menor desse primeiro passo."
            ),
            "contexto": {
                "fluxo": "tarefas",
                "etapa": 1,
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

    def _continuar_comunicacao(self, mensagem: str, etapa: int) -> dict:
        if etapa == 1:
            return {
                "resposta": (
                    "Entendi.\n\n"
                    f"Situação: {mensagem}\n\n"
                    "Qual parte você não entendeu?"
                ),
                "contexto": {
                    "fluxo": "comunicacao",
                    "etapa": 2,
                    "situacao": mensagem,
                },
            }

        return {
            "resposta": (
                "Certo.\n\n"
                f"Parte confusa: {mensagem}\n\n"
                "Uma pergunta direta que você pode usar é:\n\n"
                '"Você pode explicar isso de outro jeito?"'
            ),
            "contexto": {},
        }
