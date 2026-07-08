# Design — Reconstrução do modelo de dados do SmartArt (editabilidade pós-geração)

**Data:** 2026-07-08
**Autor:** brainstorming assistido (Claude) + Rodrigo
**Status:** aguardando revisão (verificação por subagentes independentes antes da implementação)
**Resolve:** D3 em `docs/_DECISOES-PENDENTES.md` (decisão tomada: opção B — reconstruir nós do modelo de dados)

## Problema

O gerador (`templatefill/igoe.py`) hoje edita apenas o **desenho SmartArt em
cache** (`drawing*.xml`) — é o que garante o render correto (fato já verificado:
LibreOffice não regenera o desenho a partir do modelo de dados). O **modelo de
dados** (`data*.xml`), que é a fonte que o PowerPoint usa quando o usuário
**edita o SmartArt de dentro do PowerPoint**, só é sincronizado de forma
melhor-esforço (`_sync_data_text`): substitui texto de nós existentes 1:1 só
quando a contagem bate exatamente, e não recria a topologia. Como o número de
itens por lane é variável (é o requisito do próprio gerador), a contagem quase
nunca bate — ou seja, hoje a edição pós-geração no PowerPoint é essencialmente
não suportada; se o usuário editar o SmartArt, o PowerPoint pode recalcular o
desenho a partir do modelo de dados desatualizado e reexibir texto de exemplo
do template.

## Decisão do usuário

Rodrigo confirmou (2026-07-08) que **precisamos de editabilidade pós-geração**:
o deck gerado deve poder ser aberto e editado no PowerPoint sem reverter para
texto do template. **Critério de sucesso assumido** (pergunta de escopo feita
ao usuário não teve resposta síncrona — assumindo a opção de menor risco,
sinalizado explicitamente para correção posterior se necessário):
- ✅ Alvo: editar texto de um item existente no PowerPoint mantém a lista correta.
- ❌ Fora de escopo por ora: suportar adicionar/remover itens de uma lane
  **interativamente pela UI do SmartArt** do PowerPoint após a geração — não
  testável nesta máquina (sem PowerPoint real) e não foi pedido explicitamente.

## Achado técnico (verificado no XML real do template, não suposição)

Inspecionado `ppt/diagrams/data8.xml` do arquivo de referência
(`Diagramas de Escopo_Realizar Auditoria e subprocessos_2026_GSF.pptx`, unidade
usada pelo `slide15`). Cada lane (ENTRADAS/ATIVIDADES/SAÍDAS) já contém, no
próprio template, múltiplos itens reais de lista usando o padrão nativo do
SmartArt "hProcess7":

- ENTRADAS: 6 nós de conteúdo → objeto de apresentação compartilhado `{6C142579-...}`
- ATIVIDADES: 4 nós de conteúdo → `{157C8837-...}`
- SAÍDAS: 5 nós de conteúdo → `{AB3238E6-...}`

**Estrutura repetível por item de lista** (confirmada via `dgm:ptLst` +
`dgm:cxnLst`):

1. Um `dgm:pt` de conteúdo — `modelId` próprio, `dgm:t` com o texto (parágrafo(s)
   `a:p`/`a:r`, herdando `rPr` de um item-molde existente).
2. Um `dgm:pt type="parTrans"` e um `dgm:pt type="sibTrans"` — nós de transição
   vazios (`dgm:t` com só `endParaRPr`), exigidos pelo schema, referenciados por
   `parTransId`/`sibTransId` no `cxn` de hierarquia (não aparecem em nenhum
   `srcId`/`destId` diretamente).
3. Um `dgm:cxn` de hierarquia (sem atributo `type`, i.e. `parOf` implícito):
   `srcId` = nó-raiz da lane, `destId` = novo nó de conteúdo, `srcOrd`/`destOrd`
   = posição na lista, `parTransId`/`sibTransId` = os dois nós do item 2.
4. Um `dgm:cxn type="presOf"`: `srcId` = novo nó de conteúdo, `destId` = objeto
   de apresentação **compartilhado** da lane (mesmo para todos os itens da
   mesma lane), `ord` = posição, `presId` = `urn:microsoft.com/office/officeart/2005/8/layout/hProcess7`.

Ou seja: a "lista variável dentro de uma lane" já é um padrão nativo do
SmartArt, não uma view custom nossa — múltiplos nós de dados mapeando para o
mesmo shape de apresentação. Isso reduz o risco frente ao que estava registrado
no ledger de decisões ("reconstruir topologia — esforço alto, XML frágil"):
o "esforço alto" continua existindo (é código XML novo), mas "frágil" foi
substituído por "mecânico", porque replicamos um padrão que o próprio Office
já usa e valida.

## Abordagem escolhida

Nova função em `templatefill/igoe.py`, substituindo `_sync_data_text`:

```
_rebuild_lane_data_nodes(pkg, data_name, lane_root_id, shared_pres_id, items, template_child_pt)
```

Chamada 1x por lane (3x por slide) a partir de `_fill_lanes`, com os IDs
descobertos dinamicamente (não hardcoded — ver "Descoberta de IDs" abaixo, o
template varia por slide clonado).

Passo a passo por lane:

1. **Localizar** o nó-raiz da lane no `data*.xml` pelo texto do rótulo (mesmo
   critério já usado no desenho: comparar texto normalizado contra
   `LANE_LABELS`), e o `presOf` que aponta para o objeto de apresentação
   compartilhado dos filhos atuais dessa lane.
2. **Remover** todos os nós-filho de conteúdo atuais da lane + seus
   `parTrans`/`sibTrans` (via `parTransId`/`sibTransId` do cxn de hierarquia) +
   as entradas de `cxnLst` (hierarquia e `presOf`) que os referenciam.
3. **Para cada item novo:** clonar a formatação (`rPr`) do primeiro filho-molde
   original (mesmo truque já usado em `_replace_paragraph_list` para os
   parágrafos do desenho); gerar 3 `dgm:pt` novos (conteúdo + parTrans +
   sibTrans, `modelId` via `uuid.uuid4()`) e 2 `dgm:cxn` novos (hierarquia +
   `presOf`) com `ord` sequencial.
4. **Atualizar o texto do próprio rótulo** da lane (nó-raiz) — comportamento já
   existente, mantido.
5. Serializar e gravar a parte de volta (`pkg.set_part`).

**Descoberta de IDs (não hardcoded):** como o slide IGOE é clonado por
subprocesso (`opc.py::clone_slide`), cada clone tem seu próprio `data*.xml` com
`modelId`s únicos (GUIDs do template original, preservados na clonagem — a
clonagem hoje copia bytes da parte sem regenerar IDs). O nó-raiz de cada lane é
localizado por **texto do rótulo**, exatamente como já é feito para os shapes
do desenho — não por ID fixo.

## Tratamento de erros

Mesma filosofia defensiva do código atual: se o nó-raiz da lane ou o `presOf`
compartilhado não forem localizados no formato esperado (ex.: template mudou de
estrutura), a função **não lança exceção** — registra e faz *no-op* nessa lane,
deixando o modelo de dados como estava (o render continua correto via
desenho, só a editabilidade fica degradada para essa lane específica, igual ao
comportamento best-effort de hoje). Geração nunca falha por causa disso.

## Estratégia de testes

1. **Estrutural (automatizado, roda sempre):** após gerar um deck de teste,
   parsear `data*.xml` de cada slide e verificar:
   - contagem de `dgm:pt` de conteúdo por lane == número de itens injetados;
   - todo `dgm:cxn` de hierarquia tem `parTransId`/`sibTransId` apontando para
     `dgm:pt` existentes no mesmo `ptLst`;
   - todo `dgm:cxn type="presOf"` de uma lane aponta para o **mesmo** `destId`
     compartilhado, com `ord` 0..N-1 sem buracos nem repetição;
   - XML resultante é bem-formado e a parte abre sem erro.
2. **Regressão:** testes de fumaça existentes (`tests/test_generation.py`)
   continuam passando — geração não pode quebrar.
3. **Render:** pipeline de QA visual (LibreOffice → PDF → PyMuPDF → PNG)
   confirma que o **desenho** (fonte de verdade do render) continua idêntico a
   antes — esta mudança não deve alterar nada visualmente, só o modelo de
   dados por trás.
4. **Limite conhecido, não testável nesta máquina:** o teste real de
   "abrir no PowerPoint de verdade, clicar num item do SmartArt, editar o
   texto, e o resultado continuar consistente" **não pode ser automatizado
   aqui** (sem PowerPoint instalado; LibreOffice não recalcula SmartArt a
   partir do modelo de dados). Este passo de validação final **é do usuário**
   — abrir o `.pptx` gerado no PowerPoint e confirmar manualmente.

## Fora de escopo (YAGNI)

- Suporte a adicionar/remover itens de lane **interativamente** pela UI do
  SmartArt do PowerPoint pós-geração (não pedido; não testável aqui).
- Mudar layouts SmartArt (`loTypeId`) ou coordenadas de apresentação —
  inalterado.
- Bandas/eventos/título (REGULADORES, RECURSOS, OBJETIVO, EVENTO, título) —
  são caixas de texto comuns do slide, não SmartArt; já totalmente editáveis
  hoje, sem relação com este trabalho.

## Riscos residuais

- **Risco principal:** o comportamento real do motor de layout do PowerPoint
  ao recalcular a partir do modelo de dados reconstruído não pode ser
  verificado nesta máquina antes da entrega. A verificação estrutural garante
  que o XML é **bem-formado e consistente com o padrão nativo observado**, mas
  não garante 100% que o PowerPoint vai aceitar sem ressalvas — só a abertura
  real no PowerPoint resolve essa dúvida.
- Mitigação: tratamento de erro no-op (acima) garante que, na pior hipótese, o
  resultado é idêntico ao comportamento atual (render correto, edição
  degradada) — nunca pior do que hoje.
