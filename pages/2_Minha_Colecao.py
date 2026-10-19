from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.navbar import mostrar_navbar
from services.database import (
    listar_titulos,
    atualizar_status,
    atualizar_nota_pessoal,
    atualizar_favorito,
    remover_titulo
)

st.set_page_config(
    page_title="Minha coleção | CineTrack",
    page_icon="📚",
    layout="wide"
)

with open(ROOT / "styles.css", encoding="utf-8") as arquivo:
    st.markdown(
        f"<style>{arquivo.read()}</style>",
        unsafe_allow_html=True
    )

st.markdown("""
<style>
.collection-card {
    background: linear-gradient(145deg, #191d2a, #11141d);
    border: 1px solid #2c3243;
    border-radius: 18px;
    padding: 22px;
    margin: 10px 0 22px;
    transition: border-color 0.2s, transform 0.2s;
}
.collection-card:hover {
    border-color: #8d73ef;
}
.collection-title {
    color: #f4f5f7;
    font-size: 23px;
    font-weight: 800;
    line-height: 1.3;
    margin-bottom: 8px;
    overflow-wrap: anywhere;
}
.collection-meta {
    color: #b9a7ff;
    font-size: 13px;
    font-weight: 650;
    margin-bottom: 14px;
}
.collection-description {
    color: #aeb6c9;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 16px;
}
.collection-status {
    display: inline-block;
    background: #29213f;
    border: 1px solid #493b70;
    color: #d5c9ff;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 12px;
}
.collection-rating {
    color: #f2cf75;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 12px;
}
.collection-favorite {
    color: #ffd166;
    font-size: 15px;
    font-weight: 750;
    margin-bottom: 10px;
}
div[data-testid="stImage"] img {
    border-radius: 12px;
}
div[data-testid="stSlider"] {
    padding-top: 4px;
}
</style>
""", unsafe_allow_html=True)

mostrar_navbar()
st.divider()

st.markdown("""
<div class="page-heading">
    <div class="page-eyebrow">TUDO NO SEU LUGAR</div>
    <h1>Minha coleção</h1>
    <p>Seus filmes e séries organizados em um só lugar.</p>
</div>
""", unsafe_allow_html=True)

titulos_originais = listar_titulos()

total = len(titulos_originais)
quero_assistir = sum(
    1 for titulo in titulos_originais
    if titulo["status"] == "Quero assistir"
)
assistindo = sum(
    1 for titulo in titulos_originais
    if titulo["status"] == "Assistindo"
)
concluidos = sum(
    1 for titulo in titulos_originais
    if titulo["status"] == "Concluído"
)
favoritos_total = sum(
    1 for titulo in titulos_originais
    if titulo.get("favorito", 0) == 1
)

col1, col2, col3, col4, col5 = st.columns(5)

metricas = [
    (col1, "TÍTULOS", total),
    (col2, "QUERO ASSISTIR", quero_assistir),
    (col3, "ASSISTINDO", assistindo),
    (col4, "CONCLUÍDOS", concluidos),
    (col5, "FAVORITOS ⭐", favoritos_total)
]

for coluna, rotulo, valor in metricas:
    with coluna:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{rotulo}</div>
            <div class="metric-value">{valor}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Sua biblioteca</div>',
    unsafe_allow_html=True
)

col_busca, col_categoria, col_filtro, col_favoritos, col_ordenacao = st.columns(
    [2, 1, 1.2, 1.2, 2]
)

with col_busca:
    busca = st.text_input(
        "Buscar título",
        placeholder="Digite o nome de um filme ou série..."
    )

with col_categoria:
    categoria_selecionada = st.selectbox(
        "Categoria",
        ["Todos", "Filmes", "Séries"]
    )

with col_filtro:
    filtro = st.selectbox(
        "Filtrar por status",
        ["Todos", "Quero assistir", "Assistindo", "Concluído"]
    )

with col_favoritos:
    filtro_favoritos = st.selectbox(
        "Favoritos",
        ["Todos", "Somente favoritos"]
    )

with col_ordenacao:
    ordenacao = st.selectbox(
        "Ordenar por",
        [
            "Adicionados recentemente",
            "Nome (A–Z)",
            "Nome (Z–A)",
            "Ano (mais recente)",
            "Ano (mais antigo)",
            "Nota do TMDB (maior primeiro)",
            "Sua nota pessoal (maior primeiro)"
        ]
    )

titulos = list(titulos_originais)

if categoria_selecionada == "Filmes":
    titulos = [
        titulo for titulo in titulos
        if titulo["categoria"] == "Filme"
    ]
elif categoria_selecionada == "Séries":
    titulos = [
        titulo for titulo in titulos
        if titulo["categoria"] == "Série"
    ]

if filtro != "Todos":
    titulos = [
        titulo for titulo in titulos
        if titulo["status"] == filtro
    ]

if filtro_favoritos == "Somente favoritos":
    titulos = [
        titulo for titulo in titulos
        if titulo.get("favorito", 0) == 1
    ]

if busca.strip():
    termo = busca.strip().casefold()
    titulos = [
        titulo for titulo in titulos
        if termo in (titulo["nome"] or "").casefold()
    ]

if ordenacao == "Adicionados recentemente":
    titulos.sort(
        key=lambda titulo: titulo["id"],
        reverse=True
    )
elif ordenacao == "Nome (A–Z)":
    titulos.sort(
        key=lambda titulo: (titulo["nome"] or "").casefold()
    )
elif ordenacao == "Nome (Z–A)":
    titulos.sort(
        key=lambda titulo: (titulo["nome"] or "").casefold(),
        reverse=True
    )
elif ordenacao == "Ano (mais recente)":
    titulos.sort(
        key=lambda titulo: (
            int(titulo["ano"])
            if str(titulo["ano"] or "").isdigit()
            else 0
        ),
        reverse=True
    )
elif ordenacao == "Ano (mais antigo)":
    titulos.sort(
        key=lambda titulo: (
            int(titulo["ano"])
            if str(titulo["ano"] or "").isdigit()
            else 9999
        )
    )
elif ordenacao == "Nota do TMDB (maior primeiro)":
    titulos.sort(
        key=lambda titulo: float(titulo["nota_tmdb"] or 0),
        reverse=True
    )
elif ordenacao == "Sua nota pessoal (maior primeiro)":
    titulos.sort(
        key=lambda titulo: (
            titulo["nota_pessoal"] is not None,
            float(titulo["nota_pessoal"] or 0)
        ),
        reverse=True
    )

if not titulos:
    if not titulos_originais:
        st.info(
            "Sua coleção ainda está vazia. "
            "Explore o catálogo para adicionar seu primeiro título."
        )
    elif filtro_favoritos == "Somente favoritos":
        st.info(
            "Você ainda não tem favoritos nessa visualização. "
            "Marque títulos com ⭐ para encontrá-los aqui."
        )
    else:
        st.info("Nenhum título encontrado com os filtros selecionados.")
else:
    st.write(f"{len(titulos)} título(s) nesta visualização.")

    for titulo in titulos:
        with st.container():
            st.markdown(
                '<div class="collection-card">',
                unsafe_allow_html=True
            )

            col_poster, col_info = st.columns([1, 3], gap="large")

            with col_poster:
                if titulo["poster"]:
                    st.image(
                        f"https://image.tmdb.org/t/p/w342{titulo['poster']}",
                        use_container_width=True
                    )
                else:
                    st.markdown("🎬 *Pôster indisponível*")

            with col_info:
                favorito_atual = titulo.get("favorito", 0) == 1

                texto_favorito = (
                    "⭐ Remover dos favoritos"
                    if favorito_atual
                    else "☆ Adicionar aos favoritos"
                )

                if st.button(
                    texto_favorito,
                    key=f"favorito_{titulo['id']}",
                    use_container_width=True
                ):
                    atualizar_favorito(
                        titulo["id"],
                        not favorito_atual
                    )
                    st.rerun()

                if favorito_atual:
                    st.markdown(
                        '<div class="collection-favorite">⭐ Está nos seus favoritos</div>',
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f'<div class="collection-status">{titulo["status"]}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="collection-title">{titulo["nome"]}</div>',
                    unsafe_allow_html=True
                )

                ano = titulo["ano"] or "Ano desconhecido"
                categoria = titulo["categoria"] or "Título"
                nota_tmdb = float(titulo["nota_tmdb"] or 0)

                st.markdown(
                    f'<div class="collection-meta">{categoria} · {ano}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="collection-rating">⭐ {nota_tmdb:.1f}/10 no TMDB</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="collection-description">{titulo["sinopse"] or "Sinopse indisponível."}</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    "🔎 Ver detalhes",
                    key=f"detalhes_{titulo['id']}",
                    use_container_width=True
                ):
                    st.session_state["titulo_detalhes"] = titulo["id"]
                    st.switch_page("pages/3_Detalhes.py")

                opcoes = [
                    "Quero assistir",
                    "Assistindo",
                    "Concluído"
                ]

                status_atual = (
                    titulo["status"]
                    if titulo["status"] in opcoes
                    else "Quero assistir"
                )

                novo_status = st.selectbox(
                    "Status",
                    opcoes,
                    index=opcoes.index(status_atual),
                    key=f"status_{titulo['id']}"
                )

                if novo_status != titulo["status"]:
                    atualizar_status(titulo["id"], novo_status)
                    st.rerun()

                nota_atual = titulo["nota_pessoal"]

                if nota_atual is None:
                    nota_atual = 0.0

                nova_nota = st.slider(
                    "Sua nota pessoal",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(nota_atual),
                    step=0.5,
                    key=f"nota_{titulo['id']}"
                )

                if st.button(
                    "Salvar minha nota",
                    key=f"salvar_nota_{titulo['id']}",
                    use_container_width=True
                ):
                    atualizar_nota_pessoal(
                        titulo["id"],
                        nova_nota
                    )
                    st.success("Sua nota foi salva!")
                    st.rerun()

                chave_confirmacao = f"confirmar_remocao_{titulo['id']}"

                if st.button(
                    "🗑️ Remover da coleção",
                    key=f"remover_{titulo['id']}",
                    use_container_width=True
                ):
                    st.session_state[chave_confirmacao] = True
                    st.rerun()

                if st.session_state.get(chave_confirmacao, False):
                    st.warning(
                        f"Tem certeza de que deseja remover "
                        f"'{titulo['nome']}' da sua coleção?"
                    )

                    col_confirmar, col_cancelar = st.columns(2)

                    with col_confirmar:
                        if st.button(
                            "Sim, remover",
                            key=f"confirmar_{titulo['id']}",
                            use_container_width=True
                        ):
                            remover_titulo(titulo["id"])
                            st.session_state.pop(chave_confirmacao, None)
                            st.rerun()

                    with col_cancelar:
                        if st.button(
                            "Cancelar",
                            key=f"cancelar_{titulo['id']}",
                            use_container_width=True
                        ):
                            st.session_state.pop(chave_confirmacao, None)
                            st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

st.caption(
    "Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB."
)
