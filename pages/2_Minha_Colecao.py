from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from components.navbar import mostrar_navbar
from services.database import (
    listar_titulos,
    atualizar_status,
    atualizar_nota_pessoal,
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

col1, col2, col3, col4 = st.columns(4)

metricas = [
    (col1, "TÍTULOS", total),
    (col2, "QUERO ASSISTIR", quero_assistir),
    (col3, "ASSISTINDO", assistindo),
    (col4, "CONCLUÍDOS", concluidos)
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

filtro = st.selectbox(
    "Filtrar por status",
    ["Todos", "Quero assistir", "Assistindo", "Concluído"]
)

titulos = titulos_originais

if filtro != "Todos":
    titulos = [
        titulo for titulo in titulos
        if titulo["status"] == filtro
    ]

if not titulos:
    if not titulos_originais:
        st.info(
            "Sua coleção ainda está vazia. "
            "Explore o catálogo para adicionar seu primeiro título."
        )
    else:
        st.info("Nenhum título encontrado com esse status.")
else:
    st.write(f"{len(titulos)} título(s) nesta visualização.")

    for titulo in titulos:
        col1, col2 = st.columns([1, 3])

        with col1:
            if titulo["poster"]:
                st.image(
                    f"https://image.tmdb.org/t/p/w342{titulo['poster']}",
                    use_container_width=True
                )
            else:
                st.markdown("🎬 *Pôster indisponível*")

        with col2:
            st.subheader(titulo["nome"])

            st.caption(
                f"{titulo['categoria']} • {titulo['ano']} • "
                f"⭐ {titulo['nota_tmdb']:.1f}/10"
            )

            st.write(titulo["sinopse"] or "Sinopse indisponível.")

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

            novo_status = st.selectbox(
                "Status",
                opcoes,
                index=opcoes.index(titulo["status"]),
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

            if st.button(
                "🗑️ Remover da coleção",
                key=f"remover_{titulo['id']}",
                use_container_width=True
            ):
                remover_titulo(titulo["id"])
                st.rerun()

        st.divider()

st.caption(
    "Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB."
)
