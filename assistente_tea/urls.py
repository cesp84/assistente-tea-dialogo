from django.urls import path

from . import views

app_name = "assistente_tea"

urlpatterns = [
    path("", views.chat, name="chat"),
    path("enviar/", views.enviar_mensagem, name="enviar_mensagem"),
]
