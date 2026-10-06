---
title: scopediagram (PPTX + LLM) · session onboarding / state snapshot
maintained_by: Claude Code sessions; humans can edit too
last_updated: 2026-10-06
related: [_TODO.md, _DECISOES-PENDENTES.md, log.md, ../BLOCKED-ON-RODRIGO.md, ../LESSONS.md]
---

# scopediagram: session onboarding

Ponto de entrada único (área `scopediagram`, que cobre o app inteiro; chamava-se `pptx` até 06/10). ≤ 1 página.
Histórico em `log.md`; tarefas em `_TODO.md`; decisões em `_DECISOES-PENDENTES.md`; ações só-humano em `../BLOCKED-ON-RODRIGO.md`; lições em
`../LESSONS.md`.

## 1. O que é (30s)
App Streamlit (`app.py`): extrai um modelo IGOE de texto via LLM (`llm.py` → `ScopeDiagram` em `schema.py`) e gera
o PowerPoint **preenchendo o template real (SmartArt)**, pacote `templatefill/`. O LLM passa pelo módulo
compartilhado `llm_cadeia/` (cadeia local Gemma → Gemini → Groq → Cerebras → OpenRouter). Remotes: `github`
(github.com/rodilpinto/scopediagram) e `origin` (remoto interno; URL em `git remote -v`).

## 2. Estado na última pausa (2026-10-06)
**Passe do nuati-framework concluído** (D5/D7; log 05-06/10), falta só a limpeza (apagar `feat/llm-cadeia`).
- **`main` = `a4acec5` = tag `v1.1.0`** (produção, `diagrama-escopo.streamlit.app`), com `llm_cadeia` 1.1.0,
  `pptx_opc` 1.0.0, `tempo_economizado` 1.0.0 e `branding` 1.0.0 (pastas com a árvore git idêntica à do framework
  v0.1.0) e "Versão 1.1.0" no rodapé. Conferida no ar em 06/10.
- **`homologacao`** (trabalho do dia a dia, `diagrama-escopo-homologacao.streamlit.app`): igual à `main` mais commits
  de journal. A URL antiga `diagramadeescopo.streamlit.app` não existe mais.
- **Promover** (só com ok do Rodrigo): (1) em `homologacao`, trocar `VERSAO_APP` em `app.py`, testar, commit e push
  nos dois remotos; (2) conferir o app de homologação no ar (rodapé com a versão nova, uma geração); (3)
  `git switch main && git merge --ff-only homologacao`; (4) `git tag -a vX.Y.Z -m "vX.Y.Z: <o que mudou>"`;
  (5) `git push github main vX.Y.Z` e `git push origin main vX.Y.Z`, conferir com `git ls-remote`; (6) conferir a
  produção no ar; (7) `git switch homologacao`. Exemplo real: entrada de 06/10 do `log.md` (v1.1.0).
- **Retorno:** tags anotadas `pre-framework-2026-10-05-main` e `pre-framework-2026-10-05-feat-llm-cadeia`; voltar a
  `main` por `git revert`, nunca por push forçado.
- **Working tree:** arquivos não rastreados do usuário (2 `.pptx` na raiz e `.claude/settings.local.json`), intocados.
- **Cadeia desta sessão (05-06/10, em `homologacao`):** `de34e02` (merge) → `28386b1` → `514d71c` → `22ee8e5` →
  `e4278bc` → `67beb1b` → `a4acec5` (= `main` = `v1.1.0`) → commits de journal e o do checkpoint. ⚠ O SHA mais novo
  listado aqui está sempre um ou mais atrás dos commits que gravaram este arquivo: a cadeia real termina em
  `git log --oneline -3`.

## 3. Achados críticos (não perder)
- Pastas do framework (`llm_cadeia/`, `pptx_opc/`, `tempo_economizado/`, `branding/`): não editar; defeito vira
  pedido ao `nuati-framework`. Recopiar o recurso X da ref R: comparar a cópia por hash git com a versão que ela diz
  ter; `git -C ../nuati-framework fetch -q origin --tags`; `git rm -r -q X && git -C ../nuati-framework archive R X | tar -x -f - && git add X`; conferir
  `git rev-parse HEAD:X` contra `git -C ../nuati-framework rev-parse R:X` depois do commit; testes; commit
  "adota X <versão> (nuati-framework @ R)"; atualizar as linhas do app no README §4 do framework. Procedência só no registro de cópias do framework (README §4), nunca na pasta.
  O que é do app fica fora delas: etapas do tempo economizado em `economia.py`, tema em `.streamlit/config.toml`.
- Da rede da Câmara (PC do trabalho, 28/09) os 4 serviços externos passaram: Gemini, Groq, Cerebras, OpenRouter. O Gemma (servidor local, `LLM_BASE_URL`) só é alcançável daqui;
  no Cloud, sem `LLM_BASE_URL`.
- Testes locais: `LLM_SOMENTE=nenhum py -3.13 -m pytest tests llm_cadeia pptx_opc tempo_economizado branding -q`
  (`LLM_SOMENTE=nenhum` garante que nada chame LLM de verdade; o `python` do PATH é o atalho da Store, use o `py`). O render do `pptx_opc` só roda com `NUATI_TESTE_POWERPOINT=1`. Segredos locais em `~/.streamlit/secrets.toml` (fora do repo).
- Porta 8502 pode estar ocupada pelo app de Checklist; suba o scopediagram em outra (`--server.port 8531`).
- PPTX: template é **SmartArt**; `python-pptx` não o edita → `templatefill/` mexe no XML (zip + lxml). O LibreOffice
  **não** regenera SmartArt; o `drawingN.xml` em cache é obrigatório. Cada lane = 1 `dsp:sp` com N parágrafos; no
  `data*.xml` cada item é um `dgm:pt` (D3). Lanes são achadas **por texto**, nunca por ordem.
- QA visual fiel: PowerPoint real via COM, `py -3.13 -m pptx_opc.render_powerpoint <pptx> <pasta>` (precisa de
  `pywin32`, fora do `requirements.txt`). Antes/depois: `tools/qa_gerar_exemplo.py` + render + `tools/qa_compara_png.py`
  (prova por PNG, não por bytes: `LESSONS.md` 05/10). Extração real: `tools/qa_extracao_real.py`.

## 4. Disciplina
Um chunk por vez → verificar → atualizar durables → commit → `/checkpoint`. Trabalho em `homologacao`; push na `main` só com ok do
Rodrigo (promoção).

## 5. Próximo movimento (recomendação)
1. Com a confirmação do Rodrigo: apagar `feat/llm-cadeia` (`../BLOCKED-ON-RODRIGO.md`).
2. Trabalho novo em `homologacao`; P2 de `_TODO.md` (rótulo SUBPROCESSOS, `use_container_width`).

## 6. Ponteiros
| Doc | Propósito |
|---|---|
| `_TODO.md` · `_DECISOES-PENDENTES.md` · `log.md` | tarefas · decisões (D5-D7 do passe; eco D-C22/23/24, cumpridas) · timeline |
| `../BLOCKED-ON-RODRIGO.md` · `../LESSONS.md` | ações só-humano · lições transversais |
| `../llm_cadeia/README.md` | módulo de LLM (uso, segredos, changelog) |
| `../.streamlit/secrets.toml.example` | nomes dos segredos (sem valores) |
| `superpowers/specs/2026-07-02-template-based-ppt-generation-design.md` | arquitetura do PPTX |
| `superpowers/specs/2026-07-08-smartart-data-model-editability-design.md` | editabilidade do SmartArt (D3) |
| `../templatefill/{igoe,builder}.py` · `../pptx_opc/` (OPC + render, do framework) | motor PPTX · QA via PowerPoint |
| `../economia.py` · `../tools/qa_*.py` | etapas do tempo economizado · scripts de QA (receita no docstring) |
| `../../nuati-framework` · `../../buscador-normativos` | clones irmãos neste PC: origem das pastas do framework e de onde vêm os SHAs externos citados (`ab3fa66` = tag v0.1.0, `bc24c61`, `2221d74`: framework; `7f1c069`: buscador) |

## 7. Como atualizar
Ao mudar de estado: §2/§5, `last_updated`, entrada no `log.md`, ledgers; snapshot de memória datado se mudou muito.
