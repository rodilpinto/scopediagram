import json
import os
from pathlib import Path

from google import genai
from openai import OpenAI
from pydantic import ValidationError

from schema import ScopeDiagram, scope_diagram_json_schema


PROMPT_PATH = Path(__file__).parent / "prompts" / "extraction.txt"
DEFAULT_PROVIDER = "gemini"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_OPENAI_MODEL = "gpt-5-mini"


class LLMResponseError(RuntimeError):
    pass


def _read_secret(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        secret_value = st.secrets.get(name)
        if secret_value:
            return str(secret_value)
    except Exception:
        return None

    return None


def has_configured_api_key(provider: str) -> bool:
    provider_name = provider.lower()
    if provider_name == "openai":
        return bool(_read_secret("OPENAI_API_KEY"))
    if provider_name == "gemini":
        return bool(_read_secret("GEMINI_API_KEY") or _read_secret("GOOGLE_API_KEY"))
    return False


def _load_prompt(text: str) -> str:
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    schema = json.dumps(scope_diagram_json_schema(), indent=2, ensure_ascii=False)
    return prompt_template.replace("{schema}", schema).replace("{input}", text)


def _extract_with_gemini(text: str, model: str) -> ScopeDiagram:
    api_key = _read_secret("GEMINI_API_KEY") or _read_secret("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "A chave da Gemini não foi configurada. Defina `GEMINI_API_KEY` ou `GOOGLE_API_KEY` nas variáveis de ambiente ou em `st.secrets`."
        )

    client = genai.Client(api_key=api_key)
    prompt = _load_prompt(text)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": scope_diagram_json_schema(),
        },
    )

    content = getattr(response, "text", None)
    if not content:
        raise LLMResponseError("O modelo Gemini retornou uma resposta vazia.")

    try:
        return ScopeDiagram.model_validate_json(content)
    except ValidationError as exc:
        raise LLMResponseError(
            f"O modelo Gemini retornou JSON inválido para o schema.\n\n{exc}\n\nSaída bruta:\n{content}"
        ) from exc


def _extract_with_openai(text: str, model: str) -> ScopeDiagram:
    api_key = _read_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "A chave da OpenAI não foi configurada. Defina `OPENAI_API_KEY` nas variáveis de ambiente ou em `st.secrets`."
        )

    prompt = _load_prompt(text)
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content
    if not content:
        raise LLMResponseError("O modelo OpenAI retornou uma resposta vazia.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(
            f"O modelo OpenAI não retornou JSON válido.\n\nSaída bruta:\n{content}"
        ) from exc

    try:
        return ScopeDiagram.model_validate(data)
    except ValidationError as exc:
        raise LLMResponseError(
            f"O modelo OpenAI retornou JSON inválido para o schema.\n\n{exc}\n\nSaída bruta:\n{content}"
        ) from exc


def get_default_provider() -> str:
    return (_read_secret("LLM_PROVIDER") or os.getenv("LLM_PROVIDER") or DEFAULT_PROVIDER).lower()


def get_default_model(provider: str) -> str:
    if provider == "openai":
        return _read_secret("OPENAI_MODEL") or os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL
    return _read_secret("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL


def extract_scope(text: str, provider: str | None = None, model: str | None = None) -> ScopeDiagram:
    provider_name = (provider or get_default_provider()).lower()
    model_name = model or get_default_model(provider_name)

    if provider_name == "openai":
        return _extract_with_openai(text, model_name)
    if provider_name == "gemini":
        return _extract_with_gemini(text, model_name)
    raise RuntimeError("Provedor de LLM inválido. Use `gemini` ou `openai`.")
