---
title: PPTX TODOs (persistent, version-controlled)
last_audit: 2026-09-28
related: [_DECISOES-PENDENTES.md, log.md]
---

# PPTX TODOs — o que está pendente e onde

## P0 — Bloqueadores / em andamento
- [x] ~~**Antes da reunião (29/09):** Rodrigo confere no Streamlit Cloud que `GEMINI_API_KEY` continua lá e que o app publicado (`main`) gera; se a chave for a nova (nuati.secin), pôr `GEMINI_MODEL = "gemini-3.5-flash-lite"` (a nova recebe 404 em `gemini-2.5-flash`, padrão da `main`). Reboot app.~~ Não se aplica: a versão da reunião é outra (Rodrigo, 28/09); e o merge do llm_cadeia tira o modelo fixo.
- [x] Mergear `feat/llm-cadeia` em `main` (D4 decidida 28/09).
- [ ] Rodrigo: nos Secrets do Cloud, só as chaves gratuitas (sem `LLM_BASE_URL`/`LLM_MODEL`) + Reboot app; testar uma geração no app publicado.
- [ ] Rodrigo: autorizar o push do `master` do buscador (commit 1.0.1 só local; o log de lá pede não empurrar antes da reunião).
- [ ] Verificar ao vivo a OpenAI paga via "Outro" quando houver chave (hoje só dublê).
- [x] Levar à origem (`buscador-normativos`) as observações sobre o `llm_cadeia` (feito: 1.0.1, recopiado) (log 2026-09-28 e D4): Gemma+JSON verificado; "Última resposta" precisa de rerun; OpenAI paga via "Outro" não testada (gpt-5 pode recusar `temperature`/`max_tokens`).

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
- [x] `.streamlit/secrets.toml.example` restaurado e reescrito com os nomes do `llm_cadeia` (2026-09-28, branch `feat/llm-cadeia`).
- [ ] Merge da branch `feature/smartart-data-model-editability` em `main` — aguardando o usuário validar a editabilidade no PowerPoint (item acima) antes de decidir se mergeia.
