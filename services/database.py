import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "cinetrack.db"


def conectar():
    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS titulos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tmdb_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                ano TEXT,
                nota_tmdb REAL DEFAULT 0,
                sinopse TEXT,
                poster TEXT,
                status TEXT NOT NULL DEFAULT 'Quero assistir',
                nota_pessoal REAL,
                favorito INTEGER NOT NULL DEFAULT 0,
                UNIQUE(tmdb_id, categoria)
            )
        """)

        colunas = conexao.execute(
            "PRAGMA table_info(titulos)"
        ).fetchall()

        nomes_colunas = [coluna["name"] for coluna in colunas]

        if "favorito" not in nomes_colunas:
            conexao.execute("""
                ALTER TABLE titulos
                ADD COLUMN favorito INTEGER NOT NULL DEFAULT 0
            """)


def listar_titulos():
    with conectar() as conexao:
        titulos = conexao.execute("""
            SELECT *
            FROM titulos
            ORDER BY id DESC
        """).fetchall()

        return [dict(titulo) for titulo in titulos]


def adicionar_titulo(titulo):
    with conectar() as conexao:
        conexao.execute("""
            INSERT OR IGNORE INTO titulos (
                tmdb_id, nome, categoria, ano, nota_tmdb,
                sinopse, poster, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            titulo["id"],
            titulo["nome"],
            titulo["categoria"],
            titulo["ano"],
            titulo["nota"],
            titulo["sinopse"],
            titulo["poster"],
            titulo.get("status", "Quero assistir")
        ))


def atualizar_status(titulo_id, status):
    with conectar() as conexao:
        conexao.execute("""
            UPDATE titulos
            SET status = ?
            WHERE id = ?
        """, (status, titulo_id))


def atualizar_nota_pessoal(titulo_id, nota):
    with conectar() as conexao:
        conexao.execute("""
            UPDATE titulos
            SET nota_pessoal = ?
            WHERE id = ?
        """, (nota, titulo_id))


def atualizar_favorito(titulo_id, favorito):
    with conectar() as conexao:
        conexao.execute("""
            UPDATE titulos
            SET favorito = ?
            WHERE id = ?
        """, (1 if favorito else 0, titulo_id))


def atualizar_dados_titulo(titulo_id, nome, ano, sinopse):
    with conectar() as conexao:
        conexao.execute("""
            UPDATE titulos
            SET nome = ?, ano = ?, sinopse = ?
            WHERE id = ?
        """, (
            nome.strip(),
            ano.strip(),
            sinopse.strip(),
            titulo_id
        ))


def remover_titulo(titulo_id):
    with conectar() as conexao:
        conexao.execute("""
            DELETE FROM titulos
            WHERE id = ?
        """, (titulo_id,))


criar_tabela()
