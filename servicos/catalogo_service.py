from servicos.filtros import FiltroEditora, FiltroGenero, FiltroTexto, aplicar


class CatalogoService:
    def __init__(self, repo):
        self.__repo = repo

    def listar(self):
        return list(self.__repo.livros)

    def obter(self, id_livro):
        return next((l for l in self.__repo.livros if l.id == id_livro), None)

    def buscar(self, texto="", genero="", editora=""):
        """Monta a lista de filtros pedidos e deixa o módulo de filtros decidir."""
        filtros = []
        if texto.strip():
            filtros.append(FiltroTexto(texto))
        if genero:
            filtros.append(FiltroGenero(genero))
        if editora:
            filtros.append(FiltroEditora(editora))
        return aplicar(filtros, self.__repo.livros)

    def media(self, livro):
        """Média das notas do livro, ou None se ninguém avaliou ainda."""
        notas = [a.nota for a in self.__repo.avaliacoes if a.livro is livro]
        return sum(notas) / len(notas) if notas else None

    def populares(self, quantidade=6):
        avaliados = [l for l in self.__repo.livros if self.media(l) is not None]
        return sorted(avaliados, key=self.media, reverse=True)[:quantidade]

    def livro_do_dia(self, dia):
        """Um livro por dia: o mesmo o dia inteiro, e outro no dia seguinte."""
        livros = self.__repo.livros
        return livros[dia.toordinal() % len(livros)]

    def generos(self):
        return [g.nome for g in self.__repo.generos]

    def editoras(self):
        return [e.nome for e in self.__repo.editoras]
