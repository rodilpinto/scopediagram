---
title: PPTX TODOs (persistent, version-controlled)
last_audit: 2026-07-07
related: [_DECISOES-PENDENTES.md, log.md, ../../.claude/projects/C--Users-P-8106-Documents-solucoes-scopediagram/memory/pptx_state_2026-07-07.md]
---

# PPTX TODOs — o que está pendente e onde

> Snapshot companheiro: `~/.claude/projects/C--Users-P-8106-Documents-solucoes-scopediagram/memory/pptx_state_2026-07-07.md`.

## P0 — Bloqueadores / em andamento
- [/] Teste do app ao vivo pelo usuário — conferir extração por campo + qualidade do PPTX baixado. **App foi encerrado (limite de sessão); relançar antes:** `python -m streamlit run app.py --server.headless true --server.port 8501`. Aguardando retorno; corrigir o que aparecer.

## P1 — Trabalho ativo
- [x] Motor OPC `templatefill/opc.py` (delete/clone de slides + partes SmartArt) — `f2e55aa`.
- [x] Preenchimento IGOE `templatefill/igoe.py` (título, bandas, eventos, lanes) — `f2e55aa`.
- [x] Orquestrador `templatefill/builder.py` + shim `ppt.py` + `ppt_legacy.py` — `f2e55aa`.
- [x] Auto-fit de fonte nas lanes + z-order dos eventos — `55d87ea`.
- [x] Testes de fumaça + `lxml` no requirements — `2b912ea`.
- [x] Pré-visualização não-fatal (Graphviz opcional) — `5e9d1b7`.
- [ ] **Auto-fit nas BANDAS** (REGULADORES/RECURSOS/OBJETIVO) — hoje só as lanes têm auto-fit; listas longas nessas bandas podem transbordar. Fazer se o teste do usuário mostrar overflow.
- [ ] Reagir ao retorno do teste ao vivo (tracebacks / campos errados / overflow).

## P2 / P3 — Depois / nice-to-have
- [ ] Merge da branch `feature/template-ppt-generation` em `main` (+ PR) — ver `superpowers:finishing-a-development-branch`.
- [ ] Melhorar sync do modelo de dados do SmartArt (`_sync_data_text` é best-effort; editar o SmartArt no PowerPoint pode reexibir texto do template). Só se editabilidade pós-abertura virar requisito.
- [ ] Refinar o conteúdo LGPD de exemplo (era proposta minha, não validada) — só se o usuário quiser um deck de demonstração fiel; o objetivo real da sessão era o PPTX, não o conteúdo.
- [ ] Limpeza: decidir sobre `D .streamlit/secrets.toml.example` (deleção no working tree, não desta sessão).
