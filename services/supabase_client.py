import streamlit as st
from supabase import create_client, Client


def conectar_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    chave = st.secrets["SUPABASE_KEY"]

    return create_client(url, chave)


supabase = conectar_supabase()


def obter_cliente_usuario() -> Client:
    usuario = st.session_state.get("usuario_cinetrack")
    sessao = st.session_state.get("sessao_supabase")

    if not usuario or not sessao:
        return supabase

    usuario_id = usuario.get("id")

    cliente_existente = st.session_state.get("supabase_usuario")
    usuario_existente = st.session_state.get("supabase_usuario_id")

    if cliente_existente and usuario_existente == usuario_id:
        return cliente_existente

    cliente = conectar_supabase()

    cliente.auth.set_session(
        sessao["access_token"],
        sessao["refresh_token"]
    )

    st.session_state["supabase_usuario"] = cliente
    st.session_state["supabase_usuario_id"] = usuario_id

    return cliente
