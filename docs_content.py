import streamlit as st


PPT_FONTE = "Diagramas de Escopo_Realizar Auditoria e subprocessos_2026_GSF.pptx"
PPT_SLIDES_REFERENCIA = "slides 2, 3, 4, 6, 8, 10, 12, 14 e 15"


def render_modelo_visual() -> None:
    st.markdown(
        """
        <style>
        .nuati-modelo {
            border: 1px solid #d1d5db;
            border-radius: 14px;
            padding: 16px;
            background: #ffffff;
            margin-bottom: 16px;
        }
        .nuati-faixa {
            border: 1px solid #d1d5db;
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 12px;
            font-weight: 600;
        }
        .nuati-objetivo { background: #fcefd6; }
        .nuati-reguladores { background: #eadbef; }
        .nuati-recursos { background: #d6eaf8; }
        .nuati-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
            margin-bottom: 12px;
        }
        .nuati-coluna {
            border: 1px solid #d1d5db;
            border-radius: 12px;
            min-height: 220px;
            overflow: hidden;
            background: #fff;
        }
        .nuati-coluna h4 {
            margin: 0;
            padding: 10px 12px;
            color: white;
            font-size: 14px;
        }
        .nuati-coluna ul {
            margin: 0;
            padding: 14px 20px 16px 30px;
        }
        .nuati-entradas h4 { background: #4f8a4b; }
        .nuati-atividades h4 { background: #d39c22; }
        .nuati-saidas h4 { background: #cb5b5b; }
        .nuati-eventos {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .nuati-evento {
            border: 1px solid #d1d5db;
            border-radius: 12px;
            padding: 12px 14px;
            background: #ecf0f1;
            font-weight: 600;
        }
        .nuati-subtitulo {
            color: #475569;
            font-size: 13px;
            margin-top: 4px;
            font-weight: 400;
        }
        </style>
        <div class="nuati-modelo">
            <div class="nuati-faixa nuati-objetivo">
                OBJETIVO DO SUBPROCESSO
                <div class="nuati-subtitulo">Estabelecer a estratégia e a programação do trabalho.</div>
            </div>
            <div class="nuati-faixa nuati-reguladores">
                REGULADORES
                <div class="nuati-subtitulo">Normas, legislações, manuais e políticas que condicionam a execução.</div>
            </div>
            <div class="nuati-grid">
                <div class="nuati-coluna nuati-entradas">
                    <h4>ENTRADAS</h4>
                    <ul>
                        <li>Demandas</li>
                        <li>Documentos</li>
                        <li>Informações</li>
                    </ul>
                </div>
                <div class="nuati-coluna nuati-atividades">
                    <h4>ATIVIDADES</h4>
                    <ul>
                        <li>Analisar</li>
                        <li>Planejar</li>
                        <li>Executar</li>
                    </ul>
                </div>
                <div class="nuati-coluna nuati-saidas">
                    <h4>SAÍDAS</h4>
                    <ul>
                        <li>Relatórios</li>
                        <li>Entregas</li>
                        <li>Resultados</li>
                    </ul>
                </div>
            </div>
            <div class="nuati-faixa nuati-recursos">
                RECURSOS DE SUPORTE
                <div class="nuati-subtitulo">Equipes, sistemas, ferramentas, instalações e parceiros de apoio.</div>
            </div>
            <div class="nuati-eventos">
                <div class="nuati-evento">EVENTO DE INÍCIO<div class="nuati-subtitulo">Estímulo que dispara a execução.</div></div>
                <div class="nuati-evento">EVENTO DE FIM<div class="nuati-subtitulo">Resultado que caracteriza a conclusão.</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_documentacao() -> None:
    st.header("Guia do Diagrama de Escopo")
    st.caption(
        f"Fonte principal desta seção: arquivo local `{PPT_FONTE}`, especialmente os {PPT_SLIDES_REFERENCIA}."
    )

    guia_tab, fluxo_tab, fontes_tab = st.tabs(["Método IGOE", "Fluxo do aplicativo", "Fontes e referência"])

    with guia_tab:
        st.subheader("Modelo visual adotado")
        st.write(
            "A imagem abaixo é uma reconstrução visual do modelo usado no aplicativo, baseada no layout e nos elementos do PowerPoint de referência."
        )
        render_modelo_visual()

        st.subheader("O que significa cada campo")
        st.markdown(
            """
            - `Processo`: é o processo principal que está sendo analisado.
            - `Objetivo`: responde para que o processo existe e qual proposta de valor ele entrega.
            - `Evento de início`: é o estímulo ou insumo sem o qual o processo não começa.
            - `Evento de fim`: é o resultado ou estado que caracteriza a conclusão do processo.
            - `Reguladores`: são legislações, normativos, manuais, padrões e políticas que regulam a forma de execução.
            - `Entradas`: são informações, documentos, demandas e insumos usados para produzir as entregas do processo.
            - `Saídas`: são informações, relatórios, produtos, serviços, entregas e resultados produzidos pelo processo.
            - `Recursos de suporte`: são equipes, sistemas, ferramentas, instalações, planilhas e até parceiros que apoiam a execução.
            - `Subprocessos`: são os blocos principais que compõem o processo.
            - `Atividades`: no nível do subprocesso, são as ações executadas para transformar entradas em saídas.
            """
        )

        st.subheader("Leitura do acrônimo IGOE")
        st.markdown(
            """
            - `I`: Entradas
            - `G`: Guias e reguladores
            - `O`: Saídas
            - `E`: Executores e recursos de suporte
            """
        )

    with fluxo_tab:
        st.subheader("O que o aplicativo faz")
        st.markdown(
            """
            O aplicativo transforma uma descrição textual de processo em um diagrama de escopo estruturado e em um arquivo PowerPoint pronto para uso.
            """
        )

        st.subheader("Etapas executadas")
        st.markdown(
            """
            1. Você cola um texto ou envia um arquivo com a descrição do processo.
            2. O app monta um prompt com instruções de extração e injeta o schema JSON esperado.
            3. O modelo de linguagem recebe esse prompt e devolve somente JSON.
            4. O JSON retornado é validado com Pydantic. Se estiver inválido, o app falha de forma explícita.
            5. Com o JSON válido, o app gera uma pré-visualização em Graphviz.
            6. Em seguida, o app monta os slides em PowerPoint com layout fixo inspirado no arquivo de referência.
            7. Por fim, o usuário baixa o `.pptx` final.
            """
        )

        st.subheader("Como o resultado é construído")
        st.markdown(
            """
            - A extração estruturada usa o schema `ScopeDiagram`.
            - O schema separa processo principal, subprocessos e elementos globais.
            - O PowerPoint não usa SmartArt. Ele é desenhado com formas e caixas de texto para ter previsibilidade no código.
            - Reguladores e recursos podem vir do nível global ou do próprio subprocesso, dependendo do conteúdo extraído.
            """
        )

    with fontes_tab:
        st.subheader("Fontes usadas nesta explicação")
        st.markdown(
            f"""
            - Fonte principal: arquivo local `{PPT_FONTE}`.
            - Slides usados como base conceitual: 3, 4, 6, 8, 10 e 12.
            - Slides usados como base de layout: 14 e 15.
            - Nesta versão da aba, o conteúdo explicativo foi extraído apenas do arquivo local. Se no futuro forem adicionadas fontes externas, elas devem ser listadas aqui com link e indicação clara do que veio de cada uma.
            """
        )
