from datetime import date
from pathlib import Path

from flask import abort, flash, redirect, render_template, request, session, url_for

from app import app, sistema


def usuario_logado():
    return sistema.conta.buscar_por_id(session.get("usuario_id"))


@app.context_processor
def dados_das_paginas():
    """Deixa o usuário e a função da média disponíveis em todos os templates."""
    return {"usuario": usuario_logado(), "media": sistema.catalogo.media}


@app.template_global()
def capa_url(livro):
    """Endereço da capa do livro (static/img/capas/<id>.svg); sem arquivo, usa a capa padrão."""
    nome = f"img/capas/{livro.id}.svg"
    if not (Path(app.static_folder) / nome).exists(): 
        nome = "img/capas/padrao.svg"
    return url_for("static", filename=nome)


@app.before_request
def exigir_login():
    livres = ("login", "cadastro", "static")
    if request.endpoint not in livres and usuario_logado() is None:
        return redirect(url_for("login"))


def buscar_livro(id_livro):
    livro = sistema.catalogo.obter(id_livro)
    if livro is None:
        abort(404)
    return livro


# --- conta ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            usuario = sistema.conta.entrar(request.form["email"], request.form["senha"])
            session["usuario_id"] = usuario.id
            return redirect(url_for("inicio"))
        except ValueError as erro:
            flash(str(erro))
    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        try:
            usuario = sistema.conta.cadastrar(
                request.form["nome"], request.form["email"], request.form["senha"]
            )
            session["usuario_id"] = usuario.id
            return redirect(url_for("inicio"))
        except ValueError as erro:
            flash(str(erro))
    return render_template("cadastro.html")


@app.route("/sair", methods=["POST"])
def sair():
    session.clear()
    return redirect(url_for("login"))


@app.route("/perfil")
def perfil():
    pessoa = usuario_logado()
    avaliacoes, comentarios = sistema.avaliacao.do_usuario(pessoa)
    return render_template(
        "perfil.html",
        resumo=sistema.estante.resumo(pessoa),
        qtd_avaliacoes=len(avaliacoes),
        qtd_comentarios=len(comentarios),
    )


# --- telas principais ---

@app.route("/")
def inicio():
    destaque = sistema.catalogo.livro_do_dia(date.today())
    return render_template(
        "inicio.html",
        destaque=destaque,
        na_estante=sistema.estante.registro(usuario_logado(), destaque) is not None,
        populares=sistema.catalogo.populares(),
        diario=sistema.avaliacao.diario_recente(),
        resumo=sistema.estante.resumo(usuario_logado()),
    )


@app.route("/buscar")
def buscar():
    texto = request.args.get("q", "")
    genero = request.args.get("genero", "")
    editora = request.args.get("editora", "")
    return render_template(
        "buscar.html",
        livros=sistema.catalogo.buscar(texto, genero, editora),
        texto=texto,
        genero=genero,
        editora=editora,
        generos=sistema.catalogo.generos(),
        editoras=sistema.catalogo.editoras(),
    )


@app.route("/estante")
def estante():
    filtro = request.args.get("filtro", "todos")
    try:
        registros = sistema.estante.listar(usuario_logado(), filtro)
    except ValueError:
        abort(404)
    return render_template(
        "estante.html",
        registros=registros,
        filtro=filtro,
        resumo=sistema.estante.resumo(usuario_logado()),
    )


# --- página do livro e ações ---

@app.route("/livro/<int:id_livro>")
def livro(id_livro):
    livro = buscar_livro(id_livro)
    avaliacoes, comentarios = sistema.avaliacao.do_livro(livro)
    return render_template(
        "livro.html",
        livro=livro,
        avaliacoes=avaliacoes,
        comentarios=comentarios,
        registro=sistema.estante.registro(usuario_logado(), livro),
        meu_comentario=sistema.avaliacao.comentario_de(usuario_logado(), livro),
    )


@app.route("/livro/<int:id_livro>/status", methods=["POST"])
def mudar_status(id_livro):
    livro = buscar_livro(id_livro)
    try:
        sistema.estante.alternar(usuario_logado(), livro, request.form["status"])
    except ValueError as erro:
        flash(str(erro))
    return redirect(url_for("livro", id_livro=id_livro))


@app.route("/livro/<int:id_livro>/avaliar", methods=["GET", "POST"])
def avaliar(id_livro):
    livro = buscar_livro(id_livro)
    anterior = sistema.avaliacao.avaliacao_de(usuario_logado(), livro)
    if request.method == "POST":
        try:
            sistema.avaliacao.avaliar(
                usuario_logado(), livro, int(request.form["nota"]), request.form["texto"]
            )
            return redirect(url_for("livro", id_livro=id_livro))
        except ValueError as erro:
            flash(str(erro))
    return render_template("avaliar.html", livro=livro, anterior=anterior)


@app.route("/livro/<int:id_livro>/comentar", methods=["POST"])
def comentar(id_livro):
    livro = buscar_livro(id_livro)
    try:
        sistema.avaliacao.comentar(usuario_logado(), livro, request.form["texto"])
    except ValueError as erro:
        flash(str(erro))
    return redirect(url_for("livro", id_livro=id_livro))


@app.route("/comentario/<int:id_comentario>/curtir", methods=["POST"])
def curtir(id_comentario):
    try:
        comentario = sistema.avaliacao.curtir(id_comentario, usuario_logado())
    except ValueError:
        abort(404)
    return redirect(url_for("livro", id_livro=comentario.livro.id))
