from django.urls import path

from . import views

app_name = "assistente_tea"

urlpatterns = [
    path("", views.chat, name="chat"),
    path("enviar/", views.enviar_mensagem, name="enviar_mensagem"),
    path("nova-conversa/", views.nova_conversa, name="nova_conversa"),
]
