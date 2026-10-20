from pathlib import Path
import sys
import html

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.database import adicionar_titulo, listar_titulos
from components.navbar import mostrar_navbar

st.set_page_config(
    page_title="Catálogo | CineTrack",
    page_icon="🎬",
    layout="wide"
)

with open(ROOT / "styles.css", encoding="utf-8") as arquivo:
    st.markdown(
        f"<style>{arquivo.read()}</style>",
        unsafe_allow_html=True
    )

st.markdown("""
<style>
.catalog-card {
    color: #f4f5f7;
}
.catalog-title {
    color: #f4f5f7;
    font-size: 21px;
    font-weight: 800;
    line-height: 1.35;
    margin: 12px 0 8px;
    overflow-wrap: anywhere;
}
.catalog-meta {
    color: #b9a7ff;
    font-size: 13px;
    font-weight: 650;
    margin-bottom: 12px;
}
.catalog-rating {
    color: #f2cf75;
    font-size: 14px;
    font-weight: 750;
    margin-bottom: 12px;
}
.catalog-description {
    color: #aeb6c9;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 12px;
}
.catalog-type {
    display: inline-block;
    background: #29213f;
    border: 1px solid #493b70;
    color: #d5c9ff;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 12px;
}
div[class*="st-key-catalog_card_"] {
    background: linear-gradient(145deg, #191d2a, #11141d);
    border: 1px solid #2c3243;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 20px;
    transition: border-color 0.2s;
}
div[class*="st-key-catalog_card_"]:hover {
    border-color: #8d73ef;
}
div[class*="st-key-catalog_card_"] [data-testid="stImage"] img {
    border-radius: 12px;
}
.catalog-empty {
    text-align: center;
    padding: 36px 20px;
    border: 1px solid #2c3243;
    border-radius: 18px;
    background: linear-gradient(145deg, #191d2a, #11141d);
}
.catalog-empty-icon {
    font-size: 42px;
    margin-bottom: 10px;
}
.catalog-empty h3 {
    color: #f4f5f7;
}
.catalog-empty p {
    color: #aeb6c9;
}
</style>
""", unsafe_allow_html=True)

mostrar_navbar()
st.divider()

API_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"

st.markdown("""
<div class="page-heading">
    <div class="page-eyebrow">DESCUBRA ALGO NOVO</div>
    <h1>Explorar catálogo</h1>
    <p>Encontre filmes e séries para descobrir sua próxima história favorita.</p>
</div>
""", unsafe_allow_html=True)

try:
    api_key = st.secrets["TMDB_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "Chave do TMDB não encontrada em .streamlit/secrets.toml."
    )
    st.stop()

st.markdown(
    '<div class="section-title">Encontre seu próximo título</div>',
    unsafe_allow_html=True
)

col_busca, col_tipo = st.columns([3, 1.2])

with col_busca:
    pesquisa = st.text_input(
        "Buscar filmes e séries",
        placeholder="Ex.: Batman, Breaking Bad, Interestelar...",
        help="Digite o nome de um filme ou série para pesquisar no TMDB."
    )

with col_tipo:
    tipo = st.selectbox(
        "Tipo de conteúdo",
        ["Todos", "Filmes", "Séries"]
    )

col_nota, col_ordenacao = st.columns([1, 2])

with col_nota:
    nota_minima = st.slider(
        "Nota mínima no TMDB",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5
    )

with col_ordenacao:
    ordenacao = st.selectbox(
        "Ordenar resultados por",
        [
            "Mais populares",
            "Melhor avaliação",
            "Ano mais recente",
            "Ano mais antigo",
            "Nome (A–Z)"
        ]
    )

st.caption(
    "Os resultados são fornecidos pelo TMDB. "
    "Use os filtros para encontrar títulos do seu interesse."
)

st.write("")

if pesquisa.strip():
    endpoints = []

    if tipo in ["Todos", "Filmes"]:
        endpoints.append(("Filme", "search/movie"))

    if tipo in ["Todos", "Séries"]:
        endpoints.append(("Série", "search/tv"))

    resultados = []

    with st.spinner("Buscando filmes e séries..."):
        try:
            for categoria, endpoint in endpoints:
                resposta = requests.get(
                    f"{API_URL}/{endpoint}",
                    params={
                        "api_key": api_key,
                        "query": pesquisa.strip(),
                        "language": "pt-BR",
                        "include_adult": "false",
                        "page": 1
                    },
                    timeout=15
                )

                resposta.raise_for_status()

                for titulo in resposta.json().get("results", []):
                    titulo["categoria"] = categoria
                    resultados.append(titulo)

        except requests.RequestException:
            st.error(
                "Não foi possível consultar o TMDB. "
                "Verifique sua conexão e tente novamente."
            )
            st.stop()

    resultados = [
        titulo for titulo in resultados
        if float(titulo.get("vote_average") or 0) >= nota_minima
    ]

    def obter_nome(titulo):
        return (
            titulo.get("title")
            or titulo.get("name")
            or "Sem título"
        )

    def obter_data(titulo):
        return (
            titulo.get("release_date")
            or titulo.get("first_air_date")
            or ""
        )

    def obter_ano(titulo):
        data = obter_data(titulo)
        return int(data[:4]) if data[:4].isdigit() else 0

    if ordenacao == "Mais populares":
        resultados.sort(
            key=lambda titulo: float(titulo.get("popularity") or 0),
            reverse=True
        )
    elif ordenacao == "Melhor avaliação":
        resultados.sort(
            key=lambda titulo: float(titulo.get("vote_average") or 0),
            reverse=True
        )
    elif ordenacao == "Ano mais recente":
        resultados.sort(
            key=obter_ano,
            reverse=True
        )
    elif ordenacao == "Ano mais antigo":
        resultados.sort(
            key=lambda titulo: obter_ano(titulo) or 9999
        )
    elif ordenacao == "Nome (A–Z)":
        resultados.sort(
            key=lambda titulo: obter_nome(titulo).casefold()
        )

    existentes = {
        f"{item['categoria']}_{item.get('tmdb_id', item.get('id'))}"
        for item in listar_titulos()
    }

    st.markdown(
        '<div class="section-title">Resultados da busca</div>',
        unsafe_allow_html=True
    )

    if not resultados:
        st.markdown("""
        <div class="catalog-empty">
            <div class="catalog-empty-icon">🔎</div>
            <h3>Nenhum título encontrado</h3>
            <p>Tente outro nome ou diminua a nota mínima do TMDB.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write(
            f"Encontramos **{len(resultados)}** resultado(s) "
            f"para sua pesquisa."
        )

        for inicio in range(0, len(resultados), 3):
            colunas = st.columns(3, gap="large")

            for coluna, titulo in zip(
                colunas,
                resultados[inicio:inicio + 3]
            ):
                with coluna:
                    nome = obter_nome(titulo)
                    nome_seguro = html.escape(nome)

                    data = obter_data(titulo)
                    ano = data[:4] if data else "Ano desconhecido"

                    nota = float(titulo.get("vote_average") or 0)
                    sinopse = (
                        titulo.get("overview")
                        or "Sinopse indisponível para este título."
                    )

                    sinopse_segura = html.escape(sinopse)
                    poster = titulo.get("poster_path")
                    categoria = titulo["categoria"]
                    chave = f"{categoria}_{titulo['id']}"

                    with st.container(key=f"catalog_card_{chave}"):
                        if poster:
                            st.image(
                                f"{IMAGE_URL}{poster}",
                                use_container_width=True
                            )
                        else:
                            st.markdown("""
                            <div class="catalog-empty">
                                <div class="catalog-empty-icon">🎬</div>
                                <p>Pôster indisponível</p>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown(
                            f'<div class="catalog-type">{html.escape(categoria)}</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="catalog-title">{nome_seguro}</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="catalog-meta">{html.escape(str(ano))}</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="catalog-rating">⭐ {nota:.1f}/10 no TMDB</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="catalog-description">{sinopse_segura}</div>',
                            unsafe_allow_html=True
                        )

                        if chave in existentes:
                            st.button(
                                "✓ Já está na coleção",
                                key=f"adicionado_{chave}",
                                disabled=True,
                                use_container_width=True
                            )
                        elif st.button(
                            "＋ Adicionar à coleção",
                            key=f"adicionar_{chave}",
                            type="primary",
                            use_container_width=True
                        ):
                            adicionar_titulo({
                                "id": titulo["id"],
                                "nome": nome,
                                "categoria": categoria,
                                "ano": ano,
                                "nota": nota,
                                "sinopse": sinopse,
                                "poster": poster,
                                "status": "Quero assistir"
                            })

                            st.success(
                                f"{nome} foi adicionado à sua coleção!"
                            )
                            st.rerun()

else:
    st.markdown("""
    <div class="catalog-empty">
        <div class="catalog-empty-icon">🍿</div>
        <h3>Sua próxima história começa aqui</h3>
        <p>
            Pesquise um filme ou uma série, explore as avaliações
            e adicione os títulos que deseja assistir.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.caption(
    "Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB."
)
