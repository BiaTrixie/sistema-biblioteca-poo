from datetime import date

from modelos.autora import Autora
from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario
from modelos.editora import Editora
from modelos.estante import Estante
from modelos.genero import Genero
from modelos.livro import Livro
from modelos.usuario import Usuario


def main():
    genero = Genero(1, "Fantasia")
    editora = Editora(1, "HarperCollins")
    autora = Autora(1, "J. R. R. Tolkien")

    editora.adicionar_autora(autora)
    autora.adicionar_editora(editora)

    livro = Livro(
        1,
        "O Hobbit",
        1937,
        genero,
        "Um hobbit parte em uma aventura.",
        "1ª",
        editora,
    )

    usuario = Usuario(1, "Ana", "ana@email.com", "1234")

    comentario = Comentario(
        1,
        "Aventura excelente.",
        date(2026, 9, 25),
    )

    avaliacao = Avaliacao(
        1,
        5,
        date(2026, 9, 25),
        "Recomendo.",
    )

    estante = Estante(1, usuario, livro, favorito=True, quer_ler=False)

    print(genero)
    print(editora)
    print(autora)
    print(livro)
    print(usuario)
    print(comentario)
    print(avaliacao)
    print(estante)

    livro.lido = True
    print(livro)
    print(estante)


if __name__ == "__main__":
    main()
