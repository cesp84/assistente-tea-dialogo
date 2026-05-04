# 🧠 Assistente TEA — Comunicação Estruturada e Apoio Cognitivo

Assistente conversacional adaptado para pessoas com Transtorno do Espectro Autista (TEA), focado em comunicação clara, previsível e estruturada.

O projeto propõe uma abordagem baseada em regras de diálogo e fluxos guiados, com o objetivo de reduzir ambiguidade, organizar pensamentos e apoiar situações de sobrecarga e execução de tarefas.

---

## 🎯 Objetivo

Criar uma ferramenta simples, segura e útil para:

* Apoiar comunicação com linguagem direta e sem ambiguidade
* Reduzir sobrecarga cognitiva em interações
* Auxiliar na organização de tarefas em etapas pequenas
* Oferecer suporte em momentos de ansiedade ou desregulação

---

## ⚠️ Escopo e Limitações

Este projeto:

* ❌ Não realiza diagnóstico
* ❌ Não substitui acompanhamento profissional
* ❌ Não utiliza dados sensíveis sem consentimento

O foco é **apoio e organização**, não intervenção clínica.

---

## 🧩 Abordagem

Diferente de chats genéricos, este sistema utiliza:

* Respostas estruturadas (passo a passo)
* Linguagem literal e objetiva
* Fluxos guiados por contexto
* Modos de interação (ex: conversa, tarefas, sobrecarga)

---

## 🏗️ Arquitetura Inicial

```text
Usuário
   ↓
Interface (Chat + Botões)
   ↓
View Django
   ↓
DialogoService (regras de conversa)
   ↓
Resposta estruturada
```

---

## ⚙️ Tecnologias

* Python
* Django
* HTML / JavaScript
* Arquitetura baseada em serviços (services layer)

---

## 🚀 MVP (Versão Inicial)

Funcionalidades previstas:

* Chat com resposta estruturada
* 3 modos principais:

  * Conversa simples
  * Apoio em sobrecarga
  * Organização de tarefas
* Regras de diálogo (sem IA no início)

---

## 🔮 Roadmap

### Fase 1 — MVP

* [ ] Estrutura Django
* [ ] DialogoService com regras básicas
* [ ] Interface simples

### Fase 2 — Evolução

* [ ] Personalização de comunicação
* [ ] Persistência de preferências
* [ ] Melhoria de UX

### Fase 3 — IA Controlada

* [ ] Integração com IA
* [ ] Prompt estruturado
* [ ] Camada de segurança e validação

---

## 🔐 Ética e Segurança

* Comunicação clara e não ambígua
* Evitar sobrecarga de informação
* Respeito à privacidade
* Controle do comportamento da IA (quando houver)

---

## 📁 Estrutura do Projeto

```text
assistente_tea/
├── views.py
├── services/
│   └── dialogo_service.py
├── templates/
├── static/
```

---

## 🤝 Contribuição

Contribuições são bem-vindas, especialmente em:

* UX para acessibilidade
* Estruturação de fluxos de diálogo
* Boas práticas em sistemas inclusivos

---

## 📌 Status

🚧 Em desenvolvimento inicial (MVP)

---

## 📄 Licença

MIT License
