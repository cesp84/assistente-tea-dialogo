## Camadas

### 1. Interface

Responsável por:

- exibir o chat;
- apresentar respostas de forma clara e previsível;
- evitar sobrecarga visual;
- enviar mensagens via requisição HTTP (AJAX).

### 2. View Django

Responsável por:

- receber a requisição do usuário;
- validar dados básicos (mensagem, modo, etc.);
- controlar fluxo da requisição;
- chamar os services;
- retornar resposta HTTP (JSON ou renderização).

**Regra importante:**  
A view não deve conter lógica de negócio complexa.

### 3. Services

Responsáveis pela lógica do sistema.

#### `DialogoService`

- identifica intenção do usuário;
- controla fluxo de diálogo;
- executa regras fixas;
- decide quando usar IA;
- aplica fallback seguro.

#### `IAService`

- monta o prompt;
- chama a API externa (Gemini);
- trata erros de comunicação (timeout, HTTP, etc.);
- retorna resposta controlada.

#### `HistoricoService`

- recupera histórico recente;
- prepara contexto para o diálogo.

### 4. Templates

Responsáveis pela apresentação visual:

- `chat.html` como interface principal;
- estrutura simples, acessível e previsível.

### 5. Static

Responsável por:

- JavaScript (envio de mensagens, UX);
- CSS (layout simples e acessível).

---

## Estrutura Atual

```text
assistente_tea/
├── views.py
├── urls.py
├── models.py
├── services/
│   ├── dialogo_service.py
│   ├── ia_service.py
│   ├── historico_service.py
│   └── API_CLIENT.md
├── templates/
│   └── assistente_tea/
│       └── chat.html
├── static/
│   └── assistente_tea/
│       ├── js/
│       │   └── chat.js
│       └── css/
│           └── chat.css
└── VIEWS.md