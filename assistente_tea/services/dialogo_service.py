class DialogoService:
    def responder(self, mensagem: str, modo: str = "simples") -> dict:
        mensagem = (mensagem or "").strip()
        modo = modo or "simples"

        if not mensagem:
            return {
                "tipo": "orientacao",
                "resposta": "Escreva uma mensagem curta para eu te ajudar.",
            }

        if modo == "sobrecarga":
            return self._resposta_sobrecarga()

        if modo == "tarefas":
            return self._resposta_tarefas(mensagem)

        return self._resposta_simples(mensagem)

    def _resposta_simples(self, mensagem: str) -> dict:
        return {
            "tipo": "simples",
            "resposta": (
                "Entendi.\n\n"
                "Vou responder de forma clara e organizada.\n\n"
                "1. Você trouxe uma informação importante.\n"
                "2. Podemos dividir isso em partes menores.\n"
                "3. Escolha uma parte para começarmos agora."
            ),
        }

    def _resposta_sobrecarga(self) -> dict:
        return {
            "tipo": "sobrecarga",
            "resposta": (
                "Vamos reduzir a quantidade de coisas agora.\n\n"
                "Faça somente isto:\n\n"
                "1. Pare por alguns segundos.\n"
                "2. Respire devagar.\n"
                "3. Escolha uma opção:\n\n"
                "- Quero silêncio.\n"
                "- Quero organizar meus pensamentos.\n"
                "- Quero explicar o que aconteceu."
            ),
        }

    def _resposta_tarefas(self, mensagem: str) -> dict:
        return {
            "tipo": "tarefas",
            "resposta": (
                "Vamos transformar isso em passos pequenos.\n\n"
                f"Tarefa informada: {mensagem}\n\n"
                "1. Escolha apenas uma parte da tarefa.\n"
                "2. Faça essa parte primeiro.\n"
                "3. Depois revise o que falta.\n\n"
                "Comece pelo item mais simples."
            ),
        }
