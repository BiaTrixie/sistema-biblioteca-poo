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

# nome, ano, gênero, editora, autora, sinopse (os 3 últimos livros são inventados)
LIVROS = [
    ("O Hobbit", 1937, "Fantasia", "HarperCollins", "J. R. R. Tolkien",
     "Um hobbit parte em uma aventura. Bilbo Bolseiro deixa o Condado, atravessa "
     "terras desconhecidas e descobre que coragem também cabe numa casa pequena."),
    ("Orgulho e Preconceito", 1813, "Romance", "Companhia das Letras", "Jane Austen",
     "Elizabeth Bennet e o orgulhoso Sr. Darcy aprendem, entre bailes e mal-entendidos, "
     "que a primeira impressão quase nunca é a última."),
    ("Cem Anos de Solidão", 1967, "Realismo", "Record", "Gabriel García Márquez",
     "A saga da família Buendía em Macondo, uma vila onde o extraordinário acontece "
     "todo dia e a solidão atravessa as gerações."),
    ("A Hora da Estrela", 1977, "Ficção", "Rocco", "Clarice Lispector",
     "Macabéa, uma jovem nordestina no Rio de Janeiro, leva uma vida pequena sem "
     "perceber o quanto ela importa."),
    ("O Nome do Vento", 2007, "Fantasia", "Arqueiro", "Patrick Rothfuss",
     "Kvothe, músico lendário e dono de uma taverna pacata, conta a própria história: "
     "da infância numa trupe de artistas ao mistério dos nomes das coisas."),
    ("Circe", 2018, "Mitologia", "Bloomsbury", "Madeline Miller",
     "Filha de um deus, Circe é exilada numa ilha e descobre, na solidão, "
     "o poder das ervas e da feitiçaria."),
    ("O Canto das Baleias", 2019, "Natureza", "Maré Alta", "Helena Maré",
     "Uma bióloga marinha passa um inverno no oceano gravando o canto das baleias "
     "e descobre que elas guardam a memória do mar."),
    ("A Floresta que Lembra", 2015, "Natureza", "Copa Editorial", "Iara Cedro",
     "Numa floresta antiga, uma guarda-florestal aprende com as árvores, ligadas "
     "por raízes, que ninguém cresce sozinho."),
    ("Poeira de Estrelas", 2021, "Ciência", "Órbita Livros", "Sofia Órbita",
     "Do Big Bang ao seu corpo: um passeio pelo cosmos que mostra que os átomos "
     "de cada pessoa nasceram dentro de estrelas."),
]


def _achar(lista, nome):
    """Devolve o item com esse nome; se não existir ainda, devolve None."""
    return next((item for item in lista if item.nome == nome), None)


def criar_repositorio():
    """Monta o repositório com os mesmos dados que aparecem no protótipo."""
    repo = RepositorioMemoria()

    for nome, ano, nome_genero, nome_editora, nome_autora, sinopse in LIVROS:
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
        repo.livros.append(
            Livro(repo.proximo_id(repo.livros), nome, ano, genero, sinopse, "1ª", editora, autora)
        )

    ana = Usuario(1, "Ana", "ana@email.com", "123456")
    beto = Usuario(2, "Beto", "beto@email.com", "123456")
    carla = Usuario(3, "Carla", "carla@email.com", "123456")
    roberto = Usuario(4, "Roberto", "roberto@email.com", "123456")
    repo.usuarios.extend([ana, beto, carla, roberto])

    hobbit, orgulho, cem_anos, hora, nome_vento, circe, baleias, floresta, cosmos = repo.livros

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
        (beto, baleias, 5, date(2026, 10, 2), "Fiquei horas ouvindo as gravações do livro."),
        (carla, baleias, 4, date(2026, 10, 3), ""),
        (carla, floresta, 4, date(2026, 10, 5), ""),
        (roberto, cosmos, 5, date(2026, 10, 8), "Faz a gente se sentir pequeno e feliz."),
        (beto, cosmos, 4, date(2026, 10, 9), ""),
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
