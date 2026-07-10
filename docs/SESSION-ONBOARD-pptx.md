---
title: PPTX generation — session onboarding / state snapshot
maintained_by: Claude Code sessions; humans can edit too
last_updated: 2026-07-09
related: [_TODO.md, _DECISOES-PENDENTES.md, log.md]
---

# PPTX (geração do PowerPoint) — session onboarding

Ponto de entrada único para qualquer sessão nova nesta área. ≤ 1 página; atualizado
em cada pausa. Histórico em `log.md`; backlog em `_TODO.md`; decisões abertas em
`_DECISOES-PENDENTES.md`.

## 1. O que é (30s)
App Streamlit (`app.py`) que extrai um modelo IGOE de um texto via LLM (`llm.py` →
`ScopeDiagram` em `schema.py`) e gera um PowerPoint de diagrama de escopo,
**preenchendo o template real de referência (SmartArt)** — pacote `templatefill/`.
Deploy: `main`, dois remotes (`github` e `origin`/git.camara.gov.br).

## 2. Estado na última pausa (2026-07-09)
### Feito & commitado
- **`main`**: geração por template (SmartArt) mergeada e em deploy (D1/D2 decididas
  2026-07-08 — usuário testou ao vivo, funcionou; merge direto, push nos dois remotes).
- **Branch `feature/smartart-data-model-editability`** (ainda não mergeada): D3
  implementada — reconstrução do modelo de dados do SmartArt para editabilidade
  pós-geração no PowerPoint. `_find_lane_roots` → `_rebuild_lane_nodes` →
  `_sync_data_nodes` em `templatefill/igoe.py`, substituindo o antigo
  `_sync_data_text` (best-effort, removido). 6 tasks TDD, cada uma implementada e
  revisada por subagente independente (todas aprovadas); revisão final de branch
  inteira (achado importante — `<dgm:spPr/>` faltante nos nós reconstruídos —
  corrigido). Spec: `docs/superpowers/specs/2026-07-08-...-design.md`. Plano:
  `docs/superpowers/plans/2026-07-08-...editability.md`.
### Working tree
- Limpo, EXCETO `D .streamlit/secrets.toml.example` (deleção não desta sessão,
  ainda pendente de decisão — não tocado) e 2 arquivos `.pptx` do usuário não
  rastreados (deixados intocados).
### Verificado (não assumido)
- Testes de fumaça (`tests/test_generation.py`) + testes novos
  (`tests/test_smartart_data_nodes.py`, 15 testes) passam limpos.
- QA visual (LibreOffice → PDF → PyMuPDF → PNG) num deck de 2 subprocessos: lanes
  SUBPROCESSOS/ATIVIDADES corretas, sem overflow/sobreposição, sem vazamento de
  texto do template — confirma que a mudança do D3 não afetou o render (só o
  modelo de dados).
### Pendente / em aberto
- **Fechar a branch `feature/smartart-data-model-editability`** (finishing-a-development-branch:
  merge/PR/manter — ainda não decidido nesta sessão).
- **Validação manual do usuário**: abrir o `.pptx` gerado no PowerPoint de
  verdade, editar um item de lane no SmartArt, confirmar que não reverte para
  texto do template. Não testável nesta máquina (sem PowerPoint; LibreOffice não
  recalcula SmartArt a partir do modelo de dados).

## 3. Achados críticos (não perder — custam tempo se redescobertos)
- Template de referência é **SmartArt** (17 diagramas). `python-pptx` NÃO edita SmartArt de forma confiável → por isso o `templatefill/` mexe no XML direto (zip + lxml).
- **LibreOffice NÃO regenera SmartArt** a partir do modelo de dados quando o desenho em cache é removido (render vira lixo). Logo o `drawingN.xml` em cache é obrigatório.
- Cada lane = **1 `dsp:sp` com N parágrafos** no desenho; no **modelo de dados**
  (`data*.xml`), cada item de lista é um **nó `dgm:pt` próprio** (padrão nativo
  `hProcess7`: conteúdo + `parTrans`/`sibTrans` + `cxn` de hierarquia + `cxn
  presOf` compartilhado) — reconstruído por `_rebuild_lane_nodes` (D3).
- Descoberta de lane no modelo de dados é **por texto** (nunca por ordem de
  documento, que não existe ali) — esquerda/direita por igualdade exata,
  meio por eliminação (a lane do meio pode ter rótulo-alvo "SUBPROCESSOS" no
  slide de processo, mas o texto atual no modelo de dados ainda é "ATIVIDADES").
- Novo gerador depende **só de lxml** (não de python-pptx).
- **Extração NÃO foi tocada** (`llm.py`, `prompts/extraction.txt`, `schema.py` intactos).
- QA visual: LibreOffice `C:\Program Files\LibreOffice\program\soffice.exe` → PDF → PyMuPDF (`fitz`) → PNG.

## 4. Disciplina de trabalho
Um chunk = uma onda; carregue só o contexto necessário. Fecha o chunk: limpeza → verificar/render → atualizar durables → commit. `/onboard-pptx` retoma daqui.

## 5. Próximo movimento (recomendação, não decidido)
1. Rodar `superpowers:finishing-a-development-branch` para a branch
   `feature/smartart-data-model-editability` (merge/PR/manter).
2. Pedir ao usuário a validação manual no PowerPoint de verdade (item pendente acima).

## 6. Ponteiros (só caminhos — sem duplicar conteúdo)
| Doc | Propósito |
|---|---|
| `_TODO.md` | ledger de tarefas |
| `_DECISOES-PENDENTES.md` | decisões só-humano |
| `log.md` | timeline append-only |
| `docs/superpowers/specs/2026-07-02-template-based-ppt-generation-design.md` | spec da arquitetura original (template-based) |
| `docs/superpowers/specs/2026-07-08-smartart-data-model-editability-design.md` | spec da editabilidade do SmartArt (D3) |
| `docs/superpowers/plans/2026-07-08-smartart-data-model-editability.md` | plano de implementação do D3 |
| `templatefill/{opc,igoe,builder}.py` | motor OPC / preenchimento IGOE / orquestrador |

## 7. Como atualizar
Ao mudar de estado: atualize §2/§5, bump `last_updated`, prepend em `log.md`, refresque o
ledger de decisões, drope um snapshot de memória datado se o estado mudou materialmente. ≤ 1 página.
