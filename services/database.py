import streamlit as st
from services.supabase_client import obter_cliente_usuario


def _cliente():
    return obter_cliente_usuario()


def _usuario_id():
    usuario = st.session_state.get("usuario_cinetrack")

    if not usuario or not usuario.get("id"):
        return None

    return usuario["id"]


def _exigir_usuario():
    usuario_id = _usuario_id()

    if not usuario_id:
        st.warning("Entre na sua conta para acessar sua biblioteca.")
        return None

    return usuario_id


def listar_titulos():
    usuario_id = _usuario_id()

    if not usuario_id:
        return []

    resposta = (
        _cliente()
        .table("titulos")
        .select("*")
        .eq("user_id", usuario_id)
        .order("id", desc=True)
        .execute()
    )

    titulos = resposta.data or []

    for titulo in titulos:
        titulo["favorito"] = 1 if titulo.get("favorito") else 0

    return titulos


def adicionar_titulo(titulo):
    usuario_id = _exigir_usuario()

    if not usuario_id:
        return

    cliente = _cliente()
    tmdb_id = titulo.get("id")
    categoria = titulo.get("categoria")

    existentes = (
        cliente
        .table("titulos")
        .select("id")
        .eq("user_id", usuario_id)
        .eq("tmdb_id", tmdb_id)
        .eq("categoria", categoria)
        .execute()
    )

    if existentes.data:
        return

    ano = titulo.get("ano")

    try:
        ano = int(str(ano)[:4]) if ano else None
    except (ValueError, TypeError):
        ano = None

    dados = {
        "user_id": usuario_id,
        "tmdb_id": tmdb_id,
        "nome": titulo["nome"],
        "categoria": categoria,
        "ano": ano,
        "nota_tmdb": titulo.get("nota"),
        "sinopse": titulo.get("sinopse"),
        "poster": titulo.get("poster"),
        "status": titulo.get("status", "Quero assistir"),
        "favorito": False,
    }

    cliente.table("titulos").insert(dados).execute()


def atualizar_status(titulo_id, status):
    usuario_id = _exigir_usuario()

    if not usuario_id:
        return

    _cliente().table("titulos").update({
        "status": status
    }).eq(
        "id", titulo_id
    ).eq(
        "user_id", usuario_id
    ).execute()


def atualizar_nota_pessoal(titulo_id, nota):
    usuario_id = _exigir_usuario()

    if not usuario_id:
        return

    _cliente().table("titulos").update({
        "nota_pessoal": nota
    }).eq(
        "id", titulo_id
    ).eq(
        "user_id", usuario_id
    ).execute()


def atualizar_favorito(titulo_id, favorito):
    usuario_id = _exigir_usuario()

    if not usuario_id:
        return

    _cliente().table("titulos").update({
        "favorito": bool(favorito)
    }).eq(
        "id", titulo_id
    ).eq(
        "user_id", usuario_id
    ).execute()


def atualizar_dados_titulo(titulo_id, nome, ano, sinopse):
    usuario_id = _exigir_usuario()

    if not usuario_id:
        return

    try:
        ano_convertido = int(str(ano).strip()[:4]) if ano else None
    except (ValueError, TypeError):
        ano_convertido = None

    _cliente().table("titulos").update({
        "nome": nome.strip(),
        "ano": ano_convertido,
        "sinopse": sinopse.strip() if sinopse else "",
    }).eq(
        "id", titulo_id
    ).eq(
        "user_id", usuario_id
    ).execute()


def adicionar_registro_diario(
    titulo_id,
    data_assistido,
    nota,
    comentario
):
    usuario_id = _exigir_usuario()

    if not usuario_id:
        return

    cliente = _cliente()

    titulo = (
        cliente
        .table("titulos")
        .select("id")
        .eq("id", titulo_id)
        .eq("user_id", usuario_id)
        .execute()
    )

    if not titulo.data:
        st.error("Esse título não foi encontrado na sua coleção.")
        return

    if hasattr(data_assistido, "isoformat"):
        data_assistido = data_assistido.isoformat()

    cliente.table("diario").insert({
        "user_id": usuario_id,
        "titulo_id": titulo_id,
        "data_assistido": data_assistido,
        "nota": nota,
        "comentario": comentario.strip() if comentario else "",
    }).execute()

    cliente.table("titulos").update({
        "status": "Concluído"
    }).eq(
        "id", titulo_id
    ).eq(
        "user_id", usuario_id
    ).execute()


def listar_diario():
    usuario_id = _usuario_id()

    if not usuario_id:
        return []

    resposta = (
        _cliente()
        .table("diario")
        .select(
            "id, titulo_id, data_assistido, nota, "
            "comentario, criado_em, "
            "titulos(nome, categoria, ano, poster)"
        )
        .eq("user_id", usuario_id)
        .order("data_assistido", desc=True)
        .order("id", desc=True)
        .execute()
    )

    registros = []

    for registro in resposta.data or []:
        titulo = registro.pop("titulos", None) or {}

        registro["nome"] = titulo.get("nome")
        registro["categoria"] = titulo.get("categoria")
        registro["ano"] = titulo.get("ano")
        registro["poster"] = titulo.get("poster")

        registros.append(registro)

    return registros


def remover_registro_diario(registro_id):
    usuario_id = _exigir_usuario()

    if not usuario_id:
        return

    _cliente().table("diario").delete().eq(
        "id", registro_id
    ).eq(
        "user_id", usuario_id
    ).execute()


def remover_titulo(titulo_id):
    usuario_id = _exigir_usuario()

    if not usuario_id:
        return

    _cliente().table("titulos").delete().eq(
        "id", titulo_id
    ).eq(
        "user_id", usuario_id
    ).execute()
