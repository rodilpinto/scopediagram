# Scope Diagram AI

Aplicação em Streamlit que extrai dados estruturados no modelo IGOE a partir de texto, valida com Pydantic e exporta um PowerPoint com diagrama de escopo alinhado ao arquivo de referência.

## Arquivos do projeto

- `app.py`: interface Streamlit
- `schema.py`: modelos Pydantic do processo e dos subprocessos
- `llm.py`: extração estruturada (prompt + validação pydantic) via `llm_cadeia`
- `llm_cadeia/`, `pptx_opc/`, `tempo_economizado/`, `branding/`: pastas copiadas do `nuati-framework` (LLM com
  fallback; pacote OPC do `.pptx` e render no PowerPoint; tempo economizado; identidade visual). Não edite as cópias:
  melhoria e defeito vão para o framework (ver o README de cada pasta)
- `templatefill/`: preenche o template real (SmartArt) do PowerPoint (`builder.py`, `igoe.py`)
- `economia.py`: etapas do trabalho manual para o tempo economizado
- `renderer.py`: geração da pré-visualização em PNG
- `ppt.py`: ponto de entrada da geração do PowerPoint (usa `templatefill/`; `ppt_legacy.py` é o gerador antigo)
- `input_parser.py`: leitura de arquivos `.txt`, `.docx` e `.pdf`
- `docs_content.py`: conteúdo da aba de documentação do aplicativo
- `prompts/extraction.txt`: prompt de extração em JSON
- `templates/ppt-layout-spec.md`: especificação visual derivada do PowerPoint de referência
- `templates/reference-workflow.md`: instruções para manutenção do layout
- `packages.txt`: dependência de sistema para o Graphviz no Streamlit Cloud
- `.streamlit/secrets.toml.example`: exemplo de configuração de segredos
- `.streamlit/config.toml`: tema da identidade visual (do `branding/`)

## Como executar localmente

1. Instale as dependências Python:
   `pip install -r requirements.txt`
2. Instale o Graphviz no sistema operacional e garanta que o executável `dot` esteja no `PATH`
3. Configure os segredos em `.streamlit/secrets.toml` (ou em `~/.streamlit/secrets.toml`, fora do repo),
   com os nomes de `.streamlit/secrets.toml.example`. Na rede da Câmara, inclua `LLM_BASE_URL` e
   `LLM_MODEL` para usar o Gemma local; os demais provedores entram como fallback.
4. Diagnóstico opcional (1 requisição por modelo): `python -m llm_cadeia`
5. Execute:
   `python -m streamlit run app.py`

## Ambientes e deploy (Streamlit Community Cloud)

| Branch | Papel | App |
|---|---|---|
| `main` | produção (padrão no GitHub) | `diagrama-escopo.streamlit.app` |
| `homologacao` | trabalho do dia a dia | `diagrama-escopo-homologacao.streamlit.app` |

- Push na branch atualiza o app dela sozinho. Os dois remotos (`github` e o interno `origin`) recebem os mesmos
  commits; o Streamlit lê só o GitHub.
- Promover (com o ok do Rodrigo): trocar `VERSAO_APP` em `app.py` em `homologacao`, conferir no ar, depois
  `git switch main && git merge --ff-only homologacao`, `git tag -a vX.Y.Z -m "..."` com o mesmo número, push de
  `main` e da tag nos dois remotos.
- Secrets: as chaves gratuitas (nomes em `.streamlit/secrets.toml.example`); na nuvem, sem `LLM_BASE_URL`. Depois de
  mudar Secrets, **Reboot app**. A OpenAI paga não é configurada no app: o usuário informa a própria chave em
  "Usar minha própria chave de IA" › Outro (URL base `https://api.openai.com/v1`).
- O `packages.txt` instala o Graphviz no servidor. O Streamlit não troca a branch de um app: é apagar e recriar.

## Comportamento atual

- Aceita texto colado, arquivo e entrada estruturada
- Lê arquivos `.txt`, `.md`, `.csv`, `.json`, `.docx` e `.pdf`
- Extrai JSON estruturado com a cadeia `llm_cadeia` (LLM local da Câmara, Gemini, Groq, Cerebras, OpenRouter, ou a chave do próprio usuário); a barra lateral mostra quem respondeu
- Valida contra o schema `ScopeDiagram`
- Exibe uma prévia em PNG
- Mostra o tempo de trabalho manual poupado (com a conta num dropdown) e, no rodapé, a versão do app
- Exporta um PowerPoint com:
  - capa
  - slide do processo principal
  - um slide por subprocesso

## Observação de arquitetura

O PowerPoint é gerado preenchendo o template real de referência, que usa SmartArt. Como o `python-pptx` não edita
SmartArt, o `templatefill/` mexe no XML do pacote (via `pptx_opc`) e mantém o desenho em cache e o modelo de dados do
SmartArt coerentes. QA visual fiel: `python -m pptx_opc.render_powerpoint <arquivo.pptx> <pasta>` (PowerPoint real,
só Windows). O gerador antigo, com formas comuns, continua em `ppt_legacy.py`.
