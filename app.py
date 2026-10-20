from pathlib import Path
import sys
import html
import streamlit as st

RAIZ = Path(__file__).resolve().parent

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from components.navbar import mostrar_navbar
from services.database import listar_titulos

st.set_page_config(
    page_title="CineTrack",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
#MainMenu,
footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1440px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.stApp {
    background: #0c0e14;
    color: #f4f5f7;
}

.page-hero {
    background: linear-gradient(120deg, #171827 0%, #211b35 55%, #151923 100%);
    border: 1px solid #302a47;
    border-radius: 22px;
    padding: 36px;
    margin-bottom: 28px;
    box-sizing: border-box;
}

.hero-eyebrow {
    color: #b9a7ff;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.hero-title {
    color: #ffffff;
    font-size: clamp(30px, 4vw, 44px);
    font-weight: 850;
    line-height: 1.2;
    margin: 0 0 14px;
    overflow-wrap: break-word;
}

.hero-description {
    color: #b9bfd0;
    font-size: 16px;
    line-height: 1.7;
    margin: 0;
    max-width: 680px;
    overflow-wrap: break-word;
}

.section-title {
    color: #f4f5f7;
    font-size: 22px;
    font-weight: 800;
    margin: 28px 0 16px;
}

.section-subtitle {
    color: #9da5b8;
    font-size: 14px;
    line-height: 1.6;
    margin-top: -8px;
    margin-bottom: 18px;
}

.metric-card {
    background: #141722;
    border: 1px solid #292e3e;
    border-radius: 15px;
    padding: 20px 18px;
    min-height: 108px;
    height: 100%;
    box-sizing: border-box;
}

.metric-label {
    color: #9da5b8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.8px;
    line-height: 1.5;
    overflow-wrap: break-word;
}

.metric-value {
    color: #ffffff;
    font-size: 30px;
    font-weight: 850;
    margin-top: 8px;
    line-height: 1.2;
}

.feature-card {
    background: linear-gradient(145deg, #171a27, #131620);
    border: 1px solid #303449;
    border-radius: 18px;
    padding: 24px;
    min-height: 250px;
    height: auto;
    box-sizing: border-box;
    overflow-wrap: break-word;
    word-wrap: break-word;
    transition: border-color 0.2s, transform 0.2s;
}

.feature-card:hover {
    border-color: #7661c7;
    transform: translateY(-2px);
}

.feature-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 13px;
    background: #29213f;
    border: 1px solid #493b70;
    color: #d4c7ff;
    font-size: 24px;
    margin-bottom: 20px;
}

.feature-label {
    color: #b9a7ff;
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 1.4px;
    line-height: 1.5;
    margin-bottom: 9px;
    overflow-wrap: break-word;
}

.feature-card h3 {
    color: #ffffff;
    font-size: 22px;
    font-weight: 800;
    line-height: 1.35;
    margin: 0 0 12px;
    overflow-wrap: break-word;
}

.feature-card p {
    color: #aeb6c9;
    font-size: 14px;
    line-height: 1.7;
    margin: 0;
    overflow-wrap: break-word;
}

div.stButton > button {
    border-radius: 11px;
    min-height: 45px;
    height: auto;
    font-weight: 650;
    line-height: 1.4;
    white-space: normal;
    overflow-wrap: break-word;
    padding: 10px 14px;
    transition: background 0.2s, border-color 0.2s;
}

div.st-key-abrir_catalogo button,
div.st-key-abrir_colecao button {
    background: #191d2a !important;
    color: #f4f5f7 !important;
    border: 1px solid #493b70 !important;
}

div.st-key-abrir_catalogo button:hover,
div.st-key-abrir_colecao button:hover {
    background: #29213f !important;
    border-color: #8d73ef !important;
    color: #ffffff !important;
}

div.st-key-abrir_estatisticas button,
div.st-key-abrir_diario button {
    background: #141722 !important;
    color: #e8e9f0 !important;
    border: 1px solid #303449 !important;
}

div.st-key-abrir_estatisticas button:hover,
div.st-key-abrir_diario button:hover {
    background: #202437 !important;
    border-color: #7661c7 !important;
}

div[class*="st-key-home_recent_"],
div[class*="st-key-home_favorite_"] {
    background: #141722;
    border: 1px solid #292e3e;
    border-radius: 15px;
    padding: 12px;
    height: 100%;
    box-sizing: border-box;
}

div[class*="st-key-home_recent_"] img,
div[class*="st-key-home_favorite_"] img {
    border-radius: 9px;
}

.home-title-name {
    color: #f4f5f7;
    font-size: 14px;
    font-weight: 800;
    line-height: 1.45;
    margin: 8px 0 6px;
    overflow-wrap: anywhere;
}

.home-title-meta {
    color: #9da5b8;
    font-size: 12px;
    line-height: 1.5;
    margin-bottom: 8px;
    overflow-wrap: break-word;
}

.home-title-rating {
    color: #f2cf75;
    font-size: 12px;
    font-weight: 750;
    margin-bottom: 5px;
}

.home-title-status {
    display: inline-block;
    background: #29213f;
    border: 1px solid #493b70;
    border-radius: 20px;
    color: #d5c9ff;
    padding: 4px 8px;
    font-size: 10px;
    font-weight: 750;
    margin: 4px 0;
}

.empty-state {
    background: #141722;
    border: 1px dashed #383d52;
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    color: #aeb6c9;
    line-height: 1.7;
}

.empty-state-title {
    color: #f4f5f7;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 8px;
}

div[data-testid="stImage"] img {
    border-radius: 9px;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .page-hero {
        padding: 24px;
    }

    .feature-card {
        padding: 20px;
        min-height: 0;
    }

    .feature-card h3 {
        font-size: 20px;
    }

    .metric-card {
        padding: 14px;
    }

    .metric-value {
        font-size: 24px;
    }
}
</style>
""", unsafe_allow_html=True)

mostrar_navbar()
st.divider()

titulos = listar_titulos() or []

total = len(titulos)

quero_assistir = sum(
    1 for titulo in titulos
    if titulo.get("status") == "Quero assistir"
)

assistindo = sum(
    1 for titulo in titulos
    if titulo.get("status") == "Assistindo"
)

concluidos = sum(
    1 for titulo in titulos
    if titulo.get("status") == "Concluído"
)

favoritos = [
    titulo for titulo in titulos
    if titulo.get("favorito", 0) == 1
]

recentes = sorted(
    titulos,
    key=lambda titulo: titulo.get("id", 0) or 0,
    reverse=True
)

st.markdown("""
<div class="page-hero">
    <div class="hero-eyebrow">SUA EXPERIÊNCIA, SUA HISTÓRIA</div>
    <h1 class="hero-title">Bem-vindo ao CineTrack</h1>
    <p class="hero-description">
        Organize seus filmes e séries, acompanhe o que está assistindo
        e monte uma biblioteca com as histórias que marcaram você.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

metricas = [
    (col1, "TÍTULOS", total),
    (col2, "QUERO ASSISTIR", quero_assistir),
    (col3, "ASSISTINDO", assistindo),
    (col4, "CONCLUÍDOS", concluidos),
    (col5, "FAVORITOS ⭐", len(favoritos))
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
    '<div class="section-title">O que você quer fazer hoje?</div>',
    unsafe_allow_html=True
)

col_catalogo, col_colecao = st.columns(2, gap="large")

with col_catalogo:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⌕</div>
        <div class="feature-label">DESCUBRA ALGO NOVO</div>
        <h3>Explore o catálogo</h3>
        <p>
            Pesquise filmes e séries, confira as avaliações e encontre
            sua próxima história favorita.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height: 14px;"></div>', unsafe_allow_html=True)

    if st.button(
        "Explorar catálogo →",
        key="abrir_catalogo",
        use_container_width=True
    ):
        st.switch_page("pages/1_Catalogo.py")

with col_colecao:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">▤</div>
        <div class="feature-label">SUA BIBLIOTECA PESSOAL</div>
        <h3>Minha coleção</h3>
        <p>
            Organize seus títulos, atualize seu progresso, avalie o que
            assistiu e guarde seus favoritos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height: 14px;"></div>', unsafe_allow_html=True)

    if st.button(
        "Abrir minha coleção →",
        key="abrir_colecao",
        use_container_width=True
    ):
        st.switch_page("pages/2_Minha_Colecao.py")

st.markdown(
    '<div class="section-title">Acessos rápidos</div>',
    unsafe_allow_html=True
)

col_estatisticas, col_diario = st.columns(2, gap="large")

with col_estatisticas:
    if st.button(
        "📊  Minhas estatísticas",
        key="abrir_estatisticas",
        use_container_width=True
    ):
        st.switch_page("pages/4_Estatisticas.py")

with col_diario:
    if st.button(
        "📔  Meu diário",
        key="abrir_diario",
        use_container_width=True
    ):
        st.switch_page("pages/5_Diario.py")

st.markdown(
    '<div class="section-title">Adicionados recentemente</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Os últimos títulos que chegaram à sua biblioteca.'
    '</div>',
    unsafe_allow_html=True
)


def mostrar_titulo_resumido(titulo, chave, mostrar_status=False):
    titulo_id = titulo.get("id", chave)
    nome = html.escape(str(titulo.get("nome") or "Título sem nome"))
    categoria = html.escape(str(titulo.get("categoria") or "Título"))
    ano = html.escape(str(titulo.get("ano") or "Ano desconhecido"))
    nota = float(titulo.get("nota_tmdb") or 0)
    status = html.escape(str(titulo.get("status") or "Sem status"))
    poster = titulo.get("poster")

    with st.container(key=f"{chave}_{titulo_id}"):
        if poster:
            st.image(
                f"https://image.tmdb.org/t/p/w342{poster}",
                width=150
            )
        else:
            st.markdown("🎬 *Pôster indisponível*")

        st.markdown(
            f'<div class="home-title-name">{nome}</div>'
            f'<div class="home-title-meta">{categoria} · {ano}</div>',
            unsafe_allow_html=True
        )

        if mostrar_status:
            st.markdown(
                f'<div class="home-title-status">{status}</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="home-title-rating">⭐ {nota:.1f}/10 no TMDB</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "Ver detalhes",
            key=f"detalhes_{chave}_{titulo_id}",
            use_container_width=True
        ):
            st.session_state["titulo_detalhes"] = titulo_id
            st.switch_page("pages/3_Detalhes.py")


if recentes:
    colunas_recentes = st.columns(min(5, len(recentes)), gap="medium")

    for indice, titulo in enumerate(recentes[:5]):
        with colunas_recentes[indice]:
            mostrar_titulo_resumido(
                titulo,
                "home_recent",
                mostrar_status=True
            )
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-title">Sua biblioteca começa aqui</div>
        Você ainda não adicionou nenhum filme ou série.
        Explore o catálogo e encontre algo para assistir.
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "Encontrar meu primeiro título →",
        key="catalogo_vazio",
        use_container_width=True
    ):
        st.switch_page("pages/1_Catalogo.py")

if favoritos:
    st.markdown(
        '<div class="section-title">Seus favoritos ⭐</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Aquelas histórias que você quer guardar por perto.'
        '</div>',
        unsafe_allow_html=True
    )

    colunas_favoritos = st.columns(min(5, len(favoritos)), gap="medium")

    for indice, titulo in enumerate(favoritos[:5]):
        with colunas_favoritos[indice]:
            mostrar_titulo_resumido(
                titulo,
                "home_favorite",
                mostrar_status=False
            )