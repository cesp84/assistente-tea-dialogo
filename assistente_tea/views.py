from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
import logging

from .models import Interacao
from .services.dialogo_service import DialogoService

logger = logging.getLogger(__name__)


def chat(request):
    """
    Renderiza a página inicial do chat.
    Garante que o contexto da conversa exista na sessão.
    """
    # Inicializa o contexto na sessão se não existir
    if "dialogo_contexto" not in request.session:
        request.session["dialogo_contexto"] = {}

    return render(request, "assistente_tea/chat.html")


@require_POST
def enviar_mensagem(request):
    """
    Processa a mensagem enviada pelo usuário via AJAX.
    Retorna JSON com a resposta do assistente e o novo contexto.
    """
    mensagem = request.POST.get("mensagem", "").strip()
    modo = request.POST.get("modo", "auto")

    # 1. Validação de Entrada
    if not mensagem:
        return JsonResponse(
            {
                "resposta": "Por favor, escreva uma mensagem para continuarmos.",
                "contexto": request.session.get("dialogo_contexto", {}),
            },
            status=400,
        )

    # Recupera o contexto atual da sessão
    contexto_atual = request.session.get("dialogo_contexto", {})
    service = DialogoService()

    try:
        # 2. Processamento da Lógica (DialogoService + IA se aplicável)
        resultado = service.responder(
            mensagem=mensagem,
            modo=modo,
            contexto=contexto_atual,
        )

        novo_contexto = resultado.get("contexto", {})
        resposta_texto = resultado.get(
            "resposta", "Não consegui gerar uma resposta adequada."
        )

        # 3. Atualização da Sessão
        # Importante: marcar a sessão como modificada para garantir o save
        request.session["dialogo_contexto"] = novo_contexto
        request.session.modified = True

        # 4. Persistência da Interação (Log/Histórico)
        # Nota: Em produção, considere usar celery para isso não atrasar a resposta HTTP
        try:
            Interacao.objects.create(
                mensagem_usuario=mensagem,
                resposta_sistema=resposta_texto,
                modo=modo,
            )
        except Exception as db_error:
            # Logamos o erro de banco, mas NÃO falhamos a requisição do usuário
            logger.warning(f"Falha ao salvar interação no banco: {db_error}")

        # 5. Resposta ao Frontend
        return JsonResponse(
            {
                "resposta": resposta_texto,
                "contexto": novo_contexto,
            }
        )

    except Exception as e:
        # Log detalhado para desenvolvedores/administradores
        logger.error(f"Erro crítico ao processar mensagem: {e}", exc_info=True)

        # Resposta amigável e previsível para o usuário (Crucial para TEA)
        return JsonResponse(
            {
                "resposta": "Tive um pequeno problema técnico ao entender sua mensagem. Por favor, tente reformular ou envie novamente.",
                "contexto": request.session.get("dialogo_contexto", {}),
            },
            status=500,
        )


def nova_conversa(request):
    """
    Reseta o contexto da conversa e redireciona para o início.
    """
    request.session["dialogo_contexto"] = {}
    request.session.modified = True
    return redirect("assistente_tea:chat")
