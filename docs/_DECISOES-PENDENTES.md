---
title: "Decisões abertas — ledger consolidado (PPTX)"
maintained_by: Claude Code sessions; só Rodrigo resolve
last_updated: 2026-07-07
related: [_TODO.md, SESSION-ONBOARD-pptx.md, log.md]
---

# Decisões abertas — o que precisa da chamada do humano

> `_TODO.md` é o ledger de TAREFAS; este é o de DECISÕES. Status: 🔴 OPEN · 🟡 EM ANÁLISE · 🟢 DECIDIDA.
> Sugestões aqui são propostas, não fatos validados.

## D1 — Resultado do teste ao vivo do app define os próximos ajustes
- **Status:** 🔴 OPEN (aguardando o teste do usuário)
- **Tipo:** validação / direção
- **Onde aparece:** app em http://localhost:8501; PPTX baixado

**A questão.** O usuário está testando o app com conteúdo real. O que ele reportar
(campos extraídos corretos? algum overflow? traceback?) decide o próximo trabalho.

**Tarefas bloqueadas por D1:**
- Estender (ou não) o auto-fit às bandas.
- Qualquer correção de mapeamento de campo ou render.

**Decisão tomada:** _(pendente)_

---

## D2 — Mergear a branch `feature/template-ppt-generation` em `main`?
- **Status:** 🔴 OPEN
- **Tipo:** git / release
- **Onde aparece:** repositório; deploy no Streamlit Cloud

**A questão.** A nova geração vive numa branch. Quando o usuário validar o app,
mergear em `main` (a `main` é o que o Streamlit Cloud faz deploy).

**Opções & trade-offs (📝 análise minha):**

| Opção | Ganha | Perde / risco |
|---|---|---|
| A. Merge direto em `main` | simples; deploy imediato | sem revisão formal |
| B. Abrir PR e revisar | rastreabilidade, code review | mais passos |

**Recomendação (📝 sugestão):** B — abrir PR após o usuário validar o app ao vivo.

**Tarefas bloqueadas por D2:** merge/PR no `_TODO.md` (P2).

**Decisão tomada:** _(pendente)_

---

## D3 — Precisamos de editabilidade fiel do SmartArt no PowerPoint?
- **Status:** 🟡 EM ANÁLISE
- **Tipo:** arquitetura
- **Onde aparece:** `templatefill/igoe.py::_sync_data_text`

**A questão.** O render usa o desenho em cache (correto). Mas o **modelo de dados**
do SmartArt só é sincronizado best-effort. Se o usuário **editar** o SmartArt dentro
do PowerPoint, o layout pode regenerar a partir do modelo de dados e reexibir texto
do template. Vale investir em reconstruir o modelo de dados?

**Opções & trade-offs (📝 análise minha):**

| Opção | Ganha | Perde / risco |
|---|---|---|
| A. Deixar como está (best-effort) | simples; deck abre perfeito | edição do SmartArt no PPT pode bagunçar |
| B. Reconstruir nós do modelo de dados | editável e consistente | esforço alto, XML frágil |

**Recomendação (📝 sugestão):** A, salvo o usuário exigir editar o SmartArt pós-entrega.

**Tarefas bloqueadas por D3:** item P3 de sync no `_TODO.md`.

**Decisão tomada:** _(pendente)_
