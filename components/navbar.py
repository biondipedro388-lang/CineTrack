import streamlit as st


def mostrar_navbar():
    st.markdown("""
    <div class="cinetrack-navbar">
        <div class="cinetrack-logo">
            <span class="cinetrack-logo-icon">C</span>
            <span>CineTrack<span class="cinetrack-logo-dot">.</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    espaco, inicio, catalogo, colecao, estatisticas, entrar = st.columns(
        [2.2, 1, 1.2, 1.5, 1.2, 1],
        vertical_alignment="center"
    )

    with inicio:
        st.page_link("app.py", label="Início")

    with catalogo:
        st.page_link("pages/1_Catalogo.py", label="Catálogo")

    with colecao:
        st.page_link("pages/2_Minha_Colecao.py", label="Minha coleção")

    with estatisticas:
        st.page_link("pages/4_Estatisticas.py", label="Estatísticas")

    with entrar:
        if st.button("Entrar", key="navbar_entrar", use_container_width=True):
            st.session_state["abrir_login"] = True

    if st.session_state.get("abrir_login", False):
        st.info("A tela de login será criada na próxima etapa.")
