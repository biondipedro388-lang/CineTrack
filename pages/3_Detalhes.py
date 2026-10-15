from pathlib import Path
import sys

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from components.navbar import mostrar_navbar
from services.database import listar_titulos

st.set_page_config(
    page_title="Detalhes | CineTrack",
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
PROFILE_URL = "https://image.tmdb.org/t/p/w185"

st.markdown("""
<div class="page-heading">
    <div class="page-eyebrow">CONHEÇA CADA HISTÓRIA</div>
    <h1>Detalhes do título</h1>
    <p>Explore informações, trailers, elenco e equipe de produção.</p>
</div>
""", unsafe_allow_html=True)

parametro_id = st.query_params.get("titulo_id")

if parametro_id:
    try:
        st.session_state["titulo_detalhes"] = int(parametro_id)
    except (TypeError, ValueError):
        st.error("O identificador do título é inválido.")
        st.stop()

titulo_id = st.session_state.get("titulo_detalhes")

if titulo_id is None:
    st.warning("Nenhum título foi selecionado.")

    if st.button("Abrir minha coleção"):
        st.switch_page("pages/2_Minha_Colecao.py")

    st.stop()

titulos = listar_titulos()

titulo = next(
    (
        item for item in titulos
        if int(item["id"]) == int(titulo_id)
    ),
    None
)

if titulo is None:
    st.error("Esse título não foi encontrado na sua coleção.")

    if st.button("Voltar à coleção"):
        st.switch_page("pages/2_Minha_Colecao.py")

    st.stop()

try:
    api_key = st.secrets["TMDB_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("Chave do TMDB não encontrada em .streamlit/secrets.toml.")
    st.stop()

categoria_api = "movie" if titulo["categoria"] == "Filme" else "tv"

with st.spinner("Carregando detalhes, vídeos e elenco..."):
    try:
        resposta = requests.get(
            f"{API_URL}/{categoria_api}/{titulo['tmdb_id']}",
            params={
                "api_key": api_key,
                "language": "pt-BR"
            },
            timeout=15
        )
        resposta.raise_for_status()
        detalhes = resposta.json()

        resposta_videos = requests.get(
            f"{API_URL}/{categoria_api}/{titulo['tmdb_id']}/videos",
            params={
                "api_key": api_key,
                "language": "pt-BR"
            },
            timeout=15
        )
        resposta_videos.raise_for_status()
        videos = resposta_videos.json().get("results", [])

        if not videos:
            resposta_videos = requests.get(
                f"{API_URL}/{categoria_api}/{titulo['tmdb_id']}/videos",
                params={
                    "api_key": api_key,
                    "language": "en-US"
                },
                timeout=15
            )
            resposta_videos.raise_for_status()
            videos = resposta_videos.json().get("results", [])

        resposta_elenco = requests.get(
            f"{API_URL}/{categoria_api}/{titulo['tmdb_id']}/credits",
            params={
                "api_key": api_key,
                "language": "pt-BR"
            },
            timeout=15
        )
        resposta_elenco.raise_for_status()
        creditos = resposta_elenco.json()

    except requests.RequestException:
        st.error("Não foi possível carregar as informações do TMDB.")
        st.stop()

col1, col2 = st.columns([1, 2])

with col1:
    if detalhes.get("poster_path"):
        st.image(
            f"{IMAGE_URL}{detalhes['poster_path']}",
            use_container_width=True
        )
    else:
        st.markdown("🎬 Pôster indisponível")

with col2:
    nome = detalhes.get("title") or detalhes.get("name") or titulo["nome"]

    st.header(nome)

    nome_original = (
        detalhes.get("original_title")
        or detalhes.get("original_name")
    )

    if nome_original and nome_original != nome:
        st.caption(f"Título original: {nome_original}")

    generos = [
        genero["name"]
        for genero in detalhes.get("genres", [])
    ]

    if generos:
        st.markdown("**Gêneros:** " + " • ".join(generos))

    data = detalhes.get("release_date") or detalhes.get("first_air_date")

    if data:
        st.markdown(f"**Lançamento:** {data}")

    duracao = detalhes.get("runtime")

    if duracao:
        st.markdown(f"**Duração:** {duracao} minutos")

    temporadas = detalhes.get("number_of_seasons")

    if temporadas:
        st.markdown(f"**Temporadas:** {temporadas}")

    episodios = detalhes.get("number_of_episodes")

    if episodios:
        st.markdown(f"**Episódios:** {episodios}")

    nota_tmdb = detalhes.get("vote_average", 0)
    st.markdown(f"**Nota do TMDB:** ⭐ {nota_tmdb:.1f}/10")
    st.markdown(f"**Seu status:** {titulo['status']}")

    if titulo["nota_pessoal"] is not None:
        st.markdown(
            f"**Sua nota:** ⭐ {titulo['nota_pessoal']:.1f}/10"
        )

    st.markdown("### Sinopse")

    st.write(
        detalhes.get("overview")
        or titulo["sinopse"]
        or "Sinopse indisponível."
    )

st.divider()

st.markdown("### ▶️ Trailers e vídeos")

videos_youtube = [
    video for video in videos
    if video.get("site") == "YouTube"
    and video.get("key")
]

trailers = [
    video for video in videos_youtube
    if video.get("type") == "Trailer"
]

videos_para_exibir = trailers or videos_youtube

if videos_para_exibir:
    video_principal = next(
        (
            video for video in videos_para_exibir
            if video.get("official")
        ),
        videos_para_exibir[0]
    )

    st.video(
        f"https://www.youtube.com/watch?v={video_principal['key']}"
    )
    st.caption(video_principal.get("name", "Trailer"))

    outros_videos = [
        video for video in videos_para_exibir
        if video["key"] != video_principal["key"]
    ]

    if outros_videos:
        opcoes_videos = {
            video.get("name", "Vídeo"): video["key"]
            for video in outros_videos
        }

        video_escolhido = st.selectbox(
            "Outros trailers e vídeos",
            list(opcoes_videos.keys())
        )

        st.video(
            f"https://www.youtube.com/watch?v={opcoes_videos[video_escolhido]}"
        )
else:
    st.info("Nenhum trailer disponível no TMDB para este título.")

st.divider()

st.markdown("### 🎭 Elenco principal")

elenco = creditos.get("cast", [])[:12]

if elenco:
    for inicio in range(0, len(elenco), 4):
        colunas = st.columns(4)

        for coluna, ator in zip(colunas, elenco[inicio:inicio + 4]):
            with coluna:
                if ator.get("profile_path"):
                    st.image(
                        f"{PROFILE_URL}{ator['profile_path']}",
                        use_container_width=True
                    )
                else:
                    st.markdown("👤 Foto indisponível")

                st.markdown(f"**{ator.get('name', 'Nome indisponível')}**")
                st.caption(
                    f"Personagem: {ator.get('character') or 'Não informado'}"
                )
else:
    st.info("Nenhum integrante do elenco encontrado no TMDB.")

st.divider()

st.markdown("### 🎬 Equipe de direção")

diretores = [
    pessoa for pessoa in creditos.get("crew", [])
    if pessoa.get("job") == "Director"
]

if diretores:
    nomes_diretores = list(dict.fromkeys(
        pessoa["name"] for pessoa in diretores
    ))
    st.write(", ".join(nomes_diretores))
else:
    st.info("Informações de direção indisponíveis.")

st.divider()

st.markdown("### Informações adicionais")

if detalhes.get("original_language"):
    st.write(
        f"**Idioma original:** "
        f"{detalhes['original_language'].upper()}"
    )

if detalhes.get("production_countries"):
    paises = [
        pais["name"]
        for pais in detalhes["production_countries"]
    ]
    st.write("**Países:** " + ", ".join(paises))

if detalhes.get("production_companies"):
    produtoras = [
        empresa["name"]
        for empresa in detalhes["production_companies"]
    ]
    st.write("**Produtoras:** " + ", ".join(produtoras))

st.caption(
    "Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB."
)
