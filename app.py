import json

import streamlit as st

from branding.streamlit_cd import cd_brand
from docs_content import render_documentacao
from economia import etapas_manuais
from input_parser import read_uploaded_file
from llm import LLMResponseError, LLMUnavailableError, extract_scope
from llm_cadeia.painel_streamlit import painel_llm
from ppt import generate_ppt_bytes
from renderer import build_preview_images
from schema import GlobalElements, Process, ScopeDiagram, Subprocess
from tempo_economizado import estimar
from tempo_economizado.painel_streamlit import mostrar_tempo_economizado


# Versão do app: igual à tag da promoção para a main (git tag -a vX.Y.Z). Atualize as duas juntas.
VERSAO_APP = "1.1.0"

cd_brand.configurar_pagina("Gerador de Diagramas de Escopo")


def _render_efficiency_footer(scope: ScopeDiagram) -> None:
    st.markdown("---")
    # Sem tempo da ferramenta (automatico_min=0): mesmo número da conta antiga do app.
    mostrar_tempo_economizado(estimar(etapas_manuais(scope)))


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


cd_brand.cabecalho(
    "Gerador de Diagramas de Escopo (IGOE)",
    "Cole um texto, envie um arquivo ou preencha os campos estruturados para gerar o PowerPoint e a imagem do diagrama.",
)

with st.sidebar:
    st.header("Configuração")
    st.write(
        "A IA tenta, em ordem, os provedores configurados em `Secrets` (LLM local da Câmara, Gemini, Groq, "
        "Cerebras, OpenRouter) até um responder. Para usar a OpenAI paga, informe sua chave em "
        "\"Usar minha própria chave de IA\" › Outro (URL base `https://api.openai.com/v1`)."
    )
    st.write("O aplicativo pode receber texto, Word (`.docx`) e PDF com texto extraível.")
    painel_llm()


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

            try:
                with st.spinner("Extraindo JSON estruturado do diagrama de escopo..."):
                    scope, origem = extract_scope(source_text)
            except LLMResponseError as exc:
                st.error("O modelo retornou uma resposta inválida para o schema definido.")
                st.code(str(exc))
                st.stop()
            except LLMUnavailableError as exc:
                st.error("IA indisponível agora. Tentativas:")
                st.code(str(exc))
                st.stop()
            except Exception as exc:
                st.error("Ocorreu um erro inesperado durante a extração.")
                st.code(str(exc))
                st.stop()

            _store_generated_scope(scope, input_mode)
            st.session_state["generated_origin"] = origem

        else:
            try:
                scope = _build_scope_from_structured_form(int(subprocess_count))
            except ValueError as exc:
                st.error(str(exc))
                st.stop()
            _store_generated_scope(scope, input_mode)
            st.session_state.pop("generated_origin", None)

    generated_scope = _get_generated_scope()
    if generated_scope is not None:
        action_col1, action_col2 = st.columns([1, 5])
        with action_col1:
            if st.button("Limpar resultado"):
                st.session_state.pop("generated_scope", None)
                st.session_state.pop("generated_source_mode", None)
                st.session_state.pop("preview_selection", None)
                st.session_state.pop("generated_origin", None)
                st.rerun()
        with action_col2:
            st.caption("O resultado gerado permanece carregado enquanto você alterna entre subprocessos e downloads.")
            if st.session_state.get("generated_origin"):
                st.caption(f"Extraído por: {st.session_state['generated_origin']}")

        st.subheader("Pré-visualização")
        selected_preview = None
        preview_label = "diagrama"
        try:
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
            st.caption("Prévia aproximada (Graphviz). O PowerPoint para download reproduz o template real.")
        except Exception as exc:  # ex.: Graphviz `dot` ausente — não deve bloquear o download
            st.info(
                "Prévia indisponível (o executável `dot` do Graphviz não foi encontrado). "
                "Isso não afeta o PowerPoint abaixo, que é o entregável real."
            )
            st.caption(f"Detalhe técnico: {exc}")

        col_preview, col_ppt = st.columns(2)
        with col_preview:
            if selected_preview is not None:
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

# Sempre visível (não só depois de gerar): autoria e versão do app.
st.caption(f"Feito por Rodrigo Pinto · Versão {VERSAO_APP}")
# App público: só a marca, sem assinatura de unidade (MIV p.14; F-A10 do framework).
cd_brand.rodape(unidades=())
