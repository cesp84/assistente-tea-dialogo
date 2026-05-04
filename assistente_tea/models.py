from django.db import models


class Interacao(models.Model):
    MODO_CHOICES = [
        ("simples", "Conversa simples"),
        ("sobrecarga", "Estou sobrecarregado"),
        ("tarefas", "Organizar tarefa"),
    ]

    mensagem_usuario = models.TextField()
    resposta_sistema = models.TextField()
    modo = models.CharField(max_length=30, choices=MODO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_modo_display()} - {self.criado_em:%d/%m/%Y %H:%M}"
