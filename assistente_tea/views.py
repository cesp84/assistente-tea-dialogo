from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
import logging

from .models import Interacao
from .services.dialogo_service import DialogoService

logger = logging.getLogger(__name__)


def chat(request):
    # Garante que o contexto exista na sessão
    if "dialogo_contexto" not in request.session:
        request.session["dialogo_contexto"] = {}
    return render(request, "assistente_tea/chat.html")


@require_POST
def enviar_mensagem(request):
    mensagem = request.POST.get("mensagem", "").strip()
    modo = request.POST.get("modo", "auto")

    # Validação básica de entrada
    if not mensagem:
        return JsonResponse(
            {
                "resposta": "Por favor, escreva uma mensagem para continuarmos.",
                "contexto": request.session.get("dialogo_contexto", {}),
            },
            status=400,
        )

    contexto = request.session.get("dialogo_contexto", {})
    service = DialogoService()

    try:
        resultado = service.responder(
            mensagem=mensagem,
            modo=modo,
            contexto=contexto,
        )

        novo_contexto = resultado.get("contexto", {})
        resposta_texto = resultado.get(
            "resposta", "Não consegui gerar uma resposta adequada."
        )

        # Atualiza sessão
        request.session["dialogo_contexto"] = novo_contexto
        request.session.modified = True

        # Persiste interação (assíncrono idealmente, mas síncrono ok para protótipo)
        Interacao.objects.create(
            mensagem_usuario=mensagem,
            resposta_sistema=resposta_texto,
            modo=modo,
        )

        return JsonResponse(
            {
                "resposta": resposta_texto,
                "contexto": novo_contexto,
            }
        )

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
        # Mensagem amigável e previsível para o usuário
        return JsonResponse(
            {
                "resposta": "Tive um pequeno problema técnico ao entender sua mensagem. Por favor, tente reformular ou envie novamente.",
                "contexto": request.session.get("dialogo_contexto", {}),
            },
            status=500,
        )


def nova_conversa(request):
    request.session["dialogo_contexto"] = {}
    request.session.modified = True
    return redirect("assistente_tea:chat")
