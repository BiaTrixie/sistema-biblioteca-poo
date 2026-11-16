from datetime import date
from functools import cache

from werkzeug.security import generate_password_hash

from modelos.autora import Autora
from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario
from modelos.editora import Editora
from modelos.estante import Estante
from modelos.genero import Genero
from modelos.livro import Livro
from modelos.usuario import Usuario
from repositorios.repositorio_memoria import RepositorioMemoria

# SEMENTE = os dados iniciais do protótipo. Roda uma vez, quando o banco está vazio, para o
# sistema já abrir com livros, contas, estante e avaliações para mostrar.
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
    ("Curiosidades das Árvores", 2015, "Natureza", "Copa Editorial", "Iara Cedro",
     "Por que as árvores têm anéis? Elas conversam pelas raízes? Curiosidades curtas "
     "sobre como as árvores vivem, se comunicam e envelhecem."),
    ("Poeira de Estrelas", 2021, "Ciência", "Órbita Livros", "Sofia Órbita",
     "Do Big Bang ao seu corpo: um passeio pelo cosmos que mostra que os átomos "
     "de cada pessoa nasceram dentro de estrelas."),
]


@cache
def _senha_padrao():
    """Hash de '123456', calculado uma vez só (cada hash leva uns 130 ms)."""
    return generate_password_hash("123456")


# É a porta de entrada: devolve um repositório já com dados. Sem argumento, cria um de memória.
def criar_repositorio(repo=None):
    """Devolve o repositório pronto. Se estiver vazio, enche com os dados do protótipo."""
    repo = repo or RepositorioMemoria()
    with repo.transacao():
        if repo.esta_vazio():  # conferido dentro da transação, para duas execuções não semearem juntas
            _semear(repo)
    return repo


# Evita duplicar gênero, editora e autora: dois livros de "Fantasia" usam o MESMO objeto Genero.
def _obter(repo, cache, classe, colecao, nome):
    """Reaproveita o item com esse nome; se for novo, cria e salva."""
    if nome not in cache:
        cache[nome] = classe(repo.proximo_id(colecao), nome)
        repo.salvar(cache[nome])
    return cache[nome]


# Cria e salva tudo, na ordem das dependências: primeiro gênero/editora/autora, depois os livros
# (que apontam para eles), depois contas, estante, avaliações e comentários.
def _semear(repo):
    generos, editoras, autoras, livros = {}, {}, {}, []

    for nome, ano, nome_genero, nome_editora, nome_autora, sinopse in LIVROS:
        genero = _obter(repo, generos, Genero, "generos", nome_genero)
        editora = _obter(repo, editoras, Editora, "editoras", nome_editora)
        autora = _obter(repo, autoras, Autora, "autoras", nome_autora)
        if autora not in editora.autores:
            editora.adicionar_autora(autora)
            autora.adicionar_editora(editora)
            repo.salvar(editora)
        livro = Livro(repo.proximo_id("livros"), nome, ano, genero, sinopse, "1ª", editora, autora)
        repo.salvar(livro)
        livros.append(livro)

    # todas as contas da semente usam a senha 123456
    # (enumerate(..., start=1) numera as contas a partir do id 1)
    contas = [("Ana", "ana@email.com"), ("Beto", "beto@email.com"), ("Carla", "carla@email.com"),
              ("Roberto", "roberto@email.com"), ("Juliana", "juliana@email.com"),
              ("Lucas Arruda", "lucas@email.com")]
    usuarios = [Usuario(i, nome, email, _senha_padrao(), senha_protegida=True)
                for i, (nome, email) in enumerate(contas, start=1)]
    for usuario in usuarios:
        repo.salvar(usuario)
    ana, beto, carla, roberto, juliana, lucas = usuarios

    # Desempacota a lista: dá um nome a cada livro, na mesma ordem em que estão em LIVROS.
    hobbit, orgulho, cem_anos, hora, nome_vento, circe, baleias, floresta, cosmos = livros

    # Cada tupla é (livro, favorito, quer_ler, lido), mesma ordem do construtor de Estante.
    # Repare que lido e quer_ler nunca aparecem juntos (a Estante recusaria).
    # Estante da Ana: 6 livros, 2 favoritos, 3 quero ler (como na tela "Minha estante")
    registros = [
        (hobbit, True, False, True),
        (orgulho, False, True, False),
        (cem_anos, True, False, True),
        (hora, False, False, True),
        (nome_vento, False, True, False),
        (circe, False, True, False),
    ]
    for numero, (livro, favorito, quer_ler, lido) in enumerate(registros, start=1):
        repo.salvar(Estante(numero, ana, livro, favorito, quer_ler, lido))

    # usuário, livro, nota, data, comentário
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
        (juliana, baleias, 5, date(2026, 10, 12), "É o melhor livro que já li na minha vida."),
    ]
    for numero, (usuario, livro, nota, data, texto) in enumerate(avaliacoes, start=1):
        repo.salvar(Avaliacao(numero, nota, data, usuario, livro, texto))

    # id, texto, data, usuário, livro, quem curtiu
    comentarios = [
        (1, "Aventura excelente.", date(2026, 9, 25), ana, hobbit, set()),
        (2, "Um livro curto que fica o mês inteiro na cabeça.", date(2026, 9, 24), ana, hora,
         {beto.id, carla.id, roberto.id, juliana.id, lucas.id}),
        (3, "Eu amo árvores, oh my god.", date(2026, 10, 11), lucas, floresta, set()),
    ]
    for id_comentario, texto, data, usuario, livro, curtidas in comentarios:
        repo.salvar(Comentario(id_comentario, texto, data, usuario, livro, curtidas))
