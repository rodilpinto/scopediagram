import json
from pathlib import Path

from pydantic import ValidationError

from llm_cadeia import gerar
from schema import ScopeDiagram, scope_diagram_json_schema


PROMPT_PATH = Path(__file__).parent / "prompts" / "extraction.txt"

# O schema tem listas por subprocesso; com 12 subprocessos o JSON passa fácil de 4K tokens.
MAX_TOKENS = 16384


class LLMResponseError(RuntimeError):
    pass


class LLMUnavailableError(RuntimeError):
    pass


def _load_prompt(text: str) -> str:
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    schema = json.dumps(scope_diagram_json_schema(), indent=2, ensure_ascii=False)
    return prompt_template.replace("{schema}", schema).replace("{input}", text)


def extract_scope(text: str) -> tuple[ScopeDiagram, str]:
    """Extrai o ScopeDiagram via llm_cadeia. Devolve (diagrama, origem "provedor (modelo)").

    Quem responde é decidido pela cadeia (local → gemini → ... ; ver llm_cadeia/README.md).
    O prompt já pede "APENAS JSON válido" e traz o schema; json=True faz o Gemini devolver
    JSON puro e retira a cerca ```json dos demais. A validação continua sendo o pydantic.
    """
    resposta = gerar(_load_prompt(text), json=True, max_tokens=MAX_TOKENS)

    if resposta.texto is None:
        if resposta.origem:
            raise LLMResponseError(f"O modelo {resposta.origem} retornou uma resposta vazia.")
        detalhes = "\n".join(resposta.tentativas) or "Nenhum provedor de IA configurado (veja `llm_cadeia/README.md`)."
        raise LLMUnavailableError(f"Nenhum provedor de IA respondeu.\n\n{detalhes}")

    content = resposta.texto
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(
            f"O modelo {resposta.origem} não retornou JSON válido.\n\nSaída bruta:\n{content}"
        ) from exc

    try:
        return ScopeDiagram.model_validate(data), resposta.origem
    except ValidationError as exc:
        raise LLMResponseError(
            f"O modelo {resposta.origem} retornou JSON inválido para o schema.\n\n{exc}\n\nSaída bruta:\n{content}"
        ) from exc
