import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .services.historico_service import HistoricoService
from .models import Interacao
from .services.dialogo_service import DialogoService

logger = logging.getLogger(__name__)


def chat(request):
    """
    Renderiza a página inicial do chat.
    Garante que o contexto e o histórico existam na sessão.
    """
    request.session.setdefault("dialogo_contexto", {})
    request.session.setdefault("dialogo_historico", [])

    return render(request, "assistente_tea/chat.html")


@require_POST
def enviar_mensagem(request):
    mensagem = request.POST.get("mensagem", "").strip()
    modo = request.POST.get("modo", "auto")

    contexto = request.session.get("dialogo_contexto", {})
    historico = HistoricoService().buscar_historico_recente()

    if not isinstance(contexto, dict):
        contexto = {}

    if not isinstance(historico, list):
        historico = []

    service = DialogoService()

    resultado = service.responder(
        mensagem=mensagem,
        modo=modo,
        contexto=contexto,
        historico=historico,
    )

    resposta = resultado.get("resposta", "")
    novo_contexto = resultado.get("contexto", {})

    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": resposta})

    request.session["dialogo_contexto"] = novo_contexto
    request.session["dialogo_historico"] = historico[-10:]
    request.session.modified = True

    Interacao.objects.create(
        mensagem_usuario=mensagem,
        resposta_sistema=resposta,
        modo=modo,
    )

    return JsonResponse(
        {
            "resposta": resposta,
            "contexto": novo_contexto,
        }
    )


def nova_conversa(request):
    """
    Reinicia o contexto e o histórico da conversa.
    """
    request.session["dialogo_contexto"] = {}
    request.session["dialogo_historico"] = []
    request.session.modified = True

    return redirect("assistente_tea:chat")
