# assistente_tea/services/historico_service.py
from assistente_tea.models import Interacao


class HistoricoService:
    LIMITE_INTERACOES = 6

    def buscar_historico_recente(self, session_key: str) -> list:
        if not session_key:
            return []

        # Filtra explicitamente pela sessão do usuário atual
        interacoes = Interacao.objects.filter(session_key=session_key).order_by(
            "-criado_em"
        )[: self.LIMITE_INTERACOES]

        historico = []

        # Reverte para ordem cronológica (mais antigo primeiro) para contexto da IA
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
