from modelos.genero import Genero
from modelos.livro import Livro


def main():
    genero = Genero(1, "Fantasia")

    livro = Livro(
        1,
        "O Hobbit",
        1937,
        genero,
        "Um hobbit parte em uma aventura.",
        "1ª",
        "HarperCollins",
    )

    print(genero)
    print(livro)

    livro.lido = True
    print(livro)


if __name__ == "__main__":
    main()
