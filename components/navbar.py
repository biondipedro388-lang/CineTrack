import streamlit as st
from services.supabase_client import supabase


def mostrar_navbar():
    usuario = st.session_state.get("usuario")

    st.markdown("""
    <div class="cinetrack-navbar">
        <div class="cinetrack-logo">
            <span class="cinetrack-logo-icon">C</span>
            <span>CineTrack<span class="cinetrack-logo-dot">.</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    espaco, inicio, catalogo, colecao, diario, estatisticas, entrar = st.columns(
        [1.5, 0.8, 1, 1.25, 0.8, 1, 0.9],
        vertical_alignment="center"
    )

    with inicio:
        st.page_link("app.py", label="Início")

    with catalogo:
        st.page_link("pages/1_Catalogo.py", label="Catálogo")

    with colecao:
        st.page_link("pages/2_Minha_Colecao.py", label="Minha coleção")

    with diario:
        st.page_link("pages/5_Diario.py", label="Diário")

    with estatisticas:
        st.page_link("pages/4_Estatisticas.py", label="Estatísticas")

    with entrar:
        if usuario:
            if st.button(
                "Sair",
                key="navbar_sair",
                use_container_width=True
            ):
                try:
                    supabase.auth.sign_out()
                except Exception:
                    pass

                st.session_state.pop("usuario", None)
                st.session_state.pop("usuario_cinetrack", None)
                st.session_state.pop("sessao_supabase", None)
                st.session_state.pop("supabase_usuario", None)
                st.session_state["abrir_login"] = False
                st.rerun()
        else:
            if st.button(
                "Entrar",
                key="navbar_entrar",
                use_container_width=True
            ):
                st.session_state["abrir_login"] = not st.session_state.get(
                    "abrir_login", False
                )

    if st.session_state.get("abrir_login", False) and not usuario:
        mostrar_tela_login()


def mostrar_tela_login():
    st.markdown("---")
    st.subheader("Entre no CineTrack")
    st.write("Acesse sua conta ou crie uma nova.")

    modo = st.radio(
        "Escolha uma opção",
        ["Entrar", "Criar conta"],
        horizontal=True,
        key="modo_autenticacao"
    )

    with st.form("formulario_autenticacao"):
        nome = ""

        if modo == "Criar conta":
            nome = st.text_input(
                "Nome",
                placeholder="Como você quer ser chamado?"
            )

        email = st.text_input(
            "E-mail",
            placeholder="voce@email.com"
        )

        confirmar_email = ""

        if modo == "Criar conta":
            confirmar_email = st.text_input(
                "Confirme seu e-mail",
                placeholder="Digite o e-mail novamente"
            )

        senha = st.text_input(
            "Senha",
            type="password"
        )

        confirmar_senha = ""

        if modo == "Criar conta":
            confirmar_senha = st.text_input(
                "Confirme sua senha",
                type="password"
            )

        enviar = st.form_submit_button(
            "Entrar" if modo == "Entrar" else "Criar conta",
            use_container_width=True
        )

        if not enviar:
            return

        email = email.strip().lower()

        if not email or not senha:
            st.warning("Preencha o e-mail e a senha.")
            return

        if modo == "Criar conta":
            if not nome.strip():
                st.warning("Informe seu nome.")
                return

            if not confirmar_email.strip():
                st.warning("Confirme seu e-mail.")
                return

            if email != confirmar_email.strip().lower():
                st.error("Os e-mails não coincidem.")
                return

            if not confirmar_senha:
                st.warning("Confirme sua senha.")
                return

            if senha != confirmar_senha:
                st.error("As senhas não coincidem.")
                return

            if len(senha) < 6:
                st.warning("A senha deve ter pelo menos 6 caracteres.")
                return

        try:
            if modo == "Entrar":
                resposta = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": senha
                })

                usuario = resposta.user
                sessao = resposta.session

                if not usuario or not sessao:
                    st.error("Não foi possível iniciar a sessão.")
                    return

                nome_usuario = (
                    usuario.user_metadata.get("nome", "")
                    if usuario.user_metadata
                    else ""
                )

                dados_usuario = {
                    "id": usuario.id,
                    "email": usuario.email,
                    "nome": nome_usuario
                }

                dados_sessao = {
                    "access_token": sessao.access_token,
                    "refresh_token": sessao.refresh_token
                }

                st.session_state["usuario"] = dados_usuario
                st.session_state["usuario_cinetrack"] = dados_usuario
                st.session_state["sessao_supabase"] = dados_sessao
                st.session_state["abrir_login"] = False

                st.success("Login realizado com sucesso!")
                st.rerun()

            else:
                resposta = supabase.auth.sign_up({
                    "email": email,
                    "password": senha,
                    "options": {
                        "data": {
                            "nome": nome.strip()
                        }
                    }
                })

                usuario = resposta.user
                sessao = resposta.session

                if not usuario:
                    st.error("Não foi possível criar a conta.")
                    return

                if not sessao:
                    try:
                        resposta_login = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": senha
                        })

                        usuario = resposta_login.user
                        sessao = resposta_login.session

                    except Exception as erro:
                        st.error(
                            f"Erro no login automático: {erro}"
                        )
                        usuario = None
                        sessao = None

                if usuario and sessao:
                    dados_usuario = {
                        "id": usuario.id,
                        "email": usuario.email,
                        "nome": nome.strip()
                    }

                    dados_sessao = {
                        "access_token": sessao.access_token,
                        "refresh_token": sessao.refresh_token
                    }

                    st.session_state["usuario"] = dados_usuario
                    st.session_state["usuario_cinetrack"] = dados_usuario
                    st.session_state["sessao_supabase"] = dados_sessao
                    st.session_state["abrir_login"] = False

                    st.success(
                        "Conta criada e login realizado com sucesso!"
                    )
                    st.rerun()

                else:
                    st.error(
                        "A conta pode ter sido criada, mas a sessão não "
                        "foi iniciada. Confira o erro acima."
                    )

        except Exception as erro:
            st.error(
                f"Não foi possível concluir a operação: {erro}"
            )
