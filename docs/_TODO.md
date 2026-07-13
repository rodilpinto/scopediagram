---
title: PPTX TODOs (persistent, version-controlled)
last_audit: 2026-07-09
related: [_DECISOES-PENDENTES.md, log.md]
---

# PPTX TODOs — o que está pendente e onde

## P0 — Bloqueadores / em andamento
Nenhum no momento.

## P1 — Trabalho ativo / concluído recentemente
- [x] Motor OPC `templatefill/opc.py` (delete/clone de slides + partes SmartArt) — `f2e55aa`.
- [x] Preenchimento IGOE `templatefill/igoe.py` (título, bandas, eventos, lanes) — `f2e55aa`.
- [x] Orquestrador `templatefill/builder.py` + shim `ppt.py` + `ppt_legacy.py` — `f2e55aa`.
- [x] Auto-fit de fonte nas lanes + z-order dos eventos — `55d87ea`.
- [x] Testes de fumaça + `lxml` no requirements — `2b912ea`.
- [x] Pré-visualização não-fatal (Graphviz opcional) — `5e9d1b7`.
- [x] Teste do app ao vivo pelo usuário — funcionou bem, sem overflow/traceback (D1 decidida).
- [x] Merge da branch `feature/template-ppt-generation` em `main` + deploy — feito 2026-07-08, push nos dois remotes (D2 decidida).
- [x] Reconstrução do modelo de dados do SmartArt para editabilidade pós-geração no PowerPoint (D3 decidida e implementada) — `_find_lane_roots`/`_rebuild_lane_nodes`/`_sync_data_nodes` em `templatefill/igoe.py`, substituindo `_sync_data_text`. Branch `feature/smartart-data-model-editability`, spec+plano em `docs/superpowers/specs/` e `docs/superpowers/plans/`.

## P2 / P3 — Depois / nice-to-have
- [ ] **Auto-fit nas BANDAS** (REGULADORES/RECURSOS/OBJETIVO) — hoje só as lanes têm auto-fit. Não necessário até agora (D1: sem relato de overflow), reavaliar se aparecer em uso real.
- [ ] Validação manual do usuário: abrir o `.pptx` gerado (pós-D3) no PowerPoint de verdade, editar um item de lane no SmartArt, confirmar que não reverte para texto do template. **Não testável nesta máquina** (sem PowerPoint; LibreOffice não recalcula SmartArt a partir do modelo de dados).
- [ ] Refinar o conteúdo LGPD de exemplo (era proposta minha, não validada) — só se o usuário quiser um deck de demonstração fiel; o objetivo real da sessão era o PPTX, não o conteúdo.
- [ ] Limpeza: decidir sobre `D .streamlit/secrets.toml.example` (deleção no working tree, não desta sessão) — ainda pendente, não tocado.
- [ ] Merge da branch `feature/smartart-data-model-editability` em `main` — aguardando o usuário validar a editabilidade no PowerPoint (item acima) antes de decidir se mergeia.
