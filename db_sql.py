"""Camada de acesso ao banco relacional (SQLite) do Oficina Fácil.

As rotas do Flask não executam SQL diretamente: elas chamam as funções deste módulo.
"""
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def get_db():
    """Abre uma conexão por contexto/requisição e a guarda em flask.g."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    """Fecha a conexão ao final do contexto da aplicação."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Cria novamente as tabelas descritas em schema.sql."""
    db = get_db()
    db.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
    db.commit()


# --------------------------------------------------------------------- CLIENTES
def listar_clientes():
    sql = """
        SELECT c.*, COUNT(v.id_veiculo) AS total_veiculos
        FROM clientes c
        LEFT JOIN veiculos v ON v.id_cliente = c.id_cliente
        GROUP BY c.id_cliente
        ORDER BY c.nome
    """
    return get_db().execute(sql).fetchall()


def buscar_cliente(id_cliente):
    return get_db().execute(
        "SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,)
    ).fetchone()


def criar_cliente(dados):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)", dados
    )
    db.commit()
    return cursor.lastrowid


def atualizar_cliente(dados):
    db = get_db()
    db.execute(
        "UPDATE clientes SET nome = ?, telefone = ?, email = ? WHERE id_cliente = ?",
        dados,
    )
    db.commit()


def excluir_cliente(id_cliente):
    db = get_db()
    db.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
    db.commit()


def listar_veiculos_cliente(id_cliente):
    return get_db().execute(
        "SELECT * FROM veiculos WHERE id_cliente = ? ORDER BY modelo, marca",
        (id_cliente,),
    ).fetchall()


# --------------------------------------------------------------------- VEÍCULOS
def listar_veiculos():
    sql = """
        SELECT v.*, c.nome AS cliente_nome
        FROM veiculos v
        INNER JOIN clientes c ON c.id_cliente = v.id_cliente
        ORDER BY v.modelo, v.marca
    """
    return get_db().execute(sql).fetchall()


def buscar_veiculo(id_veiculo):
    return get_db().execute(
        "SELECT * FROM veiculos WHERE id_veiculo = ?", (id_veiculo,)
    ).fetchone()


def criar_veiculo(dados):
    db = get_db()
    cursor = db.execute(
        """INSERT INTO veiculos (id_cliente, marca, modelo, placa, ano)
           VALUES (?, ?, ?, ?, ?)""",
        dados,
    )
    db.commit()
    return cursor.lastrowid


def atualizar_veiculo(dados):
    db = get_db()
    db.execute(
        """UPDATE veiculos
           SET id_cliente = ?, marca = ?, modelo = ?, placa = ?, ano = ?
           WHERE id_veiculo = ?""",
        dados,
    )
    db.commit()


def excluir_veiculo(id_veiculo):
    db = get_db()
    db.execute("DELETE FROM veiculos WHERE id_veiculo = ?", (id_veiculo,))
    db.commit()


# --------------------------------------------------------------------- SERVIÇOS
def listar_servicos():
    return get_db().execute("SELECT * FROM servicos ORDER BY nome").fetchall()


def buscar_servico(id_servico):
    return get_db().execute(
        "SELECT * FROM servicos WHERE id_servico = ?", (id_servico,)
    ).fetchone()


def criar_servico(dados):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO servicos (nome, descricao, preco) VALUES (?, ?, ?)", dados
    )
    db.commit()
    return cursor.lastrowid


def atualizar_servico(dados):
    db = get_db()
    db.execute(
        "UPDATE servicos SET nome = ?, descricao = ?, preco = ? WHERE id_servico = ?",
        dados,
    )
    db.commit()


def excluir_servico(id_servico):
    db = get_db()
    db.execute("DELETE FROM servicos WHERE id_servico = ?", (id_servico,))
    db.commit()


# --------------------------------------------------------------------- ORDENS DE SERVIÇO
STATUS_OS = ["Aberta", "Em andamento", "Concluída", "Cancelada"]


def listar_ordens(status=None):
    sql = """
        SELECT os.*, v.marca, v.modelo, v.placa,
               c.nome AS cliente_nome
        FROM ordens_servico os
        INNER JOIN veiculos v ON v.id_veiculo = os.id_veiculo
        INNER JOIN clientes c ON c.id_cliente = v.id_cliente
    """
    if status:
        sql += " WHERE os.status = ?"
        return get_db().execute(sql + " ORDER BY os.id_os DESC", (status,)).fetchall()
    return get_db().execute(sql + " ORDER BY os.id_os DESC").fetchall()


def buscar_ordem(id_os):
    sql = """
        SELECT os.*, v.marca, v.modelo, v.placa,
               c.nome AS cliente_nome, c.id_cliente
        FROM ordens_servico os
        INNER JOIN veiculos v ON v.id_veiculo = os.id_veiculo
        INNER JOIN clientes c ON c.id_cliente = v.id_cliente
        WHERE os.id_os = ?
    """
    return get_db().execute(sql, (id_os,)).fetchone()


def criar_ordem(id_veiculo, ids_servicos, observacoes=""):
    """Cria a ordem e seus itens em uma única transação."""
    db = get_db()
    ids_unicos = list(dict.fromkeys(int(item) for item in ids_servicos))
    if not ids_unicos:
        raise ValueError("Selecione ao menos um serviço.")

    try:
        cursor = db.execute(
            "INSERT INTO ordens_servico (id_veiculo, status, valor_total, observacoes) "
            "VALUES (?, 'Aberta', 0, ?)",
            (id_veiculo, observacoes),
        )
        id_os = cursor.lastrowid
        total = 0.0

        for id_servico in ids_unicos:
            servico = db.execute(
                "SELECT preco FROM servicos WHERE id_servico = ?", (id_servico,)
            ).fetchone()
            if servico is None:
                raise ValueError("Um dos serviços selecionados não existe.")
            preco = float(servico["preco"])
            total += preco
            db.execute(
                """INSERT INTO os_servicos
                   (id_os, id_servico, quantidade, valor_unitario)
                   VALUES (?, ?, 1, ?)""",
                (id_os, id_servico, preco),
            )

        db.execute(
            "UPDATE ordens_servico SET valor_total = ?, updated_at = CURRENT_TIMESTAMP "
            "WHERE id_os = ?",
            (total, id_os),
        )
        db.commit()
        return id_os
    except Exception:
        db.rollback()
        raise


def atualizar_status_os(status, id_os):
    db = get_db()
    db.execute(
        "UPDATE ordens_servico SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id_os = ?",
        (status, id_os),
    )
    db.commit()


def excluir_ordem(id_os):
    db = get_db()
    db.execute("DELETE FROM ordens_servico WHERE id_os = ?", (id_os,))
    db.commit()


def listar_itens_ordem(id_os):
    sql = """
        SELECT s.nome, s.descricao, os_s.quantidade, os_s.valor_unitario,
               (os_s.quantidade * os_s.valor_unitario) AS subtotal
        FROM os_servicos os_s
        INNER JOIN servicos s ON s.id_servico = os_s.id_servico
        WHERE os_s.id_os = ?
        ORDER BY s.nome
    """
    return get_db().execute(sql, (id_os,)).fetchall()


def obter_indicadores():
    db = get_db()
    return {
        "clientes": db.execute("SELECT COUNT(*) FROM clientes").fetchone()[0],
        "veiculos": db.execute("SELECT COUNT(*) FROM veiculos").fetchone()[0],
        "ordens_abertas": db.execute(
            "SELECT COUNT(*) FROM ordens_servico WHERE status IN ('Aberta', 'Em andamento')"
        ).fetchone()[0],
        "faturamento": db.execute(
            "SELECT COALESCE(SUM(valor_total), 0) FROM ordens_servico "
            "WHERE status = 'Concluída'"
        ).fetchone()[0],
    }
