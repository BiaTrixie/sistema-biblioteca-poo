from datetime import date

from modelos.autora import Autora
from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario
from modelos.editora import Editora
from modelos.estante import Estante
from modelos.genero import Genero
from modelos.livro import Livro
from modelos.usuario import Usuario
from repositorios.repositorio_memoria import RepositorioMemoria

# nome, ano, genero, editora, autora
LIVROS = [
    ("O Hobbit", 1937, "Fantasia", "HarperCollins", "J. R. R. Tolkien"),
    ("Orgulho e Preconceito", 1813, "Romance", "Companhia das Letras", "Jane Austen"),
    ("Cem Anos de Solidão", 1967, "Realismo", "Record", "Gabriel García Márquez"),
    ("A Hora da Estrela", 1977, "Ficção", "Rocco", "Clarice Lispector"),
    ("O Nome do Vento", 2007, "Fantasia", "Arqueiro", "Patrick Rothfuss"),
    ("Circe", 2018, "Mitologia", "Bloomsbury", "Madeline Miller"),
]


def _achar(lista, nome):
    """Devolve o item com esse nome; se não existir ainda, devolve None."""
    return next((item for item in lista if item.nome == nome), None)


def criar_repositorio():
    """Monta o repositório com os mesmos dados que aparecem no protótipo."""
    repo = RepositorioMemoria()

    for nome, ano, nome_genero, nome_editora, nome_autora in LIVROS:
        genero = _achar(repo.generos, nome_genero)
        if genero is None:
            genero = Genero(repo.proximo_id(repo.generos), nome_genero)
            repo.generos.append(genero)

        editora = _achar(repo.editoras, nome_editora)
        if editora is None:
            editora = Editora(repo.proximo_id(repo.editoras), nome_editora)
            repo.editoras.append(editora)

        autora = _achar(repo.autoras, nome_autora)
        if autora is None:
            autora = Autora(repo.proximo_id(repo.autoras), nome_autora)
            repo.autoras.append(autora)

        editora.adicionar_autora(autora)
        autora.adicionar_editora(editora)
        sinopse = f"{nome}, de {nome_autora}."
        repo.livros.append(
            Livro(repo.proximo_id(repo.livros), nome, ano, genero, sinopse, "1ª", editora, autora)
        )

    repo.livros[0].sinopse = (
        "Um hobbit parte em uma aventura. Bilbo Bolseiro deixa o Condado, atravessa "
        "terras desconhecidas e descobre que coragem também cabe numa casa pequena."
    )

    ana = Usuario(1, "Ana", "ana@email.com", "123456")
    beto = Usuario(2, "Beto", "beto@email.com", "123456")
    carla = Usuario(3, "Carla", "carla@email.com", "123456")
    repo.usuarios.extend([ana, beto, carla])

    hobbit, orgulho, cem_anos, hora, nome_vento, circe = repo.livros

    # Estante da Ana: 6 livros, 2 favoritos, 3 quero ler (como na tela "Minha estante")
    registros = [
        (hobbit, True, False, True),
        (orgulho, False, True, False),
        (cem_anos, True, False, True),
        (hora, False, False, True),
        (nome_vento, False, True, False),
        (circe, False, True, False),
    ]
    for livro, favorito, quer_ler, lido in registros:
        id_novo = repo.proximo_id(repo.estantes)
        repo.estantes.append(Estante(id_novo, ana, livro, favorito, quer_ler, lido))

    # (usuario, livro, nota, data, comentario)
    avaliacoes = [
        (ana, hobbit, 5, date(2026, 9, 25), "Recomendo."),
        (ana, cem_anos, 5, date(2026, 9, 21), ""),
        (ana, hora, 4, date(2026, 9, 22), ""),
        (beto, orgulho, 5, date(2026, 9, 18), ""),
        (carla, orgulho, 4, date(2026, 9, 19), ""),
        (beto, hora, 5, date(2026, 9, 20), ""),
        (beto, nome_vento, 4, date(2026, 9, 17), ""),
        (carla, nome_vento, 5, date(2026, 9, 18), ""),
        (carla, circe, 5, date(2026, 9, 16), ""),
    ]
    for usuario, livro, nota, data, texto in avaliacoes:
        id_novo = repo.proximo_id(repo.avaliacoes)
        repo.avaliacoes.append(Avaliacao(id_novo, nota, data, usuario, livro, texto))

    repo.comentarios.append(
        Comentario(1, "Aventura excelente.", date(2026, 9, 25), ana, hobbit)
    )
    repo.comentarios.append(
        Comentario(2, "Um livro curto que fica o mês inteiro na cabeça.",
                   date(2026, 9, 24), ana, hora, numero_likes=12)
    )
    return repo
