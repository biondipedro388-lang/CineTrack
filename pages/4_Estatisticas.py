from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.navbar import mostrar_navbar
from services.database import listar_titulos


st.set_page_config(
    page_title="Estatísticas | CineTrack",
    page_icon="📊",
    layout="wide"
)


def carregar_css():
    caminho_css = ROOT / "styles.css"

    if caminho_css.exists():
        st.markdown(
            f"<style>{caminho_css.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True
        )


def categoria_normalizada(valor):
    valor = str(valor or "").strip().lower()

    if valor in ("filme", "filmes", "movie"):
        return "Filmes"

    if valor in ("série", "séries", "serie", "series", "tv"):
        return "Séries"

    return "Outros"


def nota_valida(valor):
    try:
        if valor is None:
            return None

        nota = float(valor)

        if nota < 0 or nota > 10:
            return None

        return nota
    except (ValueError, TypeError):
        return None


carregar_css()
mostrar_navbar()

st.title("📊 Estatísticas")
st.caption("Acompanhe sua jornada pelo mundo dos filmes e séries.")

titulos = listar_titulos()

if not titulos:
    st.info("Sua coleção ainda está vazia. Adicione filmes e séries para visualizar suas estatísticas.")
    if st.button("Explorar catálogo", use_container_width=False):
        st.switch_page("pages/1_Catalogo.py")
    st.stop()

df = pd.DataFrame(titulos)

if "status" not in df.columns:
    df["status"] = "Quero assistir"

if "categoria" not in df.columns:
    df["categoria"] = "Outros"

if "nota_pessoal" not in df.columns:
    df["nota_pessoal"] = None

df["categoria_exibicao"] = df["categoria"].apply(categoria_normalizada)
df["nota_numerica"] = df["nota_pessoal"].apply(nota_valida)

total = len(df)
assistir = int((df["status"] == "Quero assistir").sum())
assistindo = int((df["status"] == "Assistindo").sum())
concluidos = int((df["status"] == "Concluído").sum())

notas = df["nota_numerica"].dropna()
media = float(notas.mean()) if not notas.empty else 0
avaliados = len(notas)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Títulos na coleção", total)
c2.metric("Concluídos", concluidos)
c3.metric("Assistindo", assistindo)
c4.metric("Média das notas", f"{media:.1f}/10" if avaliados else "Sem notas")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Minha coleção por status")

    status_counts = (
        df["status"]
        .fillna("Sem status")
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Quantidade")
    )

    st.bar_chart(status_counts, x="Status", y="Quantidade")

with col2:
    st.subheader("Filmes e séries")

    categoria_counts = (
        df["categoria_exibicao"]
        .value_counts()
        .rename_axis("Categoria")
        .reset_index(name="Quantidade")
    )

    st.bar_chart(categoria_counts, x="Categoria", y="Quantidade")

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("Distribuição das minhas notas")

    if avaliados:
        distribuicao = (
            df.dropna(subset=["nota_numerica"])
            .groupby("nota_numerica")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("nota_numerica")
        )

        st.bar_chart(distribuicao, x="nota_numerica", y="Quantidade")

        st.caption(
            f"Você avaliou {avaliados} título(s). "
            f"Menor nota: {notas.min():.1f} | Maior nota: {notas.max():.1f}"
        )
    else:
        st.info("Dê notas aos títulos da sua coleção para ver essa distribuição.")

with col4:
    st.subheader("Meus favoritos")

    favoritos = (
        df.dropna(subset=["nota_numerica"])
        .sort_values("nota_numerica", ascending=False)
        .head(5)
    )

    if favoritos.empty:
        st.info("Você ainda não avaliou nenhum título.")
    else:
        for _, titulo in favoritos.iterrows():
            nome = titulo.get("nome", "Título sem nome")
            nota = titulo["nota_numerica"]
            categoria = titulo["categoria_exibicao"]

            st.markdown(
                f"**{nome}**  \n"
                f"⭐ {nota:.1f}/10 · {categoria}"
            )
            st.divider()
