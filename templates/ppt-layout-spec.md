# Especificação de Layout do PPT

Este arquivo registra o padrão estável de layout derivado do PowerPoint de referência:
`Diagramas de Escopo_Realizar Auditoria e subprocessos_2026_GSF.pptx`

## Tipos de slide

### 1. Capa

- Título centralizado
- Nome do processo em caixa alta
- Resumo do objetivo abaixo

### 2. Slide do processo

- Título na área superior direita
- Faixa `OBJETIVO DO PROCESSO`
- Faixa `REGULADORES` ocupando toda a largura
- Área central com três colunas:
  - `ENTRADAS`
  - `SUBPROCESSOS`
  - `SAÍDAS`
- Faixa `RECURSOS DE SUPORTE` próxima da base
- Caixas de rodapé:
  - `EVENTO DE INÍCIO`
  - `EVENTO DE FIM`

### 3. Slide do subprocesso

- Título na área superior direita
- Faixa `OBJETIVO DO SUBPROCESSO`
- Faixa `REGULADORES` ocupando toda a largura
- Área central com três colunas:
  - `ENTRADAS`
  - `ATIVIDADES`
  - `SAÍDAS`
- Faixa `RECURSOS DE SUPORTE` próxima da base
- Caixas de rodapé:
  - `EVENTO DE INÍCIO`
  - `EVENTO DE FIM`

## Regra de implementação

Todos os slides finais de negócio devem ser gerados com formas e caixas de texto comuns, sem SmartArt.

## Motivo

- `python-pptx` consegue criar formas previsíveis
- a edição de SmartArt não é confiável para este fluxo
- coordenadas fixas são mais fáceis de calibrar contra o arquivo de referência
