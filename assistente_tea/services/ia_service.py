import requests
from django.conf import settings


class IAService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={self.api_key}"

    def gerar_resposta_ia(self, mensagem_usuario: str, historico: list = None) -> str:
        prompt = self._montar_prompt(mensagem_usuario, historico)

        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(self.url, json=payload)

        if response.status_code != 200:
            return "Não consegui gerar resposta agora. Tente novamente."

        data = response.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "Não consegui entender a resposta agora."

    def _montar_prompt(self, mensagem_usuario: str, historico: list) -> str:
        base = (
            "Você é um assistente para pessoas com TEA.\n"
            "- Seja claro, direto e literal\n"
            "- Use frases curtas\n"
            "- Evite metáforas\n"
            "- Seja previsível e organizado\n\n"
        )

        if historico:
            contexto = "\n".join(
                [f"{m['role']}: {m['content']}" for m in historico[-6:]]
            )
        else:
            contexto = ""

        return f"{base}\n{contexto}\nUsuário: {mensagem_usuario}"
