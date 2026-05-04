import json
from django.core.management.base import BaseCommand
from assistente_tea.models import BaseConhecimento


class Command(BaseCommand):
    help = "Importa base de conhecimento a partir de um arquivo JSON"

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=str, help="Caminho do arquivo JSON")

    def handle(self, *args, **options):
        caminho_arquivo = options["arquivo"]

        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao ler arquivo: {e}"))
            return

        count = 0

        for item in dados:
            obj, created = BaseConhecimento.objects.get_or_create(
                gatilho=item["gatilho"],
                defaults={
                    "categoria": item["categoria"],
                    "resposta": item["resposta"],
                    "ativo": item.get("ativo", True),
                },
            )

            if created:
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f"{count} registros importados com sucesso.")
        )
