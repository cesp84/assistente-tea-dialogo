# Documentacao dos Services de Integracao

Arquivos de referencia:

- `assistente_tea/services/ia_service.py`
- `assistente_tea/services/historico_service.py`
- `assistente_tea/services/dialogo_service.py`

## Visao Geral

Este projeto ainda nao possui um `api_client.py` dedicado.

A integracao externa atual fica em `IAService`, que chama a API Gemini diretamente via `requests`.

Como referencia arquitetural do projeto:

- service/client de API deve cuidar de transporte, endpoint, timeout e contrato bruto;
- normalizacao para UI nao deve ficar no client;
- regra de negocio/conversa deve ficar em service de dominio, hoje `DialogoService`.

## `IAService`

Arquivo:

- `assistente_tea/services/ia_service.py`

Responsabilidade atual:

- carregar `GEMINI_API_KEY` a partir de `settings`;
- montar URL do Gemini;
- montar prompt seguro;
- enviar payload para API;
- tratar erro HTTP, timeout, erro de conexao e erro inesperado;
- retornar texto final para o `DialogoService`.

Modelo atual:

- `gemini-2.5-flash`

Endpoint atual:

```text
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=<GEMINI_API_KEY>
```

Payload atual:

```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "<prompt>"
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.3,
    "maxOutputTokens": 180
  }
}
```

Contrato de resposta assumido:

```text
data["candidates"][0]["content"]["parts"][0]["text"]
```

Cuidados:

- validar contrato real se a API mudar;
- nao expor chave em logs;
- evitar `print` em service;
- priorizar `logger` quando houver informacao operacional util.

## Prompt Atual

O prompt instrui a IA a:

- atuar como assistente de apoio comunicacional para pessoas com TEA;
- usar historico recente apenas para contexto;
- nao alegar memoria permanente;
- nao diagnosticar;
- nao substituir profissional de saude;
- responder em portugues do Brasil;
- usar linguagem clara, direta e literal;
- usar frases curtas;
- evitar metaforas, ironias e duplo sentido;
- reduzir informacao se houver sobrecarga;
- responder com no maximo 4 frases ou lista curta.

## Tratamento de Erros

Comportamento atual:

- status HTTP diferente de `200`:
  - registra `logger.warning`;
  - retorna fallback simples.
- timeout:
  - registra `logger.warning`;
  - retorna mensagem de demora.
- erro de conexao:
  - registra `logger.error` com `exc_info=True`;
  - retorna mensagem de indisponibilidade.
- erro inesperado:
  - registra `logger.error` com `exc_info=True`;
  - retorna mensagem pedindo tentativa com mensagem mais curta.

Recomendacao:

- manter mensagens simples e seguras;
- preservar informacao tecnica em logs, sem dados sensiveis;
- quando houver body de erro da API, priorizar mensagem real se ela for segura para o usuario.

## `HistoricoService`

Arquivo:

- `assistente_tea/services/historico_service.py`

Responsabilidade atual:

- buscar as ultimas interacoes no modelo `Interacao`;
- montar lista no formato:

```json
[
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."}
]
```

Limite atual:

- `LIMITE_INTERACOES = 6`

Ponto de atencao:

- a busca atual nao filtra por usuario, sessao ou conversa;
- em ambiente multiusuario, isso pode misturar historicos.

## `DialogoService`

Arquivo:

- `assistente_tea/services/dialogo_service.py`

Responsabilidade atual:

- normalizar texto;
- identificar saudacoes e comandos globais;
- identificar fluxo por modo ou palavras-chave;
- conduzir fluxos guiados;
- chamar `IAService` quando o fluxo for simples;
- retornar dicionario com:
  - `resposta`;
  - `contexto`.

Fluxos atuais:

- `sobrecarga`;
- `tarefas`;
- `comunicacao`;
- `simples`.

Cuidados:

- manter linguagem simples;
- evitar orientacao clinica;
- nao aumentar sobrecarga cognitiva;
- preservar previsibilidade dos fluxos.

## Boas Praticas para Evolucao

- Se novas APIs externas forem adicionadas, criar client/service proprio.
- Manter API client fino: endpoint, metodo, payload bruto e erro tecnico.
- Criar normalizers/adapters para adaptar payloads antes de chegar na UI.
- Nao colocar regra de exibicao dentro de client externo.
- Nao assumir persistencia apenas porque um campo existe no input.
- Validar contrato real da API antes de consolidar comportamento.
