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

API_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_URL = "https://image.tmdb.org/t/p/w1280"
PROFILE_URL = "https://image.tmdb.org/t/p/w185"

st.markdown("""
<style>
.detalhes-eyebrow {
    color: #8b8bff;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 3px;
    margin-bottom: 8px;
}
.detalhes-subtitulo {
    color: #a5a5b5;
    font-size: 1rem;
    margin-top: -8px;
    margin-bottom: 24px;
}
.detalhes-chip {
    display: inline-block;
    padding: 6px 11px;
    margin: 3px 5px 3px 0;
    border: 1px solid rgba(150, 150, 180, 0.25);
    border-radius: 20px;
    font-size: 0.8rem;
}
.detalhes-nota {
    padding: 15px;
    border: 1px solid rgba(150, 150, 180, 0.25);
    border-radius: 12px;
    margin: 10px 0;
}
.detalhes-nota-label {
    color: #a5a5b5;
    font-size: 0.8rem;
}
.detalhes-nota-valor {
    font-size: 1.5rem;
    font-weight: 800;
    margin-top: 3px;
}
.detalhes-secao {
    font-size: 1.35rem;
    font-weight: 750;
    margin: 12px 0 18px;
}
.detalhes-personagem {
    color: #a5a5b5;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-heading">
    <div class="detalhes-eyebrow">CINETRACK ORIGINAL</div>
    <h1>Detalhes do título</h1>
    <p class="detalhes-subtitulo">
        Explore histórias, trailers, elenco e bastidores das suas produções favoritas.
    </p>
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
    st.info("Selecione um título da sua coleção para consultar os detalhes.")

    if st.button("Abrir minha coleção", type="primary"):
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

    if st.button("Voltar à coleção", type="primary"):
        st.switch_page("pages/2_Minha_Colecao.py")

    st.stop()

try:
    api_key = st.secrets["TMDB_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "Chave do TMDB não encontrada. "
        "Confira o arquivo .streamlit/secrets.toml."
    )
    st.stop()

categoria_api = "movie" if titulo["categoria"] == "Filme" else "tv"
tmdb_id = titulo.get("tmdb_id")

if not tmdb_id:
    st.error("Este título não possui um identificador do TMDB.")
    st.stop()

with st.spinner("Preparando as informações do título..."):
    try:
        resposta = requests.get(
            f"{API_URL}/{categoria_api}/{tmdb_id}",
            params={
                "api_key": api_key,
                "language": "pt-BR"
            },
            timeout=15
        )
        resposta.raise_for_status()
        detalhes = resposta.json()

        resposta_videos = requests.get(
            f"{API_URL}/{categoria_api}/{tmdb_id}/videos",
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
                f"{API_URL}/{categoria_api}/{tmdb_id}/videos",
                params={
                    "api_key": api_key,
                    "language": "en-US"
                },
                timeout=15
            )
            resposta_videos.raise_for_status()
            videos = resposta_videos.json().get("results", [])

        resposta_elenco = requests.get(
            f"{API_URL}/{categoria_api}/{tmdb_id}/credits",
            params={
                "api_key": api_key,
                "language": "pt-BR"
            },
            timeout=15
        )
        resposta_elenco.raise_for_status()
        creditos = resposta_elenco.json()

    except requests.RequestException:
        st.error(
            "Não foi possível carregar as informações do TMDB. "
            "Confira sua conexão e tente novamente."
        )
        st.button(
            "Recarregar página",
            on_click=st.rerun
        )
        st.stop()

nome = (
    titulo.get("nome")
    or detalhes.get("title")
    or detalhes.get("name")
    or "Título sem nome"
)

nome_original = (
    detalhes.get("original_title")
    or detalhes.get("original_name")
)

data_lancamento = (
    detalhes.get("release_date")
    or detalhes.get("first_air_date")
    or ""
)

ano = titulo.get("ano") or (
    data_lancamento[:4] if data_lancamento else "Não informado"
)

generos = [
    genero.get("name")
    for genero in detalhes.get("genres", [])
    if genero.get("name")
]

nota_tmdb = float(detalhes.get("vote_average") or 0)
total_votos = detalhes.get("vote_count") or 0
sinopse = (
    titulo.get("sinopse")
    or detalhes.get("overview")
    or "Sinopse indisponível para este título."
)

duracao = detalhes.get("runtime")
temporadas = detalhes.get("number_of_seasons")
episodios = detalhes.get("number_of_episodes")
poster = detalhes.get("poster_path")
backdrop = detalhes.get("backdrop_path")

url_tmdb = f"https://www.themoviedb.org/{categoria_api}/{tmdb_id}"

if backdrop:
    st.image(
        f"{BACKDROP_URL}{backdrop}",
        use_container_width=True
    )

st.write("")

col_poster, col_info = st.columns([1, 2.15], gap="large")

with col_poster:
    if poster:
        st.image(
            f"{IMAGE_URL}{poster}",
            use_container_width=True
        )
    else:
        st.markdown("### 🎬")
        st.info("Pôster indisponível.")

    st.markdown(
        f'<div class="detalhes-nota">'
        f'<div class="detalhes-nota-label">NOTA DO TMDB</div>'
        f'<div class="detalhes-nota-valor">⭐ {nota_tmdb:.1f}<span style="font-size:0.9rem;font-weight:400">/10</span></div>'
        f'<div class="detalhes-nota-label">{total_votos:,} avaliações'.replace(",", ".")
        + "</div></div>",
        unsafe_allow_html=True
    )

    if titulo.get("nota_pessoal") is not None:
        nota_pessoal = float(titulo["nota_pessoal"])

        st.markdown(
            f'<div class="detalhes-nota">'
            f'<div class="detalhes-nota-label">SUA AVALIAÇÃO</div>'
            f'<div class="detalhes-nota-valor">⭐ {nota_pessoal:.1f}<span style="font-size:0.9rem;font-weight:400">/10</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.link_button(
        "Ver no TMDB ↗",
        url_tmdb,
        use_container_width=True
    )

with col_info:
    st.markdown(f"# {nome}")

    if nome_original and nome_original != nome:
        st.caption(f"Título original: {nome_original}")

    chips = [
        f'<span class="detalhes-chip">{titulo.get("categoria", "Título")}</span>',
        f'<span class="detalhes-chip">📅 {ano}</span>',
        f'<span class="detalhes-chip">📌 {titulo.get("status", "Sem status")}</span>'
    ]

    st.markdown(
        "".join(chips),
        unsafe_allow_html=True
    )

    if generos:
        st.markdown("**Gêneros**")
        st.markdown(
            "".join(
                f'<span class="detalhes-chip">{genero}</span>'
                for genero in generos
            ),
            unsafe_allow_html=True
        )

    st.markdown("### Sinopse")
    st.write(sinopse)

    if duracao:
        st.markdown(f"**Duração:** {duracao} minutos")

    if temporadas:
        st.markdown(f"**Temporadas:** {temporadas}")

    if episodios:
        st.markdown(f"**Episódios:** {episodios}")

    if data_lancamento:
        st.markdown(f"**Data de lançamento:** {data_lancamento}")

    situacao = detalhes.get("status")
    if situacao:
        st.markdown(f"**Situação da produção:** {situacao}")

    idioma = detalhes.get("original_language")
    if idioma:
        st.markdown(f"**Idioma original:** {idioma.upper()}")

st.divider()

st.markdown(
    '<div class="detalhes-secao">▶️ Trailers e vídeos</div>',
    unsafe_allow_html=True
)

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

    col_video, col_lista = st.columns([2, 1], gap="large")

    with col_video:
        st.video(
            f"https://www.youtube.com/watch?v={video_principal['key']}"
        )
        st.caption(video_principal.get("name", "Vídeo principal"))

    outros_videos = [
        video for video in videos_para_exibir
        if video["key"] != video_principal["key"]
    ]

    with col_lista:
        if outros_videos:
            st.markdown("#### Mais vídeos")

            opcoes_videos = {
                f"{video.get('name', 'Vídeo')} · {video.get('type', 'Extra')}": video["key"]
                for video in outros_videos
            }

            video_escolhido = st.selectbox(
                "Escolha um vídeo",
                list(opcoes_videos.keys()),
                label_visibility="collapsed"
            )

            st.video(
                f"https://www.youtube.com/watch?v={opcoes_videos[video_escolhido]}"
            )
        else:
            st.info("Não há outros vídeos disponíveis.")

else:
    st.info("Nenhum trailer disponível no TMDB para este título.")

st.divider()

st.markdown(
    '<div class="detalhes-secao">🎭 Elenco principal</div>',
    unsafe_allow_html=True
)

elenco = creditos.get("cast", [])[:12]

if elenco:
    for inicio in range(0, len(elenco), 4):
        colunas = st.columns(4, gap="medium")

        for coluna, ator in zip(colunas, elenco[inicio:inicio + 4]):
            with coluna:
                if ator.get("profile_path"):
                    st.image(
                        f"{PROFILE_URL}{ator['profile_path']}",
                        use_container_width=True
                    )
                else:
                    st.markdown("👤")
                    st.caption("Foto indisponível")

                st.markdown(
                    f"**{ator.get('name') or 'Nome indisponível'}**"
                )
                st.markdown(
                    f'<div class="detalhes-personagem">'
                    f'{ator.get("character") or "Personagem não informado"}'
                    f'</div>',
                    unsafe_allow_html=True
                )
else:
    st.info("Nenhum integrante do elenco encontrado no TMDB.")

st.divider()

st.markdown(
    '<div class="detalhes-secao">🎬 Direção e criação</div>',
    unsafe_allow_html=True
)

equipe = creditos.get("crew", [])

diretores = [
    pessoa for pessoa in equipe
    if pessoa.get("job") == "Director" and pessoa.get("name")
]

nomes_diretores = list(dict.fromkeys(
    pessoa["name"] for pessoa in diretores
))

if categoria_api == "tv":
    criadores = [
        pessoa.get("name")
        for pessoa in detalhes.get("created_by", [])
        if pessoa.get("name")
    ]

    if criadores:
        st.markdown("**Criadores:** " + ", ".join(criadores))

if nomes_diretores:
    st.markdown("**Direção:** " + ", ".join(nomes_diretores))
elif categoria_api == "movie":
    st.info("Informações de direção indisponíveis.")

if not nomes_diretores and categoria_api == "tv":
    st.info("Informações de direção indisponíveis para esta série.")

st.divider()

st.markdown(
    '<div class="detalhes-secao">🏢 Informações da produção</div>',
    unsafe_allow_html=True
)

col_prod1, col_prod2 = st.columns(2)

with col_prod1:
    paises = [
        pais.get("name")
        for pais in detalhes.get("production_countries", [])
        if pais.get("name")
    ]

    if paises:
        st.markdown("**Países de produção**")
        st.write(", ".join(paises))

    redes = [
        rede.get("name")
        for rede in detalhes.get("networks", [])
        if rede.get("name")
    ]

    if redes:
        st.markdown("**Emissoras / plataformas**")
        st.write(", ".join(redes))

with col_prod2:
    produtoras = [
        empresa.get("name")
        for empresa in detalhes.get("production_companies", [])
        if empresa.get("name")
    ]

    if produtoras:
        st.markdown("**Produtoras**")
        st.write(", ".join(produtoras))

    orcamento = detalhes.get("budget")
    receita = detalhes.get("revenue")

    if orcamento:
        st.markdown(f"**Orçamento:** US$ {orcamento:,.0f}".replace(",", "."))

    if receita:
        st.markdown(f"**Bilheteria:** US$ {receita:,.0f}".replace(",", "."))

st.caption(
    "Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB."
)
