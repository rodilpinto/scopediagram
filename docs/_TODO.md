---
title: scopediagram TODOs (persistent, version-controlled)
last_audit: 2026-10-05
related: [_DECISOES-PENDENTES.md, log.md, SESSION-ONBOARD-scopediagram.md, ../BLOCKED-ON-RODRIGO.md, ../LESSONS.md]
---

# scopediagram TODOs: o que está pendente e onde

> Companion snapshot: `~/.claude/projects/<pasta-do-projeto>/memory/scopediagram_state_2026-10-06.md` (só nas máquinas do Rodrigo).
> Ações que só o Rodrigo pode fazer: `../BLOCKED-ON-RODRIGO.md` (não duplicadas aqui).

## P0 · Passe do framework (D5/D7): falta só a limpeza
- [x] Tags de volta, linha de base, `homologacao` com `llm_cadeia` 1.1.0, `pptx_opc`, `tempo_economizado`, `branding`
  e dado interno fora dos arquivos versionados (log 05/10).
- [x] D6 e passo do Streamlit (Rodrigo, 06/10): `diagrama-escopo` (`main`) e `diagrama-escopo-homologacao`.
- [x] Conferir no ar, feature por feature: produção igual a antes; homologação com cadeia na barra lateral,
  extração, PPTX baixando e abrindo, tempo economizado, branding.
- [x] Promovido com o ok: `main` = `a4acec5` = `v1.1.0`, nos dois remotos; produção conferida no ar (06/10).
- [x] `main` já é a padrão no GitHub.
- [ ] Com nova confirmação do Rodrigo: apagar `feat/llm-cadeia` nos dois remotos e local (contida na `main`).
- [ ] Rodrigo: trocar a branch padrão do Gitea interno para `main`, na tela (se ainda não for).
- [x] Registro de cópias no nuati-framework (`homologacao` @ `bc24c61`) + F-A14.
- [x] Versão do app no rodapé (`VERSAO_APP`, D7). A cada promoção: trocar `VERSAO_APP` e criar a tag igual.

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
- [ ] Recopiar `branding` e `tempo_economizado` **1.0.1** quando estiverem na `main`/tag do framework (hoje só em
  `homologacao` de lá, `2221d74`, 06/10): só os testes mudaram (pulam sem Streamlit); nenhum efeito neste app.
- [ ] **Rótulo "SUBPROCESSOS" quebrado** no slide 2 (o texto vertical quebra em 3 colunas e passa por cima dos itens):
  visto no render do PowerPoint da linha de base de 05/10, **antes** do passe (defeito antigo, não causado por ele).
- [ ] `app.py` usa `use_container_width` (o Streamlit 1.64 avisa: trocar por `width="stretch"`/`"content"`).
- [ ] Verificar ao vivo a OpenAI paga via "Outro" (hoje só dublê): depende de chave (ver `BLOCKED-ON-RODRIGO.md`);
  resultado vai para o `nuati-framework`.
- [ ] **Auto-fit nas BANDAS** (REGULADORES/RECURSOS/OBJETIVO): hoje só as lanes têm. Reavaliar se aparecer overflow.
- [ ] Refinar o conteúdo LGPD de exemplo (`exemplo_auditoria_lgpd_PROPOSTA-nao-validada.pptx`, proposta não
  validada; **ignorado pelo git** por `.gitignore` `exemplo_*.pptx`, existe só nesta máquina): só se o Rodrigo quiser um deck de demonstração fiel.
