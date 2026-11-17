from abc import ABC, abstractmethod


class Filtro(ABC):
    """Strategy: cada filtro é uma regra diferente para responder 'este item passa?'."""

    @abstractmethod
    def passa(self, item) -> bool:
        ...

#filtros do catálogo: o item é um Livro

class FiltroTexto(Filtro):
    def __init__(self, texto):
        self.__texto = texto.strip().lower()

    def passa(self, livro):
        campos = [livro.nome, livro.autor.nome, livro.genero.nome, livro.editora.nome]
        return any(self.__texto in campo.lower() for campo in campos)


class FiltroGenero(Filtro):
    def __init__(self, nome):
        self.__nome = nome.lower()

    def passa(self, livro):
        return livro.genero.nome.lower() == self.__nome


class FiltroEditora(Filtro):
    def __init__(self, nome):
        self.__nome = nome.lower()

    def passa(self, livro):
        return livro.editora.nome.lower() == self.__nome


#filtros da estante: o item é um registro Estante

class FiltroTodos(Filtro):
    def passa(self, registro):
        return True


class FiltroLido(Filtro):
    def passa(self, registro):
        return registro.lido


class FiltroFavorito(Filtro):
    def passa(self, registro):
        return registro.favorito


class FiltroQueroLer(Filtro):
    def passa(self, registro):
        return registro.quer_ler


FILTROS_ESTANTE = {
    "todos": FiltroTodos,
    "lidos": FiltroLido,
    "favoritos": FiltroFavorito,
    "quero-ler": FiltroQueroLer,
}


def aplicar(filtros, itens):
    """Devolve só os itens que passam em todos os filtros."""
    return [item for item in itens if all(f.passa(item) for f in filtros)]
