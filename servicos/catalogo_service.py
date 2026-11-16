from servicos.filtros import FiltroEditora, FiltroGenero, FiltroTexto, aplicar


# Cuida do que o usuário vê sobre os livros: lista, busca, média, populares e livro do dia.
class CatalogoService:
    # Recebe o repositório (injeção de dependência).
    def __init__(self, repo):
        self.__repo = repo

    # Só repassa a lista do repositório.
    def listar(self):
        return self.__repo.listar_livros()

    def obter(self, id_livro):
        return self.__repo.buscar_livro(id_livro)

    # Strategy em ação: cada critério preenchido vira um objeto Filtro, e `aplicar` deixa passar
    # só os livros que passam em TODOS. Para criar um critério novo basta criar outro Filtro.
    def buscar(self, texto="", genero="", editora=""):
        """Monta a lista de filtros pedidos e deixa o módulo de filtros decidir."""
        filtros = []
        if texto.strip():
            filtros.append(FiltroTexto(texto))
        if genero:
            filtros.append(FiltroGenero(genero))
        if editora:
            filtros.append(FiltroEditora(editora))
        return aplicar(filtros, self.__repo.listar_livros())

    # Média simples das notas; None quando ninguém avaliou (evita dividir por zero).
    def media(self, livro):
        """Média das notas do livro, ou None se ninguém avaliou ainda."""
        notas = [a.nota for a in self.__repo.listar_avaliacoes(livro)]
        return sum(notas) / len(notas) if notas else None

    # Livros com avaliação, do de maior média para o de menor, cortando na quantidade pedida ([:quantidade]).
    def populares(self, quantidade=6):
        avaliados = [l for l in self.__repo.listar_livros() if self.media(l) is not None]
        return sorted(avaliados, key=self.media, reverse=True)[:quantidade]

    # toordinal() transforma a data num número inteiro de dias; o resto da divisão pelo total de livros
    # escolhe a posição. Mesmo dia = mesmo livro, sem precisar guardar nada.
    def livro_do_dia(self, dia):
        """Um livro por dia: o mesmo o dia inteiro, e outro no dia seguinte."""
        livros = self.__repo.listar_livros()
        return livros[dia.toordinal() % len(livros)]

    # Só os nomes (texto), para preencher as listas de filtro da tela.
    def generos(self):
        return [g.nome for g in self.__repo.listar_generos()]

    def editoras(self):
        return [e.nome for e in self.__repo.listar_editoras()]
