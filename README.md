# Scope Diagram AI

Aplicação em Streamlit que extrai dados estruturados no modelo IGOE a partir de texto, valida com Pydantic e exporta um PowerPoint com diagrama de escopo alinhado ao arquivo de referência.

## Arquivos do projeto

- `app.py`: interface Streamlit
- `schema.py`: modelos Pydantic do processo e dos subprocessos
- `llm.py`: integração com Gemini/OpenAI e extração estruturada
- `renderer.py`: geração da pré-visualização em PNG
- `ppt.py`: composição dos slides em PowerPoint
- `input_parser.py`: leitura de arquivos `.txt`, `.docx` e `.pdf`
- `docs_content.py`: conteúdo da aba de documentação do aplicativo
- `prompts/extraction.txt`: prompt de extração em JSON
- `templates/ppt-layout-spec.md`: especificação visual derivada do PowerPoint de referência
- `templates/reference-workflow.md`: instruções para manutenção do layout
- `packages.txt`: dependência de sistema para o Graphviz no Streamlit Cloud
- `.streamlit/secrets.toml.example`: exemplo de configuração de segredos

## Como executar localmente

1. Instale as dependências Python:
   `pip install -r requirements.txt`
2. Instale o Graphviz no sistema operacional e garanta que o executável `dot` esteja no `PATH`
3. Defina uma chave de API:
   - Gemini: `GEMINI_API_KEY`
   - OpenAI: `OPENAI_API_KEY`
4. Opcionalmente, defina:
   - `LLM_PROVIDER=gemini` ou `LLM_PROVIDER=openai`
   - `GEMINI_MODEL=gemini-2.5-flash`
   - `OPENAI_MODEL=gpt-5-mini`
5. Execute:
   `python -m streamlit run app.py`

## Como fazer deploy no Streamlit Community Cloud

1. Suba o projeto para um repositório no GitHub.
2. No Streamlit Community Cloud, crie um novo app apontando para esse repositório.
3. Defina o arquivo principal como `app.py`.
4. Em `Secrets`, configure a chave da API. Exemplo para Gemini:

```toml
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "SUA_CHAVE_AQUI"
GEMINI_MODEL = "gemini-2.5-flash"
```

5. O `packages.txt` já instrui o Streamlit a instalar o Graphviz no servidor.

## Comportamento atual

- Aceita texto colado, arquivo e entrada estruturada
- Lê arquivos `.txt`, `.md`, `.csv`, `.json`, `.docx` e `.pdf`
- Extrai JSON estruturado com Gemini ou OpenAI
- Valida contra o schema `ScopeDiagram`
- Exibe uma prévia em PNG
- Exporta um PowerPoint com:
  - capa
  - slide do processo principal
  - um slide por subprocesso

## Observação de arquitetura

O exportador de PowerPoint é orientado por layout. Ele não depende de SmartArt, porque o `python-pptx` não é confiável para gerar ou editar SmartArt programaticamente. O PowerPoint de referência é tratado como especificação visual, e o código recria essa estrutura com formas e caixas de texto comuns.
