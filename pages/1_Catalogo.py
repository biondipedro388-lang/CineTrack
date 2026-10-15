from pathlib import Path
import sys

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
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
    st.error("Chave do TMDB não encontrada em .streamlit/secrets.toml.")
    st.stop()

tipo = st.selectbox(
    "Tipo de conteúdo",
    ["Todos", "Filmes", "Séries"]
)

pesquisa = st.text_input(
    "Nome do filme ou série",
    placeholder="Ex.: Batman, Breaking Bad, Interestelar..."
)

if pesquisa.strip():
    endpoints = []

    if tipo in ["Todos", "Filmes"]:
        endpoints.append(("Filme", "search/movie"))

    if tipo in ["Todos", "Séries"]:
        endpoints.append(("Série", "search/tv"))

    resultados = []

    with st.spinner("Buscando títulos..."):
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

    resultados.sort(
        key=lambda item: item.get("popularity", 0),
        reverse=True
    )

    if not resultados:
        st.warning("Nenhum título encontrado. Tente outro nome.")
    else:
        existentes = {
            f"{item['categoria']}_{item['tmdb_id']}"
            for item in listar_titulos()
        }

        st.write(f"Resultados encontrados: {len(resultados)}")

        for inicio in range(0, len(resultados), 3):
            colunas = st.columns(3)

            for coluna, titulo in zip(
                colunas,
                resultados[inicio:inicio + 3]
            ):
                with coluna:
                    nome = (
                        titulo.get("title")
                        or titulo.get("name")
                        or "Sem título"
                    )

                    data = (
                        titulo.get("release_date")
                        or titulo.get("first_air_date")
                        or ""
                    )

                    ano = data[:4] if data else "Ano desconhecido"
                    nota = titulo.get("vote_average", 0)
                    sinopse = (
                        titulo.get("overview")
                        or "Sinopse indisponível."
                    )
                    poster = titulo.get("poster_path")

                    chave = f"{titulo['categoria']}_{titulo['id']}"

                    if poster:
                        st.image(
                            f"{IMAGE_URL}{poster}",
                            width=220
                        )
                    else:
                        st.markdown("🎬 *Pôster indisponível*")

                    st.subheader(nome)

                    st.caption(
                        f"{titulo['categoria']} • {ano} • ⭐ {nota:.1f}/10"
                    )

                    st.write(sinopse)

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
                        use_container_width=True
                    ):
                        adicionar_titulo({
                            "id": titulo["id"],
                            "nome": nome,
                            "categoria": titulo["categoria"],
                            "ano": ano,
                            "nota": nota,
                            "sinopse": sinopse,
                            "poster": poster,
                            "status": "Quero assistir"
                        })

                        st.success(f"{nome} foi salvo na coleção!")
                        st.rerun()

                    st.divider()

else:
    st.markdown("""
    <div class="movie-card">
        <div class="movie-icon">🍿</div>
        <h3>Encontre seu próximo título</h3>
        <p>Digite um nome acima para pesquisar no catálogo do TMDB.</p>
    </div>
    """, unsafe_allow_html=True)

st.caption(
    "Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB."
)
