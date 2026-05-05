import openai
from django.conf import settings


class IAService:
    def __init__(self):
        # Inicializa o cliente OpenAI com a chave carregada no settings
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def gerar_resposta_ia(self, mensagem_usuario: str, historico: list = None) -> str:
        """
        Gera uma resposta empática, clara e literal, adequada para TEA.
        """
        # Prompt de Sistema: Define a personalidade do assistente
        system_prompt = (
            "Você é um assistente virtual projetado para ajudar pessoas no Espectro Autista (TEA). "
            "Suas respostas devem ser:\n"
            "1. Claras, diretas e literais (evite metáforas, ironia ou duplo sentido).\n"
            "2. Empáticas, mas calmas e previsíveis.\n"
            "3. Curtas (máximo 3-4 frases).\n"
            "4. Estruturadas (use listas se necessário).\n"
            "5. Nunca julgue. Valide os sentimentos do usuário.\n"
            "Se o usuário parecer sobrecarregado, sugira pausas ou redução de estímulos."
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Adiciona histórico recente para contexto (opcional)
        if historico:
            messages.extend(historico[-5:])  # Últimas 5 interações

        # Adiciona a mensagem atual
        messages.append({"role": "user", "content": mensagem_usuario})

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Ou "gpt-4o-mini" para melhor custo-benefício
                messages=messages,
                temperature=0.3,  # Baixa temperatura para mais consistência/previsibilidade
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            # Fallback seguro em caso de erro na API
            print(f"Erro na IA: {e}")
            return "Tive dificuldade em processar sua mensagem agora. Vamos tentar de novo?"
