from assistente_tea.models import Interacao


class HistoricoService:
    LIMITE_INTERACOES = 6

    def buscar_historico_recente(self) -> list:
        interacoes = Interacao.objects.order_by("-criado_em")[: self.LIMITE_INTERACOES]

        historico = []

        for interacao in reversed(interacoes):
            historico.append(
                {
                    "role": "user",
                    "content": interacao.mensagem_usuario,
                }
            )
            historico.append(
                {
                    "role": "assistant",
                    "content": interacao.resposta_sistema,
                }
            )

        return historico
