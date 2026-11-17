from flask import Blueprint, render_template

paginas = Blueprint("paginas", __name__)


@paginas.get("/")
def inicio():
    return render_template("inicio.html")


@paginas.get("/login")
def login():
    return render_template("login.html")


@paginas.get("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@paginas.get("/buscar")
def buscar():
    return render_template("buscar.html")


@paginas.get("/estante")
def estante():
    return render_template("estante.html")


@paginas.get("/perfil")
def perfil():
    return render_template("perfil.html")


@paginas.get("/livro/<int:id_livro>")
def livro(id_livro):
    return render_template("livro.html", id_livro=id_livro)


@paginas.get("/livro/<int:id_livro>/avaliar")
def avaliar(id_livro):
    return render_template("avaliar.html", id_livro=id_livro)
