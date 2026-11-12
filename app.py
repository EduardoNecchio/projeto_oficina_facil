"""Aplicação Flask do Oficina Fácil."""
import math
import os
import re
import sqlite3
from pathlib import Path

import click
from flask import Flask, abort, flash, redirect, render_template, request, url_for

import db_sql as sql


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-oficina-facil-troque-em-producao"),
        DATABASE=os.environ.get("DATABASE", str(Path(__file__).with_name("oficina.db"))),
    )
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(sql.close_db)
    register_cli(app)
    register_routes(app)
    return app


def register_cli(app):
    @app.cli.command("init-db")
    def init_db_command():
        """Recria as tabelas do banco (apaga os dados existentes)."""
        sql.init_db()
        click.echo("Banco Oficina Fácil inicializado com sucesso.")


def register_routes(app):
    @app.route("/")
    def index():
        return render_template(
            "index.html",
            dados=sql.obter_indicadores(),
            ordens=sql.listar_ordens()[:5],
        )

    @app.route("/ola/<nome>")
    def ola(nome):
        return render_template("ola.html", nome=nome)

    @app.route("/sobre")
    def sobre():
        return render_template("sobre.html")

    @app.route("/contato")
    def contato():
        return render_template("contato.html")

    # ---------------------------------------------------------------- CLIENTES
    @app.route("/clientes")
    def clientes():
        return render_template("clientes.html", clientes=sql.listar_clientes())

    @app.route("/clientes/novo", methods=["GET", "POST"])
    def novo_cliente():
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            telefone = request.form.get("telefone", "").strip()
            email = request.form.get("email", "").strip().lower() or None
            if not nome:
                flash("O nome do cliente é obrigatório.", "erro")
            else:
                try:
                    id_cliente = sql.criar_cliente((nome, telefone, email))
                    flash("Cliente cadastrado com sucesso.", "sucesso")
                    return redirect(url_for("detalhe_cliente", id_cliente=id_cliente))
                except sqlite3.IntegrityError:
                    flash("Este e-mail já está cadastrado. Informe outro e-mail.", "erro")
            return render_template("form_cliente.html", cliente=None, valores=request.form)
        return render_template("form_cliente.html", cliente=None, valores={})

    @app.route("/clientes/<int:id_cliente>")
    def detalhe_cliente(id_cliente):
        cliente = sql.buscar_cliente(id_cliente) or abort(404)
        veiculos = sql.listar_veiculos_cliente(id_cliente)
        return render_template("detalhe_cliente.html", cliente=cliente, veiculos=veiculos)

    @app.route("/clientes/<int:id_cliente>/editar", methods=["GET", "POST"])
    def editar_cliente(id_cliente):
        cliente = sql.buscar_cliente(id_cliente) or abort(404)
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            telefone = request.form.get("telefone", "").strip()
            email = request.form.get("email", "").strip().lower() or None
            if not nome:
                flash("O nome do cliente é obrigatório.", "erro")
            else:
                try:
                    sql.atualizar_cliente((nome, telefone, email, id_cliente))
                    flash("Cliente atualizado com sucesso.", "sucesso")
                    return redirect(url_for("detalhe_cliente", id_cliente=id_cliente))
                except sqlite3.IntegrityError:
                    flash("Este e-mail já pertence a outro cliente.", "erro")
            return render_template("form_cliente.html", cliente=cliente, valores=request.form)
        return render_template("form_cliente.html", cliente=cliente, valores={})

    @app.post("/clientes/<int:id_cliente>/excluir")
    def excluir_cliente(id_cliente):
        if sql.buscar_cliente(id_cliente) is None:
            abort(404)
        try:
            sql.excluir_cliente(id_cliente)
            flash("Cliente excluído com sucesso.", "sucesso")
        except sqlite3.IntegrityError:
            flash("Não é possível excluir este cliente: existem veículos vinculados a ele.", "erro")
        return redirect(url_for("clientes"))

    # ---------------------------------------------------------------- VEÍCULOS
    @app.route("/veiculos")
    def veiculos():
        return render_template(
            "veiculos.html", veiculos=sql.listar_veiculos(), clientes=sql.listar_clientes()
        )

    @app.route("/veiculos/novo", methods=["GET", "POST"])
    def novo_veiculo():
        clientes = sql.listar_clientes()
        if request.method == "POST":
            dados, erro = dados_veiculo_do_form()
            if erro:
                flash(erro, "erro")
            else:
                try:
                    sql.criar_veiculo(dados)
                    flash("Veículo cadastrado com sucesso.", "sucesso")
                    return redirect(url_for("veiculos"))
                except sqlite3.IntegrityError:
                    flash("Placa já cadastrada ou proprietário inválido.", "erro")
            return render_template("form_veiculo.html", veiculo=None, clientes=clientes, valores=request.form)
        return render_template("form_veiculo.html", veiculo=None, clientes=clientes, valores={})

    @app.route("/veiculos/<int:id_veiculo>/editar", methods=["GET", "POST"])
    def editar_veiculo(id_veiculo):
        veiculo = sql.buscar_veiculo(id_veiculo) or abort(404)
        clientes = sql.listar_clientes()
        if request.method == "POST":
            dados, erro = dados_veiculo_do_form()
            if erro:
                flash(erro, "erro")
            else:
                try:
                    sql.atualizar_veiculo((*dados, id_veiculo))
                    flash("Veículo atualizado com sucesso.", "sucesso")
                    return redirect(url_for("veiculos"))
                except sqlite3.IntegrityError:
                    flash("Placa já cadastrada ou proprietário inválido.", "erro")
            return render_template("form_veiculo.html", veiculo=veiculo, clientes=clientes, valores=request.form)
        return render_template("form_veiculo.html", veiculo=veiculo, clientes=clientes, valores={})

    @app.post("/veiculos/<int:id_veiculo>/excluir")
    def excluir_veiculo(id_veiculo):
        if sql.buscar_veiculo(id_veiculo) is None:
            abort(404)
        try:
            sql.excluir_veiculo(id_veiculo)
            flash("Veículo excluído com sucesso.", "sucesso")
        except sqlite3.IntegrityError:
            flash("Não é possível excluir um veículo que possui ordens de serviço.", "erro")
        return redirect(url_for("veiculos"))

    # ---------------------------------------------------------------- SERVIÇOS
    @app.route("/servicos")
    def servicos():
        return render_template("servicos.html", servicos=sql.listar_servicos())

    @app.route("/servicos/novo", methods=["GET", "POST"])
    def novo_servico():
        if request.method == "POST":
            dados, erro = dados_servico_do_form()
            if erro:
                flash(erro, "erro")
            else:
                try:
                    sql.criar_servico(dados)
                    flash("Serviço cadastrado com sucesso.", "sucesso")
                    return redirect(url_for("servicos"))
                except sqlite3.IntegrityError:
                    flash("Já existe um serviço com esse nome.", "erro")
            return render_template("form_servico.html", servico=None, valores=request.form)
        return render_template("form_servico.html", servico=None, valores={})

    @app.route("/servicos/<int:id_servico>/editar", methods=["GET", "POST"])
    def editar_servico(id_servico):
        servico = sql.buscar_servico(id_servico) or abort(404)
        if request.method == "POST":
            dados, erro = dados_servico_do_form()
            if erro:
                flash(erro, "erro")
            else:
                try:
                    sql.atualizar_servico((*dados, id_servico))
                    flash("Serviço atualizado com sucesso.", "sucesso")
                    return redirect(url_for("servicos"))
                except sqlite3.IntegrityError:
                    flash("Já existe outro serviço com esse nome.", "erro")
            return render_template("form_servico.html", servico=servico, valores=request.form)
        return render_template("form_servico.html", servico=servico, valores={})

    @app.post("/servicos/<int:id_servico>/excluir")
    def excluir_servico(id_servico):
        if sql.buscar_servico(id_servico) is None:
            abort(404)
        try:
            sql.excluir_servico(id_servico)
            flash("Serviço excluído com sucesso.", "sucesso")
        except sqlite3.IntegrityError:
            flash("Não é possível excluir um serviço que já foi usado em uma ordem.", "erro")
        return redirect(url_for("servicos"))

    # --------------------------------------------------------- ORDENS DE SERVIÇO
    @app.route("/ordens")
    def ordens():
        status = request.args.get("status", "").strip()
        if status not in sql.STATUS_OS:
            status = ""
        ordens = sql.listar_ordens(status or None)
        return render_template("ordens.html", ordens=ordens, status_filtro=status, statuses=sql.STATUS_OS)

    @app.route("/ordens/nova", methods=["GET", "POST"])
    def nova_ordem():
        veiculos = sql.listar_veiculos()
        servicos = sql.listar_servicos()
        if request.method == "POST":
            id_veiculo = request.form.get("id_veiculo", type=int)
            ids_servicos = request.form.getlist("servicos")
            observacoes = request.form.get("observacoes", "").strip()
            if not id_veiculo or sql.buscar_veiculo(id_veiculo) is None:
                flash("Selecione um veículo válido.", "erro")
            elif not ids_servicos:
                flash("Selecione ao menos um serviço.", "erro")
            else:
                try:
                    id_os = sql.criar_ordem(id_veiculo, ids_servicos, observacoes)
                    flash("Ordem de serviço criada com sucesso.", "sucesso")
                    return redirect(url_for("detalhe_ordem", id_os=id_os))
                except (ValueError, sqlite3.IntegrityError):
                    flash("Não foi possível criar a ordem. Confira o veículo e os serviços selecionados.", "erro")
            return render_template("form_ordem.html", veiculos=veiculos, servicos=servicos, valores=request.form, selecionados=request.form.getlist("servicos"))
        return render_template("form_ordem.html", veiculos=veiculos, servicos=servicos, valores={}, selecionados=[])

    @app.route("/ordens/<int:id_os>")
    def detalhe_ordem(id_os):
        ordem = sql.buscar_ordem(id_os) or abort(404)
        itens = sql.listar_itens_ordem(id_os)
        return render_template("detalhe_ordem.html", ordem=ordem, itens=itens)

    @app.post("/ordens/<int:id_os>/status")
    def atualizar_status_os(id_os):
        ordem = sql.buscar_ordem(id_os) or abort(404)
        status = request.form.get("status", "")
        if status not in sql.STATUS_OS:
            flash("Status inválido.", "erro")
        else:
            sql.atualizar_status_os(status, id_os)
            flash("Status da ordem atualizado.", "sucesso")
        return redirect(url_for("detalhe_ordem", id_os=ordem["id_os"]))

    @app.post("/ordens/<int:id_os>/excluir")
    def excluir_ordem(id_os):
        if sql.buscar_ordem(id_os) is None:
            abort(404)
        sql.excluir_ordem(id_os)
        flash("Ordem excluída com sucesso.", "sucesso")
        return redirect(url_for("ordens"))

    @app.errorhandler(404)
    def pagina_nao_encontrada(_error):
        return render_template("404.html"), 404


def dados_veiculo_do_form():
    id_cliente = request.form.get("id_cliente", type=int)
    marca = request.form.get("marca", "").strip()
    modelo = request.form.get("modelo", "").strip()
    placa = re.sub(r"[^A-Za-z0-9]", "", request.form.get("placa", "")).upper()
    ano_texto = request.form.get("ano", "").strip()
    ano = int(ano_texto) if ano_texto.isdigit() else None
    if not id_cliente or not marca or not modelo or len(placa) != 7:
        return None, "Informe proprietário, marca, modelo e uma placa válida com 7 caracteres."
    if ano_texto and ano is None:
        return None, "O ano deve ser um número válido."
    if ano is not None and not (1886 <= ano <= 2100):
        return None, "Informe um ano entre 1886 e 2100."
    return (id_cliente, marca, modelo, placa, ano), None


def dados_servico_do_form():
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    preco_texto = request.form.get("preco", "").strip().replace(",", ".")
    try:
        preco = float(preco_texto)
    except (TypeError, ValueError):
        return None, "Informe um preço válido."
    if not nome:
        return None, "O nome do serviço é obrigatório."
    if not math.isfinite(preco) or preco < 0:
        return None, "Informe um preço válido e não negativo."
    return (nome, descricao, preco), None


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
