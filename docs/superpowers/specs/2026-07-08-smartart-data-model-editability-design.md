# Design — Reconstrução do modelo de dados do SmartArt (editabilidade pós-geração)

**Data:** 2026-07-08
**Autor:** brainstorming assistido (Claude) + Rodrigo
**Status:** verificada por 3 subagentes independentes (2026-07-08) — achados incorporados abaixo
**Resolve:** D3 em `docs/_DECISOES-PENDENTES.md` (decisão tomada: opção B — reconstruir nós do modelo de dados)

## Verificação independente (2026-07-08)

Três subagentes de contexto zerado revisaram esta spec de forma independente,
cada um refazendo a investigação a partir do XML real (não confiando no texto
da spec): (1) conferência byte-a-byte das afirmações estruturais contra
`ppt/diagrams/data8.xml`, (2) viabilidade de implementação contra o código
real (`templatefill/`), (3) revisão adversarial de casos-limite. **Nenhuma
afirmação da seção "Achado técnico" foi contestada** — todas se confirmaram
exatamente no XML real. Os três encontraram, juntos, 2 lacunas sérias e várias
menores, todas já incorporadas nas seções abaixo:

1. **(Grave) Falta isolamento transacional por lane.** Uma exceção no meio da
   reconstrução de uma lane (depois de remover os filhos antigos, antes de
   terminar os novos) podia deixar o XML gravado pela metade. Ver "Tratamento
   de erros" abaixo.
2. **(Grave) Atributo `cxnId` de retorno nos nós `parTrans`/`sibTrans`** não
   estava documentado — sem ele, o XML fica inconsistente com o padrão nativo.
   Ver "Estrutura repetível" abaixo.
3. Lane vazia (`items=[]`) podia divergir do desenho (que sempre usa `"—"` de
   fallback) se a função recebesse a lista crua. Ver "Normalização de entrada".
4. Mapeamento de posição da lane (esquerda/meio/direita) **não pode** ser por
   ordem de documento no `data*.xml` (não há coordenadas ali, ao contrário do
   `drawing*.xml`) — precisa ser por igualdade de texto contra os rótulos fixos.
   Ver "Descoberta de IDs".
5. Trap de remoção: o próprio nó-raiz/rótulo da lane tem seus 2 `presOf`
   próprios — remover ingenuamente por `srcId == lane_root_id` sem checar
   `type` apagaria esses 2 também. Ver "Remoção segura".
6. Faltava: `custT="1"` no `prSet` dos nós de conteúdo; sequenciar "capturar o
   molde de formatação ANTES de remover os filhos antigos"; remoção por
   conjunto de IDs (não `.find()` de primeira ocorrência) para garantir
   idempotência; decisão explícita sobre logging (código hoje não tem nenhuma
   infra de log). Todos incorporados abaixo.

**Segunda rodada de verificação (2 subagentes novos, focados nas correções
acima):** as 4 correções técnicas (cxnId, custT, troca srcOrd/destOrd, os 2
presOf do rótulo) foram confirmadas byte-a-byte de novo, sem contestação. Mas
a revisão de consistência do documento como um todo achou uma **lacuna
arquitetural real**: a assinatura de função proposta, o "passo a passo por
lane" e a seção de isolamento transacional descreviam **três papéis
incompatíveis** para quem descobre os IDs, quem chama o quê, e quem grava o
XML — sem isso resolvido, "isolamento transacional" não era implementável sem
o implementador inventar a arquitetura sozinho. A seção "Abordagem escolhida"
abaixo foi reescrita para fechar isso com uma divisão explícita
orquestrador/mutator puro. Também faltava um teste cobrindo o risco #4
(mapeamento por texto, não por ordem de documento) — adicionado na seção de
testes.

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
`dgm:cxnLst`, byte-a-byte contra o XML real por subagente independente):

1. Um `dgm:pt` de conteúdo — `modelId` próprio (GUID no formato
   `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`, maiúsculo, com chaves — mesmo
   estilo do template; `uuid.uuid4()` do Python gera minúsculo sem chaves,
   precisa de formatação explícita). `dgm:prSet` com **`phldrT="[Texto]"
   custT="1"`** (o `custT="1"` é o que marca "texto do usuário", presente em
   todo nó de conteúdo real do template — ausente nos rótulos de lane).
   `dgm:t` com o texto (parágrafo(s) `a:p`/`a:r`, herdando `rPr` de um
   item-molde existente — **capturar esse molde ANTES de remover os filhos
   antigos**, senão não sobra exemplo para clonar).
2. Um `dgm:pt type="parTrans"` e um `dgm:pt type="sibTrans"` — nós de transição
   vazios (`dgm:t` com só `endParaRPr`), exigidos pelo schema. **Cada um carrega
   um atributo `cxnId`** que aponta de volta para o `modelId` do `dgm:cxn` de
   hierarquia do item 3 (back-reference bidirecional: o cxn referencia os dois
   via `parTransId`/`sibTransId`, e os dois referenciam o cxn via `cxnId`) —
   verificado consistente nos 36 nós de transição do template real, 0
   divergências. **Nenhum dos dois aparece como `srcId`/`destId` de qualquer
   `cxn`** — só existem via essas referências cruzadas de atributo.
3. Um `dgm:cxn` de hierarquia (sem atributo `type`, i.e. `parOf` implícito):
   `modelId` próprio (usado como `cxnId` no item 2), `srcId` = nó-raiz da lane,
   `destId` = novo nó de conteúdo, **`srcOrd`** = posição na lista (0..N-1,
   escopado por lane — não colide entre lanes), `destOrd="0"` (fixo),
   `parTransId`/`sibTransId` = os dois nós do item 2.
4. Um `dgm:cxn type="presOf"`: `srcId` = novo nó de conteúdo, `destId` = objeto
   de apresentação **compartilhado** da lane (mesmo para todos os itens da
   mesma lane), `srcOrd="0"` (fixo), **`destOrd`** = posição na lista (0..N-1 —
   nota: é `destOrd` aqui, não `srcOrd`; os dois atributos de ordem trocam de
   papel entre o cxn de hierarquia e o cxn `presOf` e precisam ficar
   sincronizados manualmente pelo código, não há vínculo automático), `presId`
   = `urn:microsoft.com/office/officeart/2005/8/layout/hProcess7`.

**Não tocar:** a árvore `presParOf` (estrutura de apresentação fixa do layout,
também dentro de `data*.xml`) é independente da contagem de itens — não
referencia os `modelId`s de conteúdo que serão trocados. A nova função não deve
mexer nela.

Ou seja: a "lista variável dentro de uma lane" já é um padrão nativo do
SmartArt, não uma view custom nossa — múltiplos nós de dados mapeando para o
mesmo shape de apresentação. Isso reduz o risco frente ao que estava registrado
no ledger de decisões ("reconstruir topologia — esforço alto, XML frágil"):
o "esforço alto" continua existindo (é código XML novo), mas "frágil" foi
substituído por "mecânico", porque replicamos um padrão que o próprio Office
já usa e valida.

## Abordagem escolhida

Duas camadas, para separar "faz I/O" de "muta XML puro" — é essa separação que
torna o isolamento transacional (abaixo) implementável sem ambiguidade:

**Camada 1 — orquestrador** `_sync_data_nodes(pkg, data_name, lanes)`, em
`templatefill/igoe.py`, chamado **1x por slide** a partir de `_fill_lanes`
(substituindo a chamada a `_sync_data_text`) — mesma assinatura de 3
argumentos que `_sync_data_text` já tem hoje, sem precisar mudar o call site
além de trocar o nome da função chamada. `left_label`/`right_label` são
derivados de `lanes[0][0]`/`lanes[2][0]` (a ordem `[esquerda, meio, direita]`
já é a mesma ordem em que `_fill_lanes` monta `lanes` hoje). Só ele toca `pkg`:

```
def _sync_data_nodes(pkg, data_name, lanes):
    # lanes = [(left_label, left_items), (mid_label, mid_items), (right_label, right_items)]
    if not pkg.has_part(data_name):
        return
    root = etree.fromstring(pkg.part(data_name))
    work = copy.deepcopy(root)          # mutações acontecem só na cópia

    left_label, right_label = lanes[0][0], lanes[2][0]
    found = _find_lane_roots(work, left_label, right_label)  # 1x por slide — ver abaixo
    if found is None:
        return                          # pré-checagem falhou: no-op para as 3 lanes

    try:
        for (lane_root_pt, shared_pres_id), (label, items) in zip(found, lanes):
            _rebuild_lane_nodes(work, lane_root_pt, shared_pres_id, label, items)  # pode levantar
    except Exception:
        return                          # aborta a operação inteira: NÃO grava `work`

    pkg.set_part(data_name, etree.tostring(work, xml_declaration=True,
                                            encoding="UTF-8", standalone=True))
```

- `_find_lane_roots` (pré-checagem, 1x por slide): retorna `None` sozinho —
  **nunca lança** — se a contagem básica de 3 rótulos de lane não bater, ou
  `left_label`/`right_label` não forem localizados, é no-op para a sincronia
  de dados **inteira** do slide (as 3 lanes de uma vez — não há como confiar
  em achar 2 de 3 com segurança se a estrutura básica já não bate).
- `_rebuild_lane_nodes` (o mutator, camada 2): **pode lançar exceção** —
  qualquer erro no meio da reconstrução de uma lane propaga até o
  `try/except` do orquestrador, que descarta `work` inteiro e **não chama
  `pkg.set_part`** — a parte original (`pkg.part(data_name)`, o que já estava
  lá antes desta chamada) permanece intocada. Isso resolve a assimetria dos
  dois modos de falha: pré-checagem malsucedida = *no-op para todo o slide*
  (soft, `_find_lane_roots is None`); exceção durante a reconstrução de
  qualquer lane = *aborta a operação inteira para o slide* (hard, via
  `except`) — nunca uma escrita parcial. (Nota: a versão anterior desta
  seção descrevia a pré-checagem como "no-op só naquela lane" — corrigido
  junto com a descoberta de IDs, ver nota na seção "Descoberta de IDs"; com
  descoberta em lote de 1x por slide, o no-op de pré-checagem também passa a
  ser em lote.)

**Camada 2 — mutator puro** `_rebuild_lane_nodes(work, lane_root_pt, shared_pres_id, label, items)`:
opera só sobre elementos `lxml` já em memória (o `work` da camada 1) — **não
recebe `pkg` nem `data_name`, não faz parsing nem serialização**. Só muta a
árvore e levanta exceção se algo inesperado acontecer (deixa a camada 1
decidir o que fazer com isso). `label` é o rótulo-alvo (necessário no passo 4
— para a lane do meio, pode ser diferente do texto atual de `lane_root_pt`,
ex. "ATIVIDADES" → "SUBPROCESSOS"; para esquerda/direita já bate por
construção, então o passo 4 é um no-op inofensivo nesses casos). Passo a
passo:

1. **Capturar o molde de formatação** (`rPr` de um filho-molde de conteúdo
   atual de `lane_root_pt`) **antes** de remover qualquer coisa — depois de
   removido não sobra exemplo para clonar.
2. **Remoção segura, por conjunto de IDs coletados primeiro** (não por
   `.find()` de primeira ocorrência — isso é o que garante idempotência: uma
   segunda chamada não deixa nós órfãos):
   - Coletar o conjunto de `modelId`s dos filhos de conteúdo atuais (via
     `cxn` de hierarquia com `srcId == lane_root_pt.modelId` **e sem atributo
     `type`** — este filtro por ausência de `type` é o que evita apagar os 2
     `presOf` que o próprio `lane_root_pt` tem para si mesmo, que têm
     `type="presOf"` e o mesmo `srcId` mas **não** devem ser tocados).
   - A partir desse conjunto, coletar também os `parTransId`/`sibTransId`
     referenciados (para remover os `parTrans`/`sibTrans` correspondentes) e
     os `cxn type="presOf"` cujo `srcId` esteja no conjunto.
   - Remover todos os `dgm:pt` e `dgm:cxn` desse conjunto fechado — nunca por
     índice/posição, sempre por pertencimento ao conjunto.
3. **Para cada item novo (0..N-1):** clonar a formatação capturada no passo 1;
   gerar 3 `dgm:pt` novos (conteúdo com `custT="1"` + parTrans + sibTrans,
   `modelId` via `uuid.uuid4()` formatado em maiúsculo com chaves) e 2
   `dgm:cxn` novos (hierarquia com `srcOrd=k`/`destOrd="0"` + `presOf` com
   `srcOrd="0"`/`destOrd=k`, ambos apontando para `shared_pres_id`) — ver
   atributos exatos na seção "Achado técnico" acima.
4. **Atualizar o texto do próprio rótulo** (`lane_root_pt`) — comportamento já
   existente, mantido.
5. Retorna `None` (sucesso — muta `work` in-place) ou deixa a exceção propagar
   (a camada 1 decide o resto). **Não grava nada** — quem grava é a camada 1.

**Normalização de entrada:** em vez de centralizar em `_fill_lanes` (que
exigiria mudar a construção de `lanes`, usada também pelo desenho),
`_rebuild_lane_nodes` aplica **a mesma regra, no mesmo estilo**, já usada por
`_replace_paragraph_list` (linha 113 de `igoe.py`) para o desenho: primeira
linha da função, `items = [i for i in items if i and i.strip()] or ["—"]`.
Cada consumidor normaliza a sua cópia de `items` de forma independente e
idêntica — desenho e modelo de dados nunca divergem sobre "lane vazia" porque
aplicam exatamente a mesma regra à mesma entrada, sem precisar de um ponto
central. Mais simples que tocar em `_fill_lanes`, e consistente com o padrão
já existente no código (`_replace_paragraph_list` já faz sua própria
normalização, não recebe `items` pré-normalizado de fora).

**Descoberta de IDs (`_find_lane_roots`, por texto — não por posição/ordem de
documento, e não por igualdade contra o rótulo ALVO):** como o slide IGOE é
clonado por subprocesso (`opc.py::clone_slide`), cada clone tem seu próprio
`data*.xml` com `modelId`s idênticos aos do template original (clonagem copia
bytes sem regenerar IDs — confirmado; sem risco de colisão entre clones porque
cada `data*.xml` é uma parte separada e autocontida).

Importante: **o `data*.xml` não tem coordenadas geométricas** (ao contrário do
`drawing*.xml`, que ordena por `off_x`). Mapear lane→posição por "ordem de
documento" seria coincidência, não invariante garantida.

**Correção de contradição encontrada ao escrever o plano de implementação
(auto-revisão):** a versão anterior desta seção dizia para casar cada lane por
igualdade de texto contra o rótulo **alvo** (`left_label`/`mid_label`/
`right_label`, os parâmetros de `fill_igoe_slide`). Isso está **errado para a
lane do meio no slide de processo**: `mid_label="SUBPROCESSOS"` nesse caso
(`builder.py`), mas o modelo de dados **nunca é renomeado** — só o desenho é
(`_fill_lanes`, "rótulos: mapear por posição", que sobrescreve o texto do
shape do desenho independente do que ele dizia antes). O `data*.xml` do
template sempre tem o texto original `"ATIVIDADES"` nesse nó, nunca
`"SUBPROCESSOS"`. Casar por igualdade contra `mid_label="SUBPROCESSOS"`
faria a busca falhar silenciosamente (cai no caminho de no-op) toda vez que o
slide for de processo — justamente o caso mais comum. Corrigido: a descoberta
usa **`left_label`/`right_label` (que são sempre literais estáveis,
`"ENTRADAS"`/`"SAÍDAS"`, nunca renomeados em nenhum caso) para achar essas
duas lanes por igualdade exata; a lane do meio é identificada **por
eliminação** — o terceiro nó cujo texto está em `LANE_LABELS` mas não é
nenhum dos dois já casados — exatamente como o código do desenho já faz
(`_fill_lanes` também não casa a lane do meio pelo rótulo alvo; ordena as 3
por posição e usa a posição do meio). `_find_lane_roots` retorna as 3 lanes de
uma vez, nesta ordem fixa `[esquerda, meio, direita]`:

```
def _find_lane_roots(work, left_label, right_label):
    candidates = [pt for pt in work.iter(_q(DGM, "pt"))
                  if not pt.get("type") and _text_of(pt) in LANE_LABELS]
    if len(candidates) != 3:
        return None
    left_pt = next((p for p in candidates if _text_of(p) == left_label), None)
    right_pt = next((p for p in candidates if _text_of(p) == right_label), None)
    if left_pt is None or right_pt is None or left_pt is right_pt:
        return None
    mid_pt = next(p for p in candidates if p is not left_pt and p is not right_pt)

    result = []
    for pt in (left_pt, mid_pt, right_pt):
        shared = _shared_pres_id(work, pt.get("modelId"))  # via presOf de um filho atual
        if shared is None:
            return None
        result.append((pt, shared))
    return result   # [(left_pt, left_shared), (mid_pt, mid_shared), (right_pt, right_shared)]
```

O orquestrador (abaixo) chama `_find_lane_roots` **uma vez por slide** (não 3x
por lane) e itera o resultado emparelhado posicionalmente com `lanes` (que já
está em ordem `[esquerda, meio, direita]` — mesma ordem que `_fill_lanes`
monta hoje). Se `_find_lane_roots` retornar `None` (candidatos != 3, ou
left/right não localizados), é no-op para as **3 lanes de uma vez** — não dá
para achar 2 de 3 com segurança se a contagem básica de 3 rótulos já não bate
(sinal de template fora do formato esperado).

## Tratamento de erros

Já concretizado na arquitetura acima (`_sync_data_nodes` / `_rebuild_lane_nodes`)
— dois modos de falha distintos, deliberadamente assimétricos:

- **Falha na pré-checagem** (`_find_lane_roots` retorna `None` — as 3 lanes
  não foram localizadas no formato esperado, ex.: template mudou de
  estrutura): **soft** — no-op para a sincronia de dados do slide **inteiro**
  (as 3 lanes de uma vez). Render continua correto via desenho; só a
  editabilidade desse slide fica degradada (igual ao comportamento
  best-effort de hoje). Geração nunca falha por causa disso.
- **Falha no meio da reconstrução** (`_rebuild_lane_nodes` lança exceção —
  achado grave da verificação, não coberto na primeira versão desta spec):
  **hard** — propaga até o `try/except` do orquestrador, que descarta `work`
  **inteiro** e não chama `pkg.set_part`. O `data*.xml` original (de antes
  desta chamada) permanece 100% intocado — nunca uma lane pela metade
  removida/reconstruída gravada no arquivo final. Isso é o que evita
  exatamente o `.pptx` corrompido que esta feature existe para prevenir.

Sobre "registrar": o código de `templatefill/` **não tem nenhuma
infraestrutura de logging hoje** (guard clauses silenciosas, sem `import
logging`). Decisão explícita: manter esse padrão — os dois modos de falha
acima são silenciosos, sem introduzir logging novo neste trabalho. Se
rastreabilidade de quando isso acontece virar necessidade, é um item separado
(não faz parte desta spec).

## Estratégia de testes

1. **Estrutural (automatizado, roda sempre):** após gerar um deck de teste,
   parsear `data*.xml` de cada slide e verificar:
   - contagem de `dgm:pt` de conteúdo por lane == número de itens injetados
     (incluindo o caso de 1 item — fallback `"—"`);
   - todo `dgm:cxn` de hierarquia tem `parTransId`/`sibTransId` apontando para
     `dgm:pt` existentes no mesmo `ptLst`, **e** os `dgm:pt` de transição
     correspondentes têm `cxnId` apontando de volta para o `modelId` do cxn
     (consistência bidirecional);
   - todo nó de conteúdo tem `custT="1"` no `prSet`;
   - todo `dgm:cxn type="presOf"` de uma lane aponta para o **mesmo** `destId`
     compartilhado, com `destOrd` 0..N-1 sem buracos nem repetição (e
     `srcOrd`/`destOrd` do cxn de hierarquia correspondente sincronizados);
   - os 2 `presOf` do próprio nó-raiz/rótulo da lane **sobrevivem intactos**
     (não foram apagados pela remoção dos filhos);
   - a árvore `presParOf` permanece inalterada antes/depois;
   - XML resultante é bem-formado e a parte abre sem erro.
2. **Idempotência:** chamar `_sync_data_nodes` 2x seguidas sobre o mesmo slide
   (mesmos itens ou itens diferentes) e verificar que não sobram `dgm:pt`/
   `dgm:cxn` órfãos — só os nós da última chamada devem existir.
3. **Falha parcial:** forçar uma exceção dentro de `_rebuild_lane_nodes` no
   item N de uma lane com N+1 itens (mock/monkeypatch) e verificar que
   `pkg.set_part` **não foi chamado** e que a parte `data*.xml` resultante é
   **idêntica** (bytes) ao estado anterior à chamada de `_sync_data_nodes` —
   nunca uma mistura de nós antigos/novos.
4. **Mapeamento por texto, não por ordem de documento:** gerar um slide com
   itens **distinguíveis por lane** (ex.: um marcador único tipo
   `"ENTRADA-X"`/`"ATIVIDADE-Y"`/`"SAIDA-Z"` por lane) e confirmar que, no
   `data*.xml` resultante, o texto que ficou sob o nó-raiz rotulado
   "ENTRADAS" é de fato o item da lane esquerda — não um item de outra lane
   que por coincidência ficasse na mesma posição de documento. Este teste
   existe especificamente para o risco de "casar por ordem em vez de por
   texto" identificado na verificação independente.
5. **Regressão:** testes de fumaça existentes (`tests/test_generation.py`)
   continuam passando — geração não pode quebrar.
6. **Render:** pipeline de QA visual (LibreOffice → PDF → PyMuPDF → PNG)
   confirma que o **desenho** (fonte de verdade do render) continua idêntico a
   antes — esta mudança não deve alterar nada visualmente, só o modelo de
   dados por trás.
7. **Limite conhecido, não testável nesta máquina:** o teste real de
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
- Mitigação: tratamento de erro no-op + isolamento transacional (acima)
  garantem que, na pior hipótese, o resultado é idêntico ao comportamento
  atual (render correto, edição degradada) — nunca pior do que hoje, e nunca
  um arquivo corrompido.
- **Achado tangencial (fora de escopo, não é uma ação deste trabalho):**
  `data*.xml` tem um `extLst/dsp:dataModelExt relId="rId7"` que referencia um
  relacionamento do **slide** (não da própria parte de dados), resolvido via
  `_rels` daquele slide. Verificado que `opc.py::clone_slide` preserva os
  valores de `Id` dos relacionamentos ao clonar (não renumera) — hoje esse
  link não quebra. Registrado aqui só para o caso de uma mudança futura em
  `clone_slide` que renumere `rId`s sem atualizar esse valor dentro de
  `data*.xml` — não é algo a corrigir agora.
