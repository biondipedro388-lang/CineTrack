from pathlib import Path
import sys
from datetime import date

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.navbar import mostrar_navbar
from services.database import listar_titulos, listar_diario


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
        if valor is None or pd.isna(valor):
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
registros = listar_diario()

if not titulos:
    st.info(
        "Sua coleção ainda está vazia. Adicione filmes e séries "
        "para visualizar suas estatísticas."
    )

    if st.button("Explorar catálogo"):
        st.switch_page("pages/1_Catalogo.py")

    st.stop()


df = pd.DataFrame(titulos)

if "status" not in df.columns:
    df["status"] = "Quero assistir"

if "categoria" not in df.columns:
    df["categoria"] = "Outros"

if "nota_pessoal" not in df.columns:
    df["nota_pessoal"] = None

if "favorito" not in df.columns:
    df["favorito"] = 0

df["categoria_exibicao"] = df["categoria"].apply(categoria_normalizada)
df["nota_numerica"] = df["nota_pessoal"].apply(nota_valida)

total = len(df)
assistir = int((df["status"] == "Quero assistir").sum())
assistindo = int((df["status"] == "Assistindo").sum())
concluidos = int((df["status"] == "Concluído").sum())

notas_colecao = df["nota_numerica"].dropna()
media_colecao = (
    float(notas_colecao.mean())
    if not notas_colecao.empty
    else None
)

if registros:
    diario_df = pd.DataFrame(registros)
else:
    diario_df = pd.DataFrame(
        columns=[
            "id",
            "titulo_id",
            "data_assistido",
            "nota",
            "comentario",
            "nome",
            "categoria",
            "ano"
        ]
    )

diario_df["nota_numerica"] = (
    diario_df["nota"].apply(nota_valida)
    if "nota" in diario_df.columns
    else None
)

if "data_assistido" in diario_df.columns:
    diario_df["data_formatada"] = pd.to_datetime(
        diario_df["data_assistido"],
        errors="coerce"
    )
else:
    diario_df["data_formatada"] = pd.NaT

if "categoria" in diario_df.columns:
    diario_df["categoria_exibicao"] = (
        diario_df["categoria"].apply(categoria_normalizada)
    )
else:
    diario_df["categoria_exibicao"] = "Outros"

total_registros = len(diario_df)

titulos_registrados = (
    diario_df["titulo_id"].nunique()
    if "titulo_id" in diario_df.columns
    else 0
)

notas_diario = diario_df["nota_numerica"].dropna()

media_diario = (
    float(notas_diario.mean())
    if not notas_diario.empty
    else None
)

ano_atual = date.today().year

registros_ano = int(
    (
        diario_df["data_formatada"].dt.year == ano_atual
    ).sum()
)

st.subheader("Visão geral da coleção")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Títulos salvos", total)
c2.metric("Concluídos", concluidos)
c3.metric("Assistindo", assistindo)
c4.metric(
    "Média da coleção",
    f"{media_colecao:.1f}/10"
    if media_colecao is not None
    else "Sem notas"
)

c5, c6, c7, c8 = st.columns(4)

c5.metric("Registros no diário", total_registros)
c6.metric("Títulos registrados", titulos_registrados)
c7.metric(
    "Média do diário",
    f"{media_diario:.1f}/10"
    if media_diario is not None
    else "Sem notas"
)
c8.metric(f"Registros em {ano_atual}", registros_ano)

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
    st.subheader("Filmes e séries na coleção")

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
    st.subheader("Distribuição das notas da coleção")

    if not notas_colecao.empty:
        distribuicao = (
            df.dropna(subset=["nota_numerica"])
            .groupby("nota_numerica")
            .size()
            .reset_index(name="Quantidade")
            .sort_values("nota_numerica")
        )

        st.bar_chart(
            distribuicao,
            x="nota_numerica",
            y="Quantidade"
        )

        st.caption(
            f"{len(notas_colecao)} título(s) avaliados. "
            f"Menor nota: {notas_colecao.min():.1f} · "
            f"Maior nota: {notas_colecao.max():.1f}"
        )
    else:
        st.info(
            "Dê notas aos títulos da coleção para visualizar "
            "a distribuição."
        )

with col4:
    st.subheader("Meus favoritos por nota")

    favoritos = (
        df[df["favorito"].fillna(0).astype(int) == 1]
        .copy()
    )

    if favoritos.empty:
        st.info(
            "Você ainda não marcou títulos como favoritos."
        )
    else:
        favoritos["nota_ordenacao"] = (
            favoritos["nota_numerica"].fillna(-1)
        )

        favoritos = favoritos.sort_values(
            "nota_ordenacao",
            ascending=False
        ).head(5)

        for _, titulo in favoritos.iterrows():
            nome = titulo.get("nome", "Título sem nome")
            nota = titulo["nota_numerica"]
            categoria = titulo["categoria_exibicao"]

            texto_nota = (
                f"⭐ {nota:.1f}/10"
                if nota is not None and pd.notna(nota)
                else "Ainda sem nota"
            )

            st.markdown(
                f"**❤️ {nome}**  \n"
                f"{texto_nota} · {categoria}"
            )

            st.divider()

st.divider()
st.header("📔 Minha jornada no diário")

if diario_df.empty:
    st.info(
        "Seu diário ainda não tem registros. "
        "Use a página Meu diário para registrar o que assistiu."
    )

else:
    diario_com_data = diario_df.dropna(
        subset=["data_formatada"]
    ).copy()

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Visualizações por mês")

        if diario_com_data.empty:
            st.info(
                "Não há datas válidas no diário para montar o gráfico."
            )
        else:
            mensal = (
                diario_com_data
                .assign(
                    Mes=diario_com_data[
                        "data_formatada"
                    ].dt.to_period("M").astype(str)
                )
                .groupby("Mes")
                .size()
                .reset_index(name="Visualizações")
                .sort_values("Mes")
                .tail(12)
            )

            st.bar_chart(
                mensal,
                x="Mes",
                y="Visualizações"
            )

            st.caption(
                "O gráfico mostra os últimos 12 meses "
                "com registros, quando disponíveis."
            )

    with col6:
        st.subheader("Visualizações por ano")

        if diario_com_data.empty:
            st.info(
                "Não há datas válidas no diário para montar o gráfico."
            )
        else:
            anual = (
                diario_com_data
                .assign(
                    Ano=diario_com_data[
                        "data_formatada"
                    ].dt.year
                )
                .groupby("Ano")
                .size()
                .reset_index(name="Visualizações")
                .sort_values("Ano")
            )

            anual["Ano"] = anual["Ano"].astype(str)

            st.bar_chart(
                anual,
                x="Ano",
                y="Visualizações"
            )

    st.divider()

    col7, col8 = st.columns(2)

    with col7:
        st.subheader("Registros por categoria")

        categorias_diario = (
            diario_df["categoria_exibicao"]
            .value_counts()
            .rename_axis("Categoria")
            .reset_index(name="Registros")
        )

        st.bar_chart(
            categorias_diario,
            x="Categoria",
            y="Registros"
        )

    with col8:
        st.subheader("Títulos mais registrados")

        mais_registrados = (
            diario_df
            .groupby("nome")
            .size()
            .reset_index(name="Registros")
            .sort_values(
                "Registros",
                ascending=False
            )
            .head(5)
        )

        if mais_registrados.empty:
            st.info("Ainda não há títulos registrados.")
        else:
            st.bar_chart(
                mais_registrados,
                x="nome",
                y="Registros"
            )

    st.divider()
    st.subheader("🏆 Melhores notas do diário")

    melhores = (
        diario_df.dropna(subset=["nota_numerica"])
        .sort_values("nota_numerica", ascending=False)
        .head(5)
    )

    if melhores.empty:
        st.info(
            "Registre notas no diário para descobrir "
            "seus títulos mais bem avaliados."
        )
    else:
        for _, registro in melhores.iterrows():
            nome = registro.get("nome", "Título sem nome")
            nota = registro["nota_numerica"]
            categoria = registro.get(
                "categoria_exibicao",
                "Outros"
            )
            data_registro = registro.get("data_assistido", "")

            st.markdown(
                f"**{nome}**  \n"
                f"⭐ {nota:.1f}/10 · {categoria} · "
                f"Assistido em {data_registro}"
            )

            comentario = registro.get("comentario") or ""

            if comentario.strip():
                with st.expander("Ver meu comentário"):
                    st.write(comentario)

            st.divider()

st.caption(
    "As estatísticas do diário consideram cada registro individual. "
    "Reassistidas também contam como novas visualizações."
)
