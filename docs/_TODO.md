---
title: PPTX TODOs (persistent, version-controlled)
last_audit: 2026-10-05
related: [_DECISOES-PENDENTES.md, log.md, SESSION-ONBOARD-pptx.md, ../BLOCKED-ON-RODRIGO.md, ../LESSONS.md]
---

# PPTX TODOs: o que está pendente e onde

> Companion snapshot: `~/.claude/projects/<pasta-do-projeto>/memory/pptx_state_2026-09-29.md`.
> Ações que só o Rodrigo pode fazer: `../BLOCKED-ON-RODRIGO.md` (não duplicadas aqui).

## P0 · Passe do framework (D5): falta o Streamlit e a conferência no ar
- [x] Tags de volta, linha de base, `homologacao` com `llm_cadeia` 1.1.0, `pptx_opc`, `tempo_economizado`, `branding`
  e dado interno fora dos arquivos versionados (log 05/10).
- [x] D6 e passo do Streamlit (Rodrigo, 06/10): `diagrama-escopo` (`main`) e `diagrama-escopo-homologacao`.
- [x] Conferir no ar, feature por feature: produção igual a antes; homologação com cadeia na barra lateral,
  extração, PPTX baixando e abrindo, tempo economizado, branding.
- [ ] Com o ok: promover `homologacao` → `main` (fast-forward) com tag de versão do app; push nos dois remotos.
- [ ] Com novo ok: `main` padrão no GitHub; apagar `feat/llm-cadeia` (e apps de teste antigos, se houver).
- [ ] Registro de cópias no nuati-framework (README §4, linhas do scopediagram).
- [ ] Rodapé "Versão 1.0" fixo em `app.py`: passar a vir da tag de versão do app (na promoção).

## P1 · Concluído recentemente
- [x] Adotar o `llm_cadeia` (Gemini/OpenAI diretos → `gerar`), verificado ao vivo na rede da Câmara (Gemma local,
  JSON, extração IGOE, app com "Última resposta") · `bc75099`, merge na `main` `0b5aee1` (D4).
- [x] Achados do módulo corrigidos na origem (1.0.1: gancho `ao_responder`, repetição `max_completion_tokens`,
  docstrings); integrados no buscador `7f1c069`; cópia daqui idêntica, procedência atualizada · `7a2c6ba`, `b972665`.
- [x] `.streamlit/secrets.toml.example` restaurado e reescrito com os nomes do `llm_cadeia` · `bc75099`.
- [x] Tag de retorno `pre-llm-cadeia` (= `6083a90`) nas duas remotes.
- [x] Reconstrução do modelo de dados do SmartArt (D3) mergeada em `main` · `6083a90`; validada no PowerPoint
  real via COM em 2026-07-13.
- [x] Motor `templatefill/` (OPC, IGOE, orquestrador), auto-fit das lanes, testes de fumaça, prévia não-fatal ·
  `f2e55aa`, `55d87ea`, `2b912ea`, `5e9d1b7`; merge em `main` 2026-07-08 (D1/D2).

## P2 / P3 · Depois / nice-to-have
- [ ] **Rótulo "SUBPROCESSOS" quebrado** no slide 2 (o texto vertical quebra em 3 colunas e passa por cima dos itens):
  visto no render do PowerPoint da linha de base de 05/10, **antes** do passe (defeito antigo, não causado por ele).
- [ ] `app.py` usa `use_container_width` (o Streamlit 1.64 avisa: trocar por `width="stretch"`/`"content"`).
- [ ] Verificar ao vivo a OpenAI paga via "Outro" (hoje só dublê): depende de chave (ver `BLOCKED-ON-RODRIGO.md`);
  resultado vai para a sessão do framework (D-C24).
- [ ] **Auto-fit nas BANDAS** (REGULADORES/RECURSOS/OBJETIVO): hoje só as lanes têm. Reavaliar se aparecer overflow.
- [ ] Refinar o conteúdo LGPD de exemplo (`exemplo_auditoria_lgpd_PROPOSTA-nao-validada.pptx`, proposta não
  validada; **ignorado pelo git** por `.gitignore` `exemplo_*.pptx`, existe só nesta máquina): só se o Rodrigo quiser um deck de demonstração fiel.
