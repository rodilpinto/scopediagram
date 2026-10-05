# Onboard: scopediagram (área `pptx`, cobre o app inteiro)

**Uso**: `/onboard-pptx`

Carrega o contexto do projeto para uma sessão nova. **LÊ e RESUME; não começa trabalho sozinho.**
Este arquivo guarda só procedimento e ponteiros; fatos de estado moram nos arquivos abaixo.

---

## O que fazer
Leia nesta ordem:

1. `docs/SESSION-ONBOARD-pptx.md` inteiro (entry point; §2 estado, §5 próximo movimento).
2. `BLOCKED-ON-RODRIGO.md` (raiz): ações que só o Rodrigo pode fazer.
3. `docs/_TODO.md` (P0/P1) e `docs/_DECISOES-PENDENTES.md` (inclui o eco das decisões do buscador que valem aqui).
4. `LESSONS.md` (raiz): skim.
5. Log recente: `grep -n "^## \[" docs/log.md | head -5` e leia as 2 entradas do topo.
6. Se o state file estiver raso: o snapshot de memória mais recente listado em
   `~/.claude/projects/<pasta-do-projeto>/memory/MEMORY.md`.
7. Git: `git log --oneline -3`, `git status --short -b`, `git branch -a`.

Se a tarefa envolver o LLM: `llm_cadeia/README.md` (a pasta é congelada; ver as decisões).
Se envolver o PPTX: `docs/superpowers/specs/2026-07-02-template-based-ppt-generation-design.md`.

---

## Depois de ler
Resumo curto (≤ 8 linhas): branch + commit atual + working tree; estado (do §2); próximo movimento (do §5);
decisões abertas e ações do `BLOCKED-ON-RODRIGO.md`.

Se a mensagem do usuário já trouxe uma tarefa junto com o onboard, siga com ela depois do resumo.
Senão, pergunte **"Tarefa de hoje?"** e pare.

Não: editar arquivos · commitar · explorar além dos docs acima antes de receber a tarefa.

---

## Verificações rápidas úteis
- Testes: `py -3.13 -m pytest tests -q` e `py -3.13 -m pytest llm_cadeia/test_llm_cadeia.py -q`
  (use o launcher `py`; o `python` do PATH é o atalho da Microsoft Store).
- App local: `py -3.13 -m streamlit run app.py --server.port 8531` (8502 pode estar com o app de Checklist).
- LLM ao vivo (só na rede da Câmara): `py -3.13 -m llm_cadeia` com os segredos de `~/.streamlit/secrets.toml`.
- QA visual fiel do PPTX: `py -3.13 -m pptx_opc.render_powerpoint <arquivo.pptx> <pasta_png>` (PowerPoint real via COM).

## Follow-ups comuns
| Pedido | Ler também | Então |
|---|---|---|
| "vamos fazer o passe do framework" | decisões D-C22/23/24 (eco em `_DECISOES-PENDENTES.md`) | seguir a receita do README do framework; checkpoint |
| "o LLM falhou" | `llm_cadeia/README.md` (esperas, segredos) | diagnosticar; defeito no módulo → pedido ao framework, não editar |
| "corrige overflow das bandas" | `templatefill/igoe.py` | replicar o auto-fit das lanes; render via PowerPoint; checkpoint |
| "o app quebrou" | traceback; `app.py`, `llm.py`, `templatefill/` | `superpowers:systematic-debugging`; checkpoint |
