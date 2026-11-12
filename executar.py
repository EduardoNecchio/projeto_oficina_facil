"""Executa um arquivo .sql no banco oficina.db e mostra cada resultado.

Uso (na pasta do projeto):
    python executar.py inclusoes.sql
    python executar.py consultas.sql
    python executar.py testes_regras.sql

Opcionalmente, informe um caminho de banco como segundo argumento:
    python executar.py consultas.sql outro_banco.db
"""
from pathlib import Path
import sqlite3
import sys

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "oficina.db"


def executar_comando(conn, comando):
    comando = comando.strip()
    if not comando or comando.startswith("--"):
        return
    primeira_linha = next((linha.strip() for linha in comando.splitlines() if linha.strip()), "SQL")
    print(f"\n>> {primeira_linha[:90]}")
    try:
        cursor = conn.execute(comando)
        if cursor.description:
            colunas = [coluna[0] for coluna in cursor.description]
            print(" | ".join(colunas))
            for linha in cursor.fetchall():
                print(" | ".join(str(valor) if valor is not None else "NULL" for valor in linha))
        else:
            print(f"OK ({cursor.rowcount} linha(s) afetada(s))")
        conn.commit()
    except sqlite3.Error as erro:
        conn.rollback()
        print(f"ERRO: {erro}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python executar.py arquivo.sql [banco.db]")
        raise SystemExit(2)

    arquivo_sql = Path(sys.argv[1])
    if not arquivo_sql.is_absolute():
        arquivo_sql = (Path.cwd() / arquivo_sql).resolve()
        if not arquivo_sql.exists():
            arquivo_sql = (BASE_DIR / sys.argv[1]).resolve()
    if not arquivo_sql.is_file():
        print(f"Arquivo SQL não encontrado: {arquivo_sql}")
        raise SystemExit(2)

    banco = Path(sys.argv[2]).expanduser() if len(sys.argv) >= 3 else DEFAULT_DB
    if not banco.is_absolute():
        banco = (Path.cwd() / banco).resolve()

    print(f"Banco: {banco}")
    print(f"Arquivo SQL: {arquivo_sql}")
    conn = sqlite3.connect(banco)
    conn.execute("PRAGMA foreign_keys = ON")

    buffer = ""
    try:
        for linha in arquivo_sql.read_text(encoding="utf-8").splitlines():
            # Comentários e linhas vazias não entram no buffer: assim um comentário
            # antes do INSERT não faz o executor descartar o comando inteiro.
            if not linha.strip() or linha.strip().startswith("--"):
                continue
            buffer += linha + "\n"
            if sqlite3.complete_statement(buffer):
                executar_comando(conn, buffer)
                buffer = ""
        if buffer.strip():
            print(f"ERRO: comando SQL incompleto no final do arquivo: {buffer.strip()[:100]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
