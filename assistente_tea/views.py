from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Interacao
from .services.dialogo_service import DialogoService


def chat(request):
    request.session.setdefault("dialogo_contexto", {})
    return render(request, "assistente_tea/chat.html")


@require_POST
def enviar_mensagem(request):
    mensagem = request.POST.get("mensagem", "")
    modo = request.POST.get("modo", "auto")
    contexto = request.session.get("dialogo_contexto", {})

    service = DialogoService()

    resultado = service.responder(
        mensagem=mensagem,
        modo=modo,
        contexto=contexto,
    )

    novo_contexto = resultado.get("contexto", {})

    request.session["dialogo_contexto"] = novo_contexto
    request.session.modified = True

    Interacao.objects.create(
        mensagem_usuario=mensagem,
        resposta_sistema=resultado["resposta"],
        modo=modo,
    )

    return JsonResponse(
        {
            "resposta": resultado["resposta"],
            "contexto": novo_contexto,
        }
    )


def nova_conversa(request):
    request.session["dialogo_contexto"] = {}
    request.session.modified = True

    return redirect("assistente_tea:chat")
