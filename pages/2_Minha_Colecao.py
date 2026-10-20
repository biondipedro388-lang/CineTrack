from pathlib import Path
import sys
import html

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
div[class*="st-key-collection_card_"] {
    background: linear-gradient(145deg, #191d2a, #11141d);
    border: 1px solid #2c3243;
    border-radius: 18px;
    padding: 22px;
    margin: 10px 0 22px;
    transition: border-color 0.2s, transform 0.2s;
}
div[class*="st-key-collection_card_"]:hover {
    border-color: #8d73ef;
}
.collection-empty {
    text-align: center;
    padding: 35px 20px;
    border: 1px solid #2c3243;
    border-radius: 18px;
    background: linear-gradient(145deg, #191d2a, #11141d);
}
@media (max-width: 768px) {
    .collection-title {
        font-size: 20px;
    }
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
        if termo in (titulo.get("nome") or "").casefold()
    ]

if ordenacao == "Adicionados recentemente":
    titulos.sort(
        key=lambda titulo: titulo["id"],
        reverse=True
    )
elif ordenacao == "Nome (A–Z)":
    titulos.sort(
        key=lambda titulo: (titulo.get("nome") or "").casefold()
    )
elif ordenacao == "Nome (Z–A)":
    titulos.sort(
        key=lambda titulo: (titulo.get("nome") or "").casefold(),
        reverse=True
    )
elif ordenacao == "Ano (mais recente)":
    titulos.sort(
        key=lambda titulo: (
            int(titulo["ano"])
            if str(titulo.get("ano") or "").isdigit()
            else 0
        ),
        reverse=True
    )
elif ordenacao == "Ano (mais antigo)":
    titulos.sort(
        key=lambda titulo: (
            int(titulo["ano"])
            if str(titulo.get("ano") or "").isdigit()
            else 9999
        )
    )
elif ordenacao == "Nota do TMDB (maior primeiro)":
    titulos.sort(
        key=lambda titulo: float(titulo.get("nota_tmdb") or 0),
        reverse=True
    )
elif ordenacao == "Sua nota pessoal (maior primeiro)":
    titulos.sort(
        key=lambda titulo: (
            titulo.get("nota_pessoal") is not None,
            float(titulo.get("nota_pessoal") or 0)
        ),
        reverse=True
    )

st.write("")

if not titulos:
    if not titulos_originais:
        st.markdown("""
        <div class="collection-empty">
            <h3>🎬 Sua coleção começa aqui</h3>
            <p>Explore o catálogo e adicione seus primeiros filmes e séries.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Explorar catálogo", type="primary"):
            st.switch_page("pages/1_Catalogo.py")
    elif filtro_favoritos == "Somente favoritos" and not any(
        titulo.get("favorito", 0) == 1
        for titulo in titulos_originais
    ):
        st.info(
            "Você ainda não tem favoritos. "
            "Marque títulos com ⭐ para encontrá-los aqui."
        )
    else:
        st.info("Nenhum título encontrado com os filtros selecionados.")
else:
    st.write(f"**{len(titulos)}** título(s) nesta visualização.")

    for titulo in titulos:
        titulo_id_atual = titulo["id"]

        with st.container(key=f"collection_card_{titulo_id_atual}"):
            col_poster, col_info = st.columns([1, 3], gap="large")

            with col_poster:
                if titulo.get("poster"):
                    st.image(
                        f"https://image.tmdb.org/t/p/w342{titulo['poster']}",
                        use_container_width=True
                    )
                else:
                    st.markdown("🎬")
                    st.caption("Pôster indisponível")

            with col_info:
                favorito_atual = titulo.get("favorito", 0) == 1

                texto_favorito = (
                    "⭐ Remover dos favoritos"
                    if favorito_atual
                    else "☆ Adicionar aos favoritos"
                )

                if st.button(
                    texto_favorito,
                    key=f"favorito_{titulo_id_atual}",
                    use_container_width=True
                ):
                    atualizar_favorito(
                        titulo_id_atual,
                        not favorito_atual
                    )
                    st.rerun()

                if favorito_atual:
                    st.markdown(
                        '<div class="collection-favorite">⭐ Está nos seus favoritos</div>',
                        unsafe_allow_html=True
                    )

                status_atual = titulo.get("status") or "Quero assistir"

                st.markdown(
                    f'<div class="collection-status">{html.escape(status_atual)}</div>',
                    unsafe_allow_html=True
                )

                nome_seguro = html.escape(
                    str(titulo.get("nome") or "Título sem nome")
                )

                st.markdown(
                    f'<div class="collection-title">{nome_seguro}</div>',
                    unsafe_allow_html=True
                )

                ano = titulo.get("ano") or "Ano desconhecido"
                categoria = titulo.get("categoria") or "Título"
                nota_tmdb = float(titulo.get("nota_tmdb") or 0)

                st.markdown(
                    f'<div class="collection-meta">{html.escape(str(categoria))} · {html.escape(str(ano))}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="collection-rating">⭐ {nota_tmdb:.1f}/10 no TMDB</div>',
                    unsafe_allow_html=True
                )

                sinopse = titulo.get("sinopse") or "Sinopse indisponível."
                sinopse_segura = html.escape(str(sinopse))

                st.markdown(
                    f'<div class="collection-description">{sinopse_segura}</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    "🔎 Ver detalhes",
                    key=f"detalhes_{titulo_id_atual}",
                    use_container_width=True
                ):
                    st.session_state["titulo_detalhes"] = titulo_id_atual
                    st.switch_page("pages/3_Detalhes.py")

                opcoes_status = [
                    "Quero assistir",
                    "Assistindo",
                    "Concluído"
                ]

                if status_atual not in opcoes_status:
                    status_atual = "Quero assistir"

                novo_status = st.selectbox(
                    "Status",
                    opcoes_status,
                    index=opcoes_status.index(status_atual),
                    key=f"status_{titulo_id_atual}"
                )

                if novo_status != titulo.get("status"):
                    atualizar_status(titulo_id_atual, novo_status)
                    st.rerun()

                nota_atual = titulo.get("nota_pessoal")
                valor_nota = (
                    float(nota_atual)
                    if nota_atual is not None
                    else 0.0
                )

                nova_nota = st.slider(
                    "Sua nota pessoal",
                    min_value=0.0,
                    max_value=10.0,
                    value=valor_nota,
                    step=0.5,
                    key=f"nota_{titulo_id_atual}"
                )

                if st.button(
                    "Salvar minha nota",
                    key=f"salvar_nota_{titulo_id_atual}",
                    use_container_width=True
                ):
                    atualizar_nota_pessoal(
                        titulo_id_atual,
                        nova_nota
                    )
                    st.success("Sua nota foi salva!")
                    st.rerun()

                chave_confirmacao = f"confirmar_remocao_{titulo_id_atual}"

                if st.button(
                    "🗑️ Remover da coleção",
                    key=f"remover_{titulo_id_atual}",
                    use_container_width=True
                ):
                    st.session_state[chave_confirmacao] = True
                    st.rerun()

                if st.session_state.get(chave_confirmacao, False):
                    st.warning(
                        f"Tem certeza de que deseja remover "
                        f"'{titulo.get('nome') or 'este título'}' da sua coleção?"
                    )

                    col_confirmar, col_cancelar = st.columns(2)

                    with col_confirmar:
                        if st.button(
                            "Sim, remover",
                            key=f"confirmar_{titulo_id_atual}",
                            use_container_width=True
                        ):
                            remover_titulo(titulo_id_atual)
                            st.session_state.pop(chave_confirmacao, None)
                            st.rerun()

                    with col_cancelar:
                        if st.button(
                            "Cancelar",
                            key=f"cancelar_{titulo_id_atual}",
                            use_container_width=True
                        ):
                            st.session_state.pop(chave_confirmacao, None)
                            st.rerun()

st.divider()

st.caption(
    "Este produto utiliza a API do TMDB, mas não é endossado nem certificado pelo TMDB."
)
