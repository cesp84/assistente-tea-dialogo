from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import Interacao
from .services.dialogo_service import DialogoService


def chat(request):
    return render(request, "assistente_tea/chat.html")


@require_POST
def enviar_mensagem(request):
    mensagem = request.POST.get("mensagem", "")
    modo = request.POST.get("modo", "simples")

    service = DialogoService()
    resultado = service.responder(mensagem=mensagem, modo=modo)

    Interacao.objects.create(
        mensagem_usuario=mensagem,
        resposta_sistema=resultado["resposta"],
        modo=modo,
    )

    return JsonResponse(resultado)
