---
title: PPTX TODOs (persistent, version-controlled)
last_audit: 2026-09-29
related: [_DECISOES-PENDENTES.md, log.md, SESSION-ONBOARD-pptx.md, ../BLOCKED-ON-RODRIGO.md, ../LESSONS.md]
---

# PPTX TODOs: o que está pendente e onde

> Companion snapshot: `~/.claude/projects/C--Users-P-8106-Documents-solucoes-scopediagram/memory/pptx_state_2026-09-29.md`.
> Ações que só o Rodrigo pode fazer: `../BLOCKED-ON-RODRIGO.md` (não duplicadas aqui).

## P0 · Em pausa: passe do framework (D-C22/D-C23/D-C24, eco em `_DECISOES-PENDENTES.md`)
- [ ] **Aguardar o passe único deste app** vindo da sessão do framework (`rodilpinto/nuati-framework`): adotar o
  framework **e** migrar para `main` (produção) / `homologacao` (playground), recriando os apps no Streamlit.
  Até lá: não criar/renomear branches, não recriar apps, não editar `llm_cadeia/`, não fazer push na `main`.
- [ ] No passe: levar o commit de trabalho pendente (`feat/llm-cadeia`, 2 commits só de docs à frente da `main`)
  para a branch certa, e apagar `feat/llm-cadeia` só depois dos apps novos conferidos no ar (ordem da D-C22).
- [ ] Pedido à sessão do framework (D-C24): o README do `llm_cadeia` cita uma spec que só existe no buscador;
  na cópia, apontar o repo de origem (achado do dogfood de 29/09).
- [ ] No passe: rodapé "Versão 1.0" fixo em `app.py` (`_render_efficiency_footer`) passa a vir da tag/framework.

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
- [ ] Verificar ao vivo a OpenAI paga via "Outro" (hoje só dublê): depende de chave (ver `BLOCKED-ON-RODRIGO.md`);
  resultado vai para a sessão do framework (D-C24).
- [ ] **Auto-fit nas BANDAS** (REGULADORES/RECURSOS/OBJETIVO): hoje só as lanes têm. Reavaliar se aparecer overflow.
- [ ] Refinar o conteúdo LGPD de exemplo (`exemplo_auditoria_lgpd_PROPOSTA-nao-validada.pptx`, proposta não
  validada; **ignorado pelo git** por `.gitignore` `exemplo_*.pptx`, existe só nesta máquina): só se o Rodrigo quiser um deck de demonstração fiel.
