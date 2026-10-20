import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "cinetrack.db"


def conectar():
    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
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

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS diario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo_id INTEGER NOT NULL,
                data_assistido TEXT NOT NULL,
                nota REAL,
                comentario TEXT,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (titulo_id)
                    REFERENCES titulos(id)
                    ON DELETE CASCADE
            )
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


def adicionar_registro_diario(
    titulo_id,
    data_assistido,
    nota,
    comentario
):
    with conectar() as conexao:
        conexao.execute("""
            INSERT INTO diario (
                titulo_id,
                data_assistido,
                nota,
                comentario
            )
            VALUES (?, ?, ?, ?)
        """, (
            titulo_id,
            data_assistido,
            nota,
            comentario.strip() if comentario else ""
        ))

        conexao.execute("""
            UPDATE titulos
            SET status = 'Concluído'
            WHERE id = ?
        """, (titulo_id,))


def listar_diario():
    with conectar() as conexao:
        registros = conexao.execute("""
            SELECT
                diario.id,
                diario.titulo_id,
                diario.data_assistido,
                diario.nota,
                diario.comentario,
                diario.criado_em,
                titulos.nome,
                titulos.categoria,
                titulos.ano,
                titulos.poster
            FROM diario
            INNER JOIN titulos
                ON titulos.id = diario.titulo_id
            ORDER BY
                diario.data_assistido DESC,
                diario.id DESC
        """).fetchall()

        return [dict(registro) for registro in registros]


def remover_registro_diario(registro_id):
    with conectar() as conexao:
        conexao.execute("""
            DELETE FROM diario
            WHERE id = ?
        """, (registro_id,))


def remover_titulo(titulo_id):
    with conectar() as conexao:
        conexao.execute("""
            DELETE FROM titulos
            WHERE id = ?
        """, (titulo_id,))


criar_tabela()
