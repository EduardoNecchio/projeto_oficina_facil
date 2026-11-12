"""Testes básicos de integração do Oficina Fácil (biblioteca padrão unittest)."""
import os
import sqlite3
import tempfile
import unittest

from app import create_app
import db_sql as sql


class OficinaFacilTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = os.path.join(self.temp_dir.name, "teste_oficina.db")
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "teste",
            "DATABASE": self.database,
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            sql.init_db()

    def tearDown(self):
        self.temp_dir.cleanup()

    def cadastrar_cliente(self, nome="Eduardo Teste", email="eduardo@teste.com"):
        return self.client.post("/clientes/novo", data={
            "nome": nome,
            "telefone": "11999990000",
            "email": email,
        }, follow_redirects=True)

    def test_pagina_inicial_e_rota_com_parametro(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Controle sua oficina", resposta.data)
        saudacao = self.client.get("/ola/Maria")
        self.assertEqual(saudacao.status_code, 200)
        self.assertIn("Maria".encode(), saudacao.data)

    def test_criar_editar_detalhar_e_excluir_cliente(self):
        resposta = self.cadastrar_cliente()
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Eduardo Teste", resposta.data)

        with self.app.app_context():
            cliente = sql.get_db().execute(
                "SELECT id_cliente FROM clientes WHERE email = ?", ("eduardo@teste.com",)
            ).fetchone()
            id_cliente = cliente["id_cliente"]

        detalhe = self.client.get(f"/clientes/{id_cliente}")
        self.assertEqual(detalhe.status_code, 200)
        self.assertIn(b"DETALHE DO CADASTRO", detalhe.data)

        edicao = self.client.post(f"/clientes/{id_cliente}/editar", data={
            "nome": "Eduardo Atualizado",
            "telefone": "11988887777",
            "email": "eduardo@teste.com",
        }, follow_redirects=True)
        self.assertEqual(edicao.status_code, 200)
        self.assertIn(b"Eduardo Atualizado", edicao.data)

        exclusao = self.client.post(f"/clientes/{id_cliente}/excluir", follow_redirects=True)
        self.assertEqual(exclusao.status_code, 200)
        self.assertIn(b"Nenhum cliente cadastrado", exclusao.data)

    def test_email_duplicado_mostra_mensagem(self):
        self.cadastrar_cliente("Primeiro", "igual@teste.com")
        resposta = self.client.post("/clientes/novo", data={
            "nome": "Segundo", "email": "igual@teste.com"
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("já está cadastrado".encode(), resposta.data)

    def test_chaves_estrangeiras_e_criacao_de_ordem(self):
        self.cadastrar_cliente()
        with self.app.app_context():
            db = sql.get_db()
            id_cliente = db.execute("SELECT id_cliente FROM clientes").fetchone()[0]
            db.execute(
                "INSERT INTO veiculos (id_cliente, marca, modelo, placa, ano) VALUES (?, ?, ?, ?, ?)",
                (id_cliente, "Honda", "Civic", "ABC1D23", 2022),
            )
            db.execute(
                "INSERT INTO servicos (nome, descricao, preco) VALUES (?, ?, ?)",
                ("Troca de óleo", "Troca de óleo e filtro", 150.0),
            )
            db.commit()

        resposta = self.client.post("/ordens/nova", data={
            "id_veiculo": "1", "servicos": ["1"], "observacoes": "Teste de ordem"
        }, follow_redirects=True)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Ordem #1", resposta.data)
        self.assertIn(b"Troca de \xc3\xb3leo", resposta.data)

        with self.app.app_context():
            db = sql.get_db()
            self.assertEqual(db.execute("SELECT COUNT(*) FROM os_servicos").fetchone()[0], 1)
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM clientes WHERE id_cliente = ?", (1,))


    def test_crud_basico_de_veiculo_e_servico(self):
        self.cadastrar_cliente("Cliente Oficina", "oficina@teste.com")

        veiculo = self.client.post("/veiculos/novo", data={
            "id_cliente": "1", "marca": "Honda", "modelo": "Fit",
            "placa": "ABC1D23", "ano": "2021",
        }, follow_redirects=True)
        self.assertEqual(veiculo.status_code, 200)
        self.assertIn(b"Honda Fit", veiculo.data)

        edicao_veiculo = self.client.post("/veiculos/1/editar", data={
            "id_cliente": "1", "marca": "Honda", "modelo": "City",
            "placa": "ABC1D23", "ano": "2022",
        }, follow_redirects=True)
        self.assertEqual(edicao_veiculo.status_code, 200)
        self.assertIn(b"Honda City", edicao_veiculo.data)

        servico = self.client.post("/servicos/novo", data={
            "nome": "Revisão", "descricao": "Revisão preventiva", "preco": "220.50"
        }, follow_redirects=True)
        self.assertEqual(servico.status_code, 200)
        self.assertIn("220.50".encode(), servico.data)

        edicao_servico = self.client.post("/servicos/1/editar", data={
            "nome": "Revisão completa", "descricao": "Revisão geral", "preco": "300.00"
        }, follow_redirects=True)
        self.assertEqual(edicao_servico.status_code, 200)
        self.assertIn("Revisão completa".encode(), edicao_servico.data)

    def test_nome_com_caracteres_sql_nao_executa_sql(self):
        texto = "Cliente '; DROP TABLE clientes; --"
        resposta = self.cadastrar_cliente(texto, "sql@teste.com")
        self.assertEqual(resposta.status_code, 200)
        with self.app.app_context():
            db = sql.get_db()
            resultado = db.execute(
                "SELECT nome FROM clientes WHERE email = ?", ("sql@teste.com",)
            ).fetchone()
            quantidade = db.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'clientes'"
            ).fetchone()[0]
        self.assertEqual(resultado["nome"], texto)
        self.assertEqual(quantidade, 1)

    def test_pagina_404_para_registro_inexistente(self):
        resposta = self.client.get("/clientes/999")
        self.assertEqual(resposta.status_code, 404)
        self.assertIn(b"N\xc3\xa3o encontramos esta p\xc3\xa1gina", resposta.data)


if __name__ == "__main__":
    unittest.main()
