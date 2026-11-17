from servicos.filtros import FiltroEditora, FiltroGenero, FiltroTexto, aplicar


class CatalogoService:
    def __init__(self, livros, avaliacoes):
        self.__livros = livros
        self.__avaliacoes = avaliacoes

    def listar(self):
        return self.__livros.listar()

    def obter(self, id_livro):
        return self.__livros.buscar(id_livro)

    def buscar(self, texto="", genero="", editora=""):
        """Monta a lista de filtros pedidos e deixa o módulo de filtros decidir."""
        filtros = []
        if texto.strip():
            filtros.append(FiltroTexto(texto))
        if genero:
            filtros.append(FiltroGenero(genero))
        if editora:
            filtros.append(FiltroEditora(editora))
        return aplicar(filtros, self.__livros.listar())

    def media(self, livro):
        """Média das notas do livro, ou None se ninguém avaliou ainda."""
        notas = [a.nota for a in self.__avaliacoes.listar(livro)]
        return sum(notas) / len(notas) if notas else None

    def populares(self, quantidade=6):
        avaliados = [l for l in self.__livros.listar() if self.media(l) is not None]
        return sorted(avaliados, key=self.media, reverse=True)[:quantidade]

    def livro_do_dia(self, dia):
        """Um livro por dia: o mesmo o dia inteiro, e outro no dia seguinte."""
        livros = self.__livros.listar()
        return livros[dia.toordinal() % len(livros)]

    def generos(self):
        return [g.nome for g in self.__livros.listar_generos()]

    def editoras(self):
        return [e.nome for e in self.__livros.listar_editoras()]
