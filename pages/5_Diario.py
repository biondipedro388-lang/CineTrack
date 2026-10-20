from datetime import date
from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.navbar import mostrar_navbar
from services.database import (
    listar_titulos,
    listar_diario,
    adicionar_registro_diario,
    remover_registro_diario
)

st.set_page_config(
    page_title="Meu diário | CineTrack",
    page_icon="📔",
    layout="wide"
)


def carregar_css():
    caminho_css = ROOT / "styles.css"

    if caminho_css.exists():
        st.markdown(
            f"<style>{caminho_css.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True
        )


carregar_css()

st.markdown("""
<style>
.diary-card {
    background: linear-gradient(145deg, #191d2a, #11141d);
    border: 1px solid #2c3243;
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
}
.diary-title {
    color: #f4f5f7;
    font-size: 21px;
    font-weight: 800;
    margin-bottom: 6px;
    overflow-wrap: anywhere;
}
.diary-meta {
    color: #b9a7ff;
    font-size: 13px;
    margin-bottom: 10px;
}
.diary-comment {
    color: #d1d5e0;
    font-size: 14px;
    line-height: 1.65;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}
.diary-rating {
    color: #f2cf75;
    font-weight: 750;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

mostrar_navbar()
st.divider()

st.markdown("""
<div class="page-heading">
    <div class="page-eyebrow">SUAS MEMÓRIAS</div>
    <h1>Meu diário</h1>
    <p>Registre o que assistiu, quando assistiu e o que achou.</p>
</div>
""", unsafe_allow_html=True)

titulos = listar_titulos()
registros = listar_diario()

total_registros = len(registros)
total_filmes = len({
    registro["titulo_id"]
    for registro in registros
    if registro["categoria"] == "Filme"
})
total_series = len({
    registro["titulo_id"]
    for registro in registros
    if registro["categoria"] == "Série"
})

col1, col2, col3 = st.columns(3)
col1.metric("Assistidas registradas", total_registros)
col2.metric("Filmes diferentes", total_filmes)
col3.metric("Séries diferentes", total_series)

st.divider()

with st.expander("＋ Registrar algo que assisti", expanded=not registros):
    if not titulos:
        st.info(
            "Sua coleção está vazia. Adicione um filme ou série "
            "pelo catálogo antes de criar um registro."
        )
        if st.button("Explorar catálogo"):
            st.switch_page("pages/1_Catalogo.py")
    else:
        titulos_por_id = {
            titulo["id"]: titulo
            for titulo in titulos
        }

        ids_titulos = list(titulos_por_id.keys())

        def formatar_titulo(titulo_id):
            titulo = titulos_por_id[titulo_id]
            ano = titulo.get("ano") or "Ano desconhecido"
            return f'{titulo["nome"]} ({ano}) · {titulo["categoria"]}'

        with st.form("form_diario", clear_on_submit=True):
            titulo_id = st.selectbox(
                "O que você assistiu?",
                options=ids_titulos,
                format_func=formatar_titulo
            )

            data_assistido = st.date_input(
                "Quando você assistiu?",
                value=date.today(),
                max_value=date.today()
            )

            nota = st.slider(
                "Sua nota",
                min_value=0.0,
                max_value=10.0,
                value=8.0,
                step=0.5
            )

            comentario = st.text_area(
                "Sua opinião",
                placeholder=(
                    "O que achou? Qual foi sua cena favorita? "
                    "Vale a pena assistir de novo?"
                ),
                max_chars=2000
            )

            salvar = st.form_submit_button(
                "Salvar no diário",
                use_container_width=True
            )

            if salvar:
                adicionar_registro_diario(
                    titulo_id=titulo_id,
                    data_assistido=data_assistido.isoformat(),
                    nota=nota,
                    comentario=comentario
                )

                st.success("Registro adicionado ao seu diário!")
                st.rerun()

st.divider()
st.subheader("📚 Histórico de visualizações")

if not registros:
    st.info(
        "Seu diário ainda está vazio. Registre seu primeiro filme "
        "ou episódio/série acima."
    )
else:
    col_busca, col_categoria = st.columns([2, 1])

    with col_busca:
        busca = st.text_input(
            "Buscar no histórico",
            placeholder="Digite o nome de um título..."
        )

    with col_categoria:
        categoria = st.selectbox(
            "Categoria",
            ["Todos", "Filmes", "Séries"]
        )

    registros_filtrados = list(registros)

    if busca.strip():
        termo = busca.strip().casefold()
        registros_filtrados = [
            registro for registro in registros_filtrados
            if termo in (registro["nome"] or "").casefold()
        ]

    if categoria == "Filmes":
        registros_filtrados = [
            registro for registro in registros_filtrados
            if registro["categoria"] == "Filme"
        ]
    elif categoria == "Séries":
        registros_filtrados = [
            registro for registro in registros_filtrados
            if registro["categoria"] == "Série"
        ]

    st.caption(
        f"{len(registros_filtrados)} registro(s) encontrado(s). "
        "Os registros mais recentes aparecem primeiro."
    )

    if not registros_filtrados:
        st.info("Nenhum registro encontrado com esses filtros.")
    else:
        for registro in registros_filtrados:
            with st.container():
                col_poster, col_info = st.columns([1, 4], gap="large")

                with col_poster:
                    if registro["poster"]:
                        st.image(
                            "https://image.tmdb.org/t/p/w342"
                            + registro["poster"],
                            use_container_width=True
                        )
                    else:
                        st.markdown("🎬")

                with col_info:
                    st.markdown(
                        '<div class="diary-card">',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f'<div class="diary-title">{registro["nome"]}</div>',
                        unsafe_allow_html=True
                    )

                    ano = registro["ano"] or "Ano desconhecido"
                    categoria_titulo = registro["categoria"] or "Título"

                    st.markdown(
                        f'<div class="diary-meta">'
                        f'{categoria_titulo} · {ano} · '
                        f'Assistido em {registro["data_assistido"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    if registro["nota"] is not None:
                        st.markdown(
                            f'<div class="diary-rating">'
                            f'⭐ Nota: {float(registro["nota"]):.1f}/10'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    comentario = registro["comentario"] or ""

                    if comentario.strip():
                        st.markdown(
                            '<div class="diary-comment">'
                            + comentario
                            + '</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.caption("Você não adicionou um comentário.")

                    st.markdown("</div>", unsafe_allow_html=True)

                    chave_confirmacao = (
                        f"confirmar_diario_{registro['id']}"
                    )

                    if st.button(
                        "🗑️ Excluir registro",
                        key=f"excluir_diario_{registro['id']}"
                    ):
                        st.session_state[chave_confirmacao] = True
                        st.rerun()

                    if st.session_state.get(chave_confirmacao, False):
                        st.warning(
                            "Deseja realmente excluir este registro "
                            "do diário? O título continuará na coleção."
                        )

                        col_sim, col_nao = st.columns(2)

                        with col_sim:
                            if st.button(
                                "Sim, excluir",
                                key=f"sim_diario_{registro['id']}"
                            ):
                                remover_registro_diario(registro["id"])
                                st.session_state.pop(
                                    chave_confirmacao,
                                    None
                                )
                                st.rerun()

                        with col_nao:
                            if st.button(
                                "Cancelar",
                                key=f"nao_diario_{registro['id']}"
                            ):
                                st.session_state.pop(
                                    chave_confirmacao,
                                    None
                                )
                                st.rerun()

st.caption(
    "Este produto utiliza a API do TMDB, mas não é endossado "
    "nem certificado pelo TMDB."
)
