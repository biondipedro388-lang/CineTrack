from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from components.navbar import mostrar_navbar
from services.database import listar_titulos

st.set_page_config(
    page_title="CineTrack",
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
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stHeaderActionElements"],
#MainMenu {
    display: none !important;
}

.feature-card {
    margin-bottom: 0;
    transition: border-color 0.2s, transform 0.2s;
}

div.stButton > button {
    border-radius: 11px;
    min-height: 45px;
    font-weight: 650;
}

.home-action-button {
    margin-top: 18px;
}

.recent-title-button {
    margin-top: 8px;
}

</style>
""", unsafe_allow_html=True)

mostrar_navbar()
st.divider()

titulos = listar_titulos()

total = len(titulos)
concluidos = sum(
    1 for titulo in titulos
    if titulo["status"] == "Concluído"
)
assistindo = sum(
    1 for titulo in titulos
    if titulo["status"] == "Assistindo"
)
quero_assistir = sum(
    1 for titulo in titulos
    if titulo["status"] == "Quero assistir"
)

st.markdown("""
<div class="hero">
    <div class="hero-tag">SEU UNIVERSO DE ENTRETENIMENTO</div>
    <h1>CineTrack<span class="hero-dot">.</span></h1>
    <p>Seus filmes, suas séries, sua história.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Sua biblioteca</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

metricas = [
    (col1, "TÍTULOS SALVOS", total, "🎬"),
    (col2, "CONCLUÍDOS", concluidos, "✓"),
    (col3, "ASSISTINDO", assistindo, "▶"),
    (col4, "NA LISTA", quero_assistir, "＋")
]

for coluna, titulo_metrica, valor, icone in metricas:
    with coluna:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icone}</div>
            <div class="metric-label">{titulo_metrica}</div>
            <div class="metric-value">{valor}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Continue explorando</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card catalog-feature">
        <div class="feature-icon">⌕</div>
        <div class="feature-label">DESCUBRA ALGO NOVO</div>
        <h3>Explore o catálogo</h3>
        <p>Encontre filmes e séries, conheça novas histórias e salve seus favoritos.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height: 18px"></div>', unsafe_allow_html=True)

    if st.button(
        "Explorar títulos  →",
        key="abrir_catalogo",
        use_container_width=True
    ):
        st.switch_page("pages/1_Catalogo.py")

with col2:
    st.markdown("""
    <div class="feature-card collection-feature">
        <div class="feature-icon">▤</div>
        <div class="feature-label">TUDO NO SEU LUGAR</div>
        <h3>Minha coleção</h3>
        <p>Acompanhe o que quer assistir, o que está vendo e o que já concluiu.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height: 18px"></div>', unsafe_allow_html=True)

    if st.button(
        "Abrir minha coleção  →",
        key="abrir_colecao",
        use_container_width=True
    ):
        st.switch_page("pages/2_Minha_Colecao.py")

st.markdown(
    '<div class="section-title">Adicionados recentemente</div>',
    unsafe_allow_html=True
)

recentes = list(reversed(titulos))[:6]

if recentes:
    colunas = st.columns(3)

    for indice, titulo in enumerate(recentes):
        with colunas[indice % 3]:
            titulo_id = titulo["id"]
            poster = titulo["poster"]

            if poster:
                st.image(
                    f"https://image.tmdb.org/t/p/w342{poster}",
                    use_container_width=True
                )
            else:
                st.markdown("🎬")

            if st.button(
                f'{titulo["nome"]}',
                key=f"abrir_titulo_{titulo_id}",
                use_container_width=True
            ):
                st.session_state["titulo_detalhes"] = titulo_id
                st.switch_page("pages/3_Detalhes.py")

            st.caption(
                f'{titulo["categoria"]} • {titulo["ano"]} • {titulo["status"]}'
            )
else:
    st.info(
        "Sua biblioteca ainda está vazia. "
        "Explore o catálogo e adicione seu primeiro título!"
    )

st.divider()

st.caption("CineTrack • Organize sua próxima história.")
