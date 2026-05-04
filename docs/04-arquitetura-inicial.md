# 🏗️ Arquitetura Inicial

## Objetivo

Definir a arquitetura inicial do Assistente TEA, mantendo o projeto simples, modular, seguro e fácil de evoluir.

---

## Visão Geral

```text
Usuário
   ↓
Interface Web
   ↓
View Django
   ↓
DialogoService
   ↓
Regras de diálogo
   ↓
Resposta estruturada
```

---

## Camadas

### 1. Interface

Responsável por exibir o chat, botões de contexto e respostas estruturadas.

### 2. View Django

Responsável por receber a requisição, validar dados básicos e chamar a camada de serviço.

### 3. Services

Responsável pela regra de diálogo e organização da resposta.

### 4. Templates

Responsáveis pela apresentação visual da aplicação.

### 5. Static

Responsável por JavaScript, CSS e recursos visuais.

---

## Estrutura Inicial

```text
assistente_tea/
├── views.py
├── urls.py
├── services/
│   ├── dialogo_service.py
│   └── seguranca_service.py
├── templates/
│   └── assistente_tea/
│       └── chat.html
└── static/
    └── assistente_tea/
        └── chat.js
```

---

## Princípios Técnicos

* Manter views simples
* Centralizar regras em services
* Evitar lógica de negócio no template
* Separar comunicação, segurança e apresentação
* Começar sem IA generativa
* Evoluir com baixo acoplamento

---

## Fluxo Inicial

1. Usuário envia mensagem
2. Interface envia requisição para Django
3. View valida mensagem e modo
4. DialogoService identifica o contexto
5. Sistema retorna resposta clara e estruturada

---

## Evolução Prevista

### Fase 1

* Regras fixas de diálogo
* Modos simples de interação
* Interface básica

### Fase 2

* Perfil de comunicação do usuário
* Preferências de resposta
* Persistência local controlada

### Fase 3

* Integração com IA
* Prompt controlado
* Camada de segurança antes e depois da resposta

---

## Decisão Arquitetural Inicial

A primeira versão será baseada em regras, não em IA generativa.

Essa decisão reduz riscos, facilita validação e permite entender melhor os fluxos reais antes de adicionar inteligência artificial.
