# Onboard — PPTX (geração do PowerPoint)

**Uso**: `/onboard-pptx`

Carrega o contexto da área de geração do PPTX (estado atual, decisões, pendências)
para uma sessão nova começar pronta. **LÊ e RESUME — não começa trabalho sozinho.**

---

## O que fazer
Leia estes arquivos nesta ordem e resuma o estado ao usuário. **NÃO comece a
trabalhar até o usuário dar uma tarefa.**

### Passo 1 — Snapshot de estado (entry point, ≤ 1 página)
`docs/SESSION-ONBOARD-pptx.md` — leia inteiro; §2 (feito) e §5 (próximo) são a fonte da verdade.

### Passo 2 — Ledgers
`docs/_TODO.md` (P0/P1) e `docs/_DECISOES-PENDENTES.md` (decisões 🔴/🟡 abertas + o que cada uma bloqueia).

### Passo 3 — Spec / arquitetura (se necessário)
`docs/superpowers/specs/2026-07-02-template-based-ppt-generation-design.md` — a abordagem e as suposições verificadas.

### Passo 4 — Snapshot de memória (se o state file estiver raso)
`~/.claude/projects/C--Users-P-8106-Documents-solucoes-scopediagram/memory/pptx_state_2026-07-07.md`.

### Passo 5 — Log recente (skim)
`grep -n "^## \[" docs/log.md | head -10`, leia as 2-3 entradas do topo.

---

## Depois de ler
Responda um resumo curto (≤ 8 linhas):
1. Commit atual (`git log --oneline -1`) + status do working tree + branch (`feature/template-ppt-generation`).
2. Último chunk concluído + saídas-chave (pacote `templatefill/`, 5 slides limpos).
3. Próximo movimento (do §5): reagir ao teste ao vivo do usuário.
4. Decisões abertas pendentes do usuário (D1/D2/D3 em `docs/_DECISOES-PENDENTES.md`).

Depois pergunte: **"Tarefa de hoje?"**

Não: editar arquivos · começar trabalho · commitar · explorar além dos docs acima. Aguarde a tarefa.

---

## Verificações rápidas úteis
- App ao vivo: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8501` (server em background pode não estar mais de pé numa sessão nova).
- Regenerar deck de teste: rodar `tests/test_generation.py` (só precisa de `lxml` + `pydantic`).
- Render p/ QA: `soffice.exe --headless --convert-to pdf` → PyMuPDF (`fitz`) → PNG (poppler/`dot` não instalados).

## Follow-ups comuns
| Pedido | Ler também | Então |
|---|---|---|
| "corrige overflow das bandas" | `templatefill/igoe.py` (`_lane_font_fit`, `fill_igoe_slide`) | replicar auto-fit p/ as caixas de banda; render p/ conferir; checkpoint |
| "mergea em main" | `docs/_DECISOES-PENDENTES.md` D2 | `superpowers:finishing-a-development-branch`; checkpoint |
| "o app quebrou" | traceback do usuário; `app.py`; `templatefill/` | `superpowers:systematic-debugging`; checkpoint |
