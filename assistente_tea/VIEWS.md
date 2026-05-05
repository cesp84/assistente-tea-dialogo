# Documentacao das Views de Assistente TEA

Arquivo de referencia: `assistente_tea/views.py`.

## Visao Geral

O app `assistente_tea` concentra a tela principal de conversa e os endpoints Django usados pelo frontend.

Responsabilidades atuais das views:

- renderizar a tela inicial do chat;
- inicializar contexto e historico de sessao;
- receber mensagens via `POST`;
- orquestrar chamada ao `DialogoService`;
- persistir interacoes no banco;
- retornar resposta JSON para o frontend;
- reiniciar conversa por rota dedicada.

## Convencoes Esperadas

- Views devem atuar como camada web/controller.
- Regras de conversa devem ficar em `services/dialogo_service.py`.
- Integracao com IA deve ficar em `services/ia_service.py`.
- Busca de historico deve ficar em `services/historico_service.py`.
- Templates devem evitar JavaScript inline.
- Frontend deve consumir endpoints Django, nao APIs externas diretamente.

## Views Atuais

### `chat(request)`

Rota:

- `/assistente_tea/`

Responsabilidade:

- renderizar `assistente_tea/chat.html`;
- garantir que a sessao possua:
  - `dialogo_contexto`;
  - `dialogo_historico`.

Comportamento atual:

- usa `request.session.setdefault(...)`;
- retorna a tela principal do chat.

### `enviar_mensagem(request)`

Rota:

- `/assistente_tea/enviar/`

Metodo:

- `POST`

Responsabilidade:

- ler `mensagem` do formulario;
- ler `modo`, usando `auto` como fallback;
- obter contexto da sessao;
- obter histórico recente da sessão;
- chamar `DialogoService.responder(...)`;
- atualizar contexto e historico de sessao;
- gravar `Interacao`;
- retornar JSON com:
  - `resposta`;
  - `contexto`.

Payload recebido atualmente:

```text
mensagem=<texto>
modo=<modo opcional>
csrfmiddlewaretoken=<token>
```

Observacao:

- O template atual nao envia campo `modo`; portanto, a view usa `auto`.

### `nova_conversa(request)`

Rota:

- `/assistente_tea/nova-conversa/`

Responsabilidade:

- limpar `dialogo_contexto`;
- limpar `dialogo_historico`;
- redirecionar para a tela do chat.

## Pontos de Atencao

### Historico

`enviar_mensagem` usa o histórico armazenado na sessão por meio de `dialogo_historico`.

Comportamento atual:

- o histórico da conversa é lido de `request.session`;
- após cada interação, a mensagem do usuário e a resposta do sistema são adicionadas ao histórico;
- a sessão mantém apenas as últimas mensagens;
- o banco continua sendo usado para persistir `Interacao`, mas não para alimentar diretamente o contexto do diálogo.

Impacto:

- reduz risco de mistura de contexto entre usuários;
- mantém o fluxo simples para o estágio atual do projeto;
- ainda permite evolução futura para histórico por usuário ou por conversa.

Observação:

- `HistoricoService` não é necessário no fluxo atual da view;
- pode ser mantido para uso futuro administrativo ou removido se não houver previsão de uso.

### Persistencia

A view cria uma `Interacao` a cada envio.

Campos gravados:

- `mensagem_usuario`;
- `resposta_sistema`;
- `modo`;
- `criado_em`.

Cuidados:

- nao persistir dados sensiveis sem avaliacao;
- considerar politica de retencao se o projeto evoluir.

### Tratamento de erro

Atualmente a view nao possui bloco proprio de tratamento de erro para falhas inesperadas.

Recomendacao:

- se o fluxo crescer, centralizar erro real de service/API e retornar JSON previsivel;
- preservar logs objetivos sem expor dados sensiveis.

## Relacao com Frontend

Template:

- `assistente_tea/templates/assistente_tea/chat.html`

JavaScript:

- `assistente_tea/static/assistente_tea/js/chat.js`

CSS:

- `assistente_tea/static/assistente_tea/css/chat.css`

Comportamento atual do JS:

- intercepta submit do formulario;
- envia `fetch` para `/assistente_tea/enviar/`;
- envia `X-CSRFToken`;
- exibe estado `Processando...`;
- mostra resposta em `#resposta`;
- limpa e refoca o textarea.

## Boas Praticas para Evolucao

- Manter views finas.
- Mover regra de fluxo para services.
- Criar normalizers/adapters se a resposta para UI crescer.
- Evitar `onclick`, `onchange` e JavaScript inline no template.
- Se houver modos visuais, expor controles acessiveis no template e manter validacao na view.
- Retornar JSON consistente em sucesso e erro.
