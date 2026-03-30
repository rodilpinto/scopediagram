import json

import streamlit as st

from docs_content import render_documentacao
from input_parser import read_uploaded_file
from llm import (
    LLMResponseError,
    extract_scope,
    get_default_model,
    get_default_provider,
    has_configured_api_key,
)
from ppt import generate_ppt_bytes
from renderer import build_preview_images
from schema import GlobalElements, Process, ScopeDiagram, Subprocess


st.set_page_config(page_title="Gerador de Diagramas de Escopo", layout="wide")


def _estimate_time_saved_hours(scope: ScopeDiagram) -> float:
    global_elements = scope.global_elements or GlobalElements()
    input_count = len(global_elements.inputs)
    output_count = len(global_elements.outputs)
    regulator_count = len(global_elements.regulators)
    resource_count = len(global_elements.resources)
    subprocess_count = len(scope.subprocesses)
    activity_count = sum(len(subprocess.activities) for subprocess in scope.subprocesses)

    extraction_time = 0.6 + (input_count + output_count + regulator_count + resource_count) * 0.06
    structuring_time = 0.8 + subprocess_count * 0.35 + activity_count * 0.08
    diagramming_time = 0.9 + subprocess_count * 0.3 + (input_count + output_count) * 0.05
    formatting_time = 0.7 + subprocess_count * 0.2
    review_time = 0.4 + regulator_count * 0.03 + resource_count * 0.03

    return round(extraction_time + structuring_time + diagramming_time + formatting_time + review_time, 1)


def _render_efficiency_footer(scope: ScopeDiagram) -> None:
    saved_hours = _estimate_time_saved_hours(scope)
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.caption("Feito por Rodrigo Pinto")
    with col2:
        st.caption("Versão 1.0")
    with col3:
        st.caption(f"Economia estimada: {saved_hours} horas")

    if st.toggle("Explicar economia de tempo", key="show_time_savings_details"):
        global_elements = scope.global_elements or GlobalElements()
        subprocess_count = len(scope.subprocesses)
        activity_count = sum(len(subprocess.activities) for subprocess in scope.subprocesses)
        st.info(
            "\n".join(
                [
                    f"Estimativa total: {saved_hours} horas economizadas.",
                    "Componentes considerados:",
                    f"- leitura, triagem e extração do texto-base: {round(0.6 + (len(global_elements.inputs) + len(global_elements.outputs) + len(global_elements.regulators) + len(global_elements.resources)) * 0.06, 1)} h",
                    f"- identificação e organização dos componentes estruturados: {round(0.8 + subprocess_count * 0.35 + activity_count * 0.08, 1)} h",
                    f"- diagramação manual do modelo visual: {round(0.9 + subprocess_count * 0.3 + (len(global_elements.inputs) + len(global_elements.outputs)) * 0.05, 1)} h",
                    f"- criação e acabamento do PowerPoint: {round(0.7 + subprocess_count * 0.2, 1)} h",
                    f"- revisão final de reguladores e recursos: {round(0.4 + len(global_elements.regulators) * 0.03 + len(global_elements.resources) * 0.03, 1)} h",
                    "A estimativa cresce conforme o volume de subprocessos, atividades, entradas, saídas, reguladores e recursos.",
                ]
            )
        )


def _split_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _build_scope_from_structured_form(subprocess_count: int) -> ScopeDiagram:
    process = Process(
        name=st.session_state["process_name"],
        objective=st.session_state["process_objective"],
        start_event=st.session_state["process_start_event"],
        end_event=st.session_state["process_end_event"],
    )

    global_elements = GlobalElements(
        inputs=_split_lines(st.session_state["global_inputs"]),
        outputs=_split_lines(st.session_state["global_outputs"]),
        regulators=_split_lines(st.session_state["global_regulators"]),
        resources=_split_lines(st.session_state["global_resources"]),
    )

    subprocesses: list[Subprocess] = []
    for index in range(subprocess_count):
        subprocesses.append(
            Subprocess(
                name=st.session_state[f"subprocess_name_{index}"],
                inputs=_split_lines(st.session_state[f"subprocess_inputs_{index}"]),
                activities=_split_lines(st.session_state[f"subprocess_activities_{index}"]),
                outputs=_split_lines(st.session_state[f"subprocess_outputs_{index}"]),
                regulators=_split_lines(st.session_state[f"subprocess_regulators_{index}"]),
                resources=_split_lines(st.session_state[f"subprocess_resources_{index}"]),
                objective=st.session_state[f"subprocess_objective_{index}"] or None,
                start_event=st.session_state[f"subprocess_start_event_{index}"] or None,
                end_event=st.session_state[f"subprocess_end_event_{index}"] or None,
            )
        )

    if not process.name.strip():
        raise ValueError("Informe o nome do processo.")
    if not process.objective.strip():
        raise ValueError("Informe o objetivo do processo.")
    if not process.start_event.strip():
        raise ValueError("Informe o evento de início do processo.")
    if not process.end_event.strip():
        raise ValueError("Informe o evento de fim do processo.")
    if not subprocesses:
        raise ValueError("Informe pelo menos um subprocesso.")
    if any(not subprocess.name.strip() for subprocess in subprocesses):
        raise ValueError("Todos os subprocessos devem ter nome.")

    return ScopeDiagram(process=process, subprocesses=subprocesses, global_elements=global_elements)


def _store_generated_scope(scope: ScopeDiagram, source_mode: str) -> None:
    st.session_state["generated_scope"] = scope.model_dump()
    st.session_state["generated_source_mode"] = source_mode
    st.session_state["preview_selection"] = "Processo principal"


def _get_generated_scope() -> ScopeDiagram | None:
    data = st.session_state.get("generated_scope")
    if not data:
        return None
    return ScopeDiagram.model_validate(data)


st.title("Gerador de Diagramas de Escopo (IGOE)")
st.caption(
    "Cole um texto, envie um arquivo ou preencha os campos estruturados para gerar o PowerPoint e a imagem do diagrama."
)

with st.sidebar:
    st.header("Configuração")
    st.write(
        "Para deploy público no Streamlit, configure a chave da API em `Secrets`. O provedor padrão deste app é Gemini."
    )
    st.write("O aplicativo pode receber texto, Word (`.docx`) e PDF com texto extraível.")
    provider = st.selectbox(
        "Provedor do modelo",
        options=["gemini", "openai"],
        index=0 if get_default_provider() == "gemini" else 1,
        format_func=lambda value: "Google Gemini" if value == "gemini" else "OpenAI",
    )
    default_model = get_default_model(provider)
    model = st.text_input("Modelo", value=default_model)

    if has_configured_api_key(provider):
        st.success("Chave de API configurada para o provedor selecionado.")
    else:
        if provider == "gemini":
            st.warning("Chave não encontrada. Configure `GEMINI_API_KEY` ou `GOOGLE_API_KEY` em `Secrets`.")
        else:
            st.warning("Chave não encontrada. Configure `OPENAI_API_KEY` em `Secrets`.")


aba_gerador, aba_documentacao = st.tabs(["Gerador", "Guia e documentação"])

with aba_gerador:
    input_mode = st.radio("Tipo de entrada", ["Texto", "Arquivo", "Estruturado"], horizontal=True)

    source_text = ""
    subprocess_count = 1

    if input_mode == "Texto":
        source_text = st.text_area(
            "Cole o conteúdo do processo",
            height=280,
            placeholder="Cole requisitos, entrevistas, anotações, normas, atas ou qualquer descrição do processo aqui.",
        )

    elif input_mode == "Arquivo":
        uploaded_file = st.file_uploader("Envie um arquivo", type=["txt", "md", "csv", "json", "docx", "pdf"])
        st.caption("PDFs escaneados sem OCR podem não gerar texto utilizável.")
        if uploaded_file is not None:
            try:
                source_text = read_uploaded_file(uploaded_file)
            except ValueError as exc:
                st.error(str(exc))
                st.stop()
            st.text_area("Pré-visualização do arquivo", value=source_text, height=280, disabled=True)

    else:
        st.subheader("Processo principal")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Nome do processo", key="process_name")
            st.text_input("Evento de início", key="process_start_event")
        with col2:
            st.text_input("Objetivo do processo", key="process_objective")
            st.text_input("Evento de fim", key="process_end_event")

        st.subheader("Elementos globais")
        col3, col4 = st.columns(2)
        with col3:
            st.text_area("Entradas globais", key="global_inputs", height=130, placeholder="Uma entrada por linha")
            st.text_area("Reguladores globais", key="global_regulators", height=130, placeholder="Um regulador por linha")
        with col4:
            st.text_area("Saídas globais", key="global_outputs", height=130, placeholder="Uma saída por linha")
            st.text_area("Recursos globais", key="global_resources", height=130, placeholder="Um recurso por linha")

        subprocess_count = st.number_input("Quantidade de subprocessos", min_value=1, max_value=12, value=1, step=1)

        for index in range(int(subprocess_count)):
            st.markdown(f"### Subprocesso {index + 1}")
            col5, col6 = st.columns(2)
            with col5:
                st.text_input("Nome", key=f"subprocess_name_{index}")
                st.text_input("Objetivo", key=f"subprocess_objective_{index}")
                st.text_input("Evento de início", key=f"subprocess_start_event_{index}")
                st.text_area(
                    "Entradas",
                    key=f"subprocess_inputs_{index}",
                    height=120,
                    placeholder="Uma entrada por linha",
                )
                st.text_area(
                    "Reguladores",
                    key=f"subprocess_regulators_{index}",
                    height=120,
                    placeholder="Um regulador por linha",
                )
            with col6:
                st.text_input("Evento de fim", key=f"subprocess_end_event_{index}")
                st.text_area(
                    "Atividades",
                    key=f"subprocess_activities_{index}",
                    height=120,
                    placeholder="Uma atividade por linha",
                )
                st.text_area(
                    "Saídas",
                    key=f"subprocess_outputs_{index}",
                    height=120,
                    placeholder="Uma saída por linha",
                )
                st.text_area(
                    "Recursos",
                    key=f"subprocess_resources_{index}",
                    height=120,
                    placeholder="Um recurso por linha",
                )

    if st.button("Gerar", type="primary"):
        if input_mode in {"Texto", "Arquivo"}:
            if not source_text.strip():
                st.error("É obrigatório informar um conteúdo de entrada.")
                st.stop()

            if not has_configured_api_key(provider):
                if provider == "gemini":
                    st.error(
                        "A chave da Gemini não está configurada. Adicione `GEMINI_API_KEY` ou `GOOGLE_API_KEY` em `Secrets` no Streamlit."
                    )
                else:
                    st.error("A chave da OpenAI não está configurada. Adicione `OPENAI_API_KEY` em `Secrets` no Streamlit.")
                st.stop()

            try:
                with st.spinner("Extraindo JSON estruturado do diagrama de escopo..."):
                    scope = extract_scope(source_text, provider=provider, model=model)
            except LLMResponseError as exc:
                st.error("O modelo retornou uma resposta inválida para o schema definido.")
                st.code(str(exc))
                st.stop()
            except RuntimeError as exc:
                st.error(str(exc))
                st.stop()
            except Exception as exc:
                st.error("Ocorreu um erro inesperado durante a extração.")
                st.code(str(exc))
                st.stop()

            _store_generated_scope(scope, input_mode)

        else:
            try:
                scope = _build_scope_from_structured_form(int(subprocess_count))
            except ValueError as exc:
                st.error(str(exc))
                st.stop()
            _store_generated_scope(scope, input_mode)

    generated_scope = _get_generated_scope()
    if generated_scope is not None:
        action_col1, action_col2 = st.columns([1, 5])
        with action_col1:
            if st.button("Limpar resultado"):
                st.session_state.pop("generated_scope", None)
                st.session_state.pop("generated_source_mode", None)
                st.session_state.pop("preview_selection", None)
                st.rerun()
        with action_col2:
            st.caption("O resultado gerado permanece carregado enquanto você alterna entre subprocessos e downloads.")

        st.subheader("Pré-visualização")
        previews = build_preview_images(generated_scope)
        preview_options = [label for label, _ in previews]
        if st.session_state.get("preview_selection") not in preview_options:
            st.session_state["preview_selection"] = preview_options[0]

        preview_label = st.selectbox(
            "Selecione a visualização",
            options=preview_options,
            key="preview_selection",
        )
        selected_preview = next(image for label, image in previews if label == preview_label)
        st.image(selected_preview, use_container_width=True)

        col_preview, col_ppt = st.columns(2)
        with col_preview:
            st.download_button(
                "Baixar PNG da pré-visualização",
                data=selected_preview,
                file_name=f"{preview_label.lower().replace(':', '').replace(' ', '_')}.png",
                mime="image/png",
            )
        with col_ppt:
            ppt_bytes = generate_ppt_bytes(generated_scope)
            st.download_button(
                "Baixar PowerPoint",
                data=ppt_bytes,
                file_name="diagrama_de_escopo.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )

        with st.expander("JSON estruturado", expanded=False):
            json_payload = json.dumps(generated_scope.model_dump(), ensure_ascii=False, indent=2)
            json_col1, json_col2 = st.columns([1, 4])
            with json_col1:
                st.download_button(
                    "Baixar JSON",
                    data=json_payload.encode("utf-8"),
                    file_name="diagrama_de_escopo.json",
                    mime="application/json",
                )
            with json_col2:
                if st.toggle("Mostrar JSON", key="show_json_toggle"):
                    st.code(json_payload, language="json")

        _render_efficiency_footer(generated_scope)

with aba_documentacao:
    render_documentacao()
