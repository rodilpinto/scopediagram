# Design — Geração de PPT por preenchimento do template real

**Data:** 2026-07-02
**Autor:** brainstorming assistido (Claude) + Rodrigo
**Status:** aguardando revisão do humano

> ⚠ **Nota de 06/10/2026:** este é o desenho original. A implementação real ficou em `templatefill/builder.py` e
> `templatefill/igoe.py`, com o pacote OPC em `pptx_opc/` (veio do `nuati-framework`; antes era `templatefill/opc.py`).
> Os módulos `igoe_slide.py`, `slide_unit.py`, `layout.py` e `tools/qa_render.py` citados abaixo não existem. QA de hoje:
> `python -m pptx_opc.render_powerpoint` e `tools/qa_*.py`.

## Problema

O gerador atual (`ppt.py`) constrói os slides **do zero** com retângulos e caixas
de texto do `python-pptx`, usando coordenadas e cores estimadas. O conteúdo sai
bom, mas a **forma nunca ficou boa** — não reproduz o visual do PowerPoint de
referência da Secretaria de Controle Interno.

O arquivo de referência
(`Diagramas de Escopo_Realizar Auditoria e subprocessos_2026_GSF.pptx`) é um deck
didático de 24 slides cujos diagramas de escopo são **SmartArt** (17 objetos,
`data1..data17`). `python-pptx` não edita SmartArt de forma confiável — por isso o
código o evitou até agora.

## Objetivo

O usuário solta um documento de processo (ex.: um Papel de Trabalho de auditoria)
e o app devolve um `.pptx` **com a mesma forma do template**, apenas com o
conteúdo trocado — sem sobreposição, sem texto fora das caixas, mantendo a
consistência visual entre slides.

## Decisões do usuário (fixadas)

1. **Escopo do deck:** apenas diagramas (enxuto) — capa + 1 diagrama IGOE do
   processo + 1 diagrama IGOE por subprocesso. Os slides didáticos são descartados.
2. **Por subprocesso:** exatamente **1 slide IGOE limpo** por subprocesso.
3. **Preview x deploy:** o `.pptx` baixado é o entregável perfeito; o preview no
   app continua sendo a aproximação leve atual (Graphviz), mantendo o deploy no
   Streamlit Community Cloud (que não roda LibreOffice).
4. **Caixas:** podem crescer/encolher conforme o conteúdo; a **consistência**
   (mesma fonte, mesmo estilo, lanes alinhadas) deve ser preservada.
5. **Variabilidade:** número de subprocessos e tamanho das listas são variáveis.

## Abordagem escolhida — "Template como substrato, editar o desenho real"

Rejeitadas:
- **python-pptx editando SmartArt** — não acessa as partes de desenho (`drawing*`),
  que são justamente o diagrama. Inviável.
- **Reconstruir com formas do zero** — é o que já falhou ("nunca ficou bom").

Escolhida: abrir o template como pacote OPC, **selecionar** a capa (slide1) e a
unidade IGOE (slide15), **clonar** a unidade IGOE por subprocesso, e **preencher**
o conteúdo editando (a) as caixas de texto do slide e (b) as formas do desenho
SmartArt em cache. O layout do corpo é controlado por nós — nós dimensionamos as
caixas conforme o conteúdo.

### Suposições já verificadas empiricamente (spikes 2026-07-02)

1. Editar texto no XML → repack → render = **pixel-perfect** (spike 1, slide15).
2. LibreOffice **não** regenera SmartArt a partir do modelo de dados quando o
   desenho em cache é removido — render fica ilegível. ⇒ o desenho em cache
   (`drawing*.xml`) é **obrigatório** e precisa ser mantido/gerado por nós.
3. LibreOffice **não** converte SmartArt em formas comuns no round-trip pptx.
4. Cada lane do IGOE é **1 forma `dsp:sp` com N parágrafos** (um por item).
5. OBJETIVO / REGULADORES / RECURSOS / EVENTO / título são **caixas de texto
   comuns** no XML do slide.
6. Fiação da unidade IGOE conhecida: `slide15` → `data8 + layout8 + colors8 +
   quickStyle8 + drawing8` (`r:dm/lo/qs/cs` + rel de `diagramDrawing`).
7. Pipeline de QA visual funciona nesta máquina: LibreOffice → PDF → PyMuPDF → PNG.

### Unidades do template reaproveitadas

- **Capa** ← `slide1` (caixas comuns: data, "Diagramas de Escopo", título em caixa
  alta). Campos: data, título do processo.
- **Slide IGOE** ← `slide15` (unidade completa acima). É usado para:
  - **Processo:** lane do meio rotulada `SUBPROCESSOS`, itens = nomes dos
    subprocessos; ENTRADAS/SAÍDAS/REGULADORES/RECURSOS = elementos globais.
  - **Subprocesso:** lane do meio `ATIVIDADES`, itens = atividades.
  Uma única unidade, reutilizada N+1 vezes ⇒ consistência garantida.

## Arquitetura de componentes

Substitui o interior de `ppt.py`. Novo pacote `templatefill/`:

> ⚠ Lista de módulos superada: ver a nota de 06/10/2026 no topo.

- `opc.py` — pacote OPC em memória (zipfile + lxml): ler/gravar partes, adicionar/
  remover partes, gerir `_rels`, `[Content_Types].xml` e a ordem de `sldId` em
  `presentation.xml`. Sem dependência de SmartArt no runtime além de texto/geometria.
- `igoe_slide.py` — preenche uma unidade IGOE: título e bandas (caixas do slide);
  rótulo e lista de parágrafos da lane (no `drawing*` **e** no `data*`, mantidos em
  sincronia de texto); geometria das caixas conforme conteúdo.
- `slide_unit.py` — clona/poda unidades de slide: duplica a unidade `slide15` com
  numeração nova de partes, refazendo rels, content-types e `presentation.xml`.
- `layout.py` — regras de dimensionamento consciente do conteúdo (abaixo).
- `builder.py` — orquestra: `ScopeDiagram` → capa + IGOE do processo + N IGOE de
  subprocesso. Expõe `generate_ppt_bytes(scope) -> bytes`.
- `ppt.py` vira um shim: `from templatefill.builder import generate_ppt_bytes`
  (mantém o import de `app.py` intacto).

Fora do runtime de deploy:
- `tools/qa_render.py` — renderiza os bytes gerados (LibreOffice→PDF→PNG) e roda
  checagens automáticas de overflow/sobreposição + exporta imagens para revisão
  visual por subagente. Usado em desenvolvimento/testes, não no app publicado.
- `renderer.py` (Graphviz) — **inalterado**, continua sendo o preview aproximado.

## Fluxo de dados

texto/arquivo/formulário → `llm.extract_scope` → `ScopeDiagram`
→ `templatefill.generate_ppt_bytes(scope)` → `.pptx` perfeito (download).
Preview in-app: `renderer.build_preview_images` (aproximado, inalterado).

## Dimensionamento consciente do conteúdo (consistência)

- **Fontes fixas por tipo de elemento** (título, rótulo de banda, corpo de banda,
  rótulo de lane, item de lane), extraídas dos valores reais do template ⇒
  consistência entre slides.
- **Altura das caixas = f(nº de linhas no texto, largura, fonte).** As três lanes
  compartilham topo comum e adotam a **maior** altura entre elas, permanecendo
  alinhadas. As bandas crescem para caber o texto. A pilha vertical é recalculada
  de cima para baixo.
- **Setas** entre lanes reposicionadas ao centro vertical das lanes.
- **Último recurso** (conteúdo excede a altura do slide): redução uniforme de
  fonte, registrada em log — nunca corta texto silenciosamente.

## Tratamento de erros e rastreabilidade

- Campos ausentes/vazios do escopo: a lane/banda mostra marcador visível
  `— (não identificado no documento)`. **Não inventamos conteúdo** para preencher
  o IGOE (regra do usuário: não misturar sugestão com fato). O app também sinaliza
  quais elementos IGOE ficaram vazios após a extração.
- Parte do template ausente/malformada: erro claro, sem gerar arquivo corrompido.
- Extração pobre (ex.: PT rico em reguladores, pobre em atividades): o resultado
  reflete honestamente o que foi extraído; o vazio fica evidente.

## Estratégia de testes / QA (obrigatória)

1. **Unitário:** cada edição produz XML bem-formado; clonagem gera OPC válido
   (`scripts/office/validate.py`).
2. **Render golden:** gerar deck a partir de um escopo conhecido; renderizar todos
   os slides a PNG e verificar:
   - (a) todo texto injetado presente (`markitdown`);
   - (b) **checagem automática de overflow** — bbox do texto dentro do bbox da caixa
     (via PyMuPDF);
   - (c) revisão visual por **subagente** (olhos frescos) para sobreposição, texto
     fora da caixa e placeholder residual.
3. **Abertura limpa:** validar sem avisos; abrir no LibreOffice sem erro.
4. Ciclo corrigir-e-reverificar até uma passada limpa (padrão da skill pptx).

## Fora de escopo (YAGNI)

- Slides didáticos do template.
- Preview pixel-perfect in-app (fica aproximado; entregável é o download).
- Edição de SmartArt via reconstrução do modelo de dados/regeneração.
- Múltiplos slides por subprocesso (mantém-se 1 IGOE limpo).

## Documento de teste do usuário

`.../pts/pt1-entendimento-objeto-lgpd-v1.11-rerevisao-ia.md` — será usado como
entrada real. Observação honesta: é um documento de **comentários de re-revisão de
auditoria**, rico em **reguladores** (LGPD, Portaria 90/2026, Res. 15/2024, Acórdão
190/2026, Decreto 9.203/2017) porém pobre em entradas/saídas/atividades/subprocessos
explícitos. Serve para exercitar o pipeline, mas o deck resultante evidenciará
lacunas de IGOE em vez de preenchê-las com invenção.
