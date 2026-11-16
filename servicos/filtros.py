from abc import ABC, abstractmethod


# PADRÃO STRATEGY: uma família de regras intercambiáveis. Todas respondem à mesma pergunta,
# passa(item) -> True/False, cada uma do seu jeito. Quem usa o filtro não precisa saber qual é
# (polimorfismo) e dá para acrescentar filtros novos sem mexer no código que já existe.
class Filtro(ABC):
    """Strategy: cada filtro é uma regra diferente para responder 'este item passa?'."""

    @abstractmethod
    def passa(self, item) -> bool:
        ...


# --- filtros do catálogo: o item é um Livro ---

# Procura o texto no título, na autora, no gênero ou na editora (ignora maiúsculas).
class FiltroTexto(Filtro):
    def __init__(self, texto):  # filtro que busca texto em diversos campos do livro (nome, autora, gênero, editora)
        self.__texto = texto.strip().lower()

    def passa(self, livro):
        campos = [livro.nome, livro.autora.nome, livro.genero.nome, livro.editora.nome]
        return any(self.__texto in campo.lower() for campo in campos) #retorna any textos que passarem no filtro, ou seja, se o texto estiver em qualquer um dos campos do livro (nome, autora, gênero ou editora), o método retorna True; caso contrário, retorna False.


# Só livros do gênero com exatamente esse nome.
class FiltroGenero(Filtro):
    def __init__(self, nome):
        self.__nome = nome.lower()

    def passa(self, livro):
        return livro.genero.nome.lower() == self.__nome # O método passa compara o nome do gênero do livro (livro.genero.nome) com o nome fornecido ao filtro (self.__nome). Se os nomes forem iguais, o método retorna True, indicando que o livro passa no filtro; caso contrário, retorna False.


# Só livros da editora com exatamente esse nome.
class FiltroEditora(Filtro):
    def __init__(self, nome):
        self.__nome = nome.lower()

    def passa(self, livro):
        return livro.editora.nome.lower() == self.__nome


# --- filtros da estante: o item é um registro Estante ---

# Deixa tudo passar (a opção "todos" da estante).
class FiltroTodos(Filtro):
    def passa(self, registro):
        return True


class FiltroLido(Filtro):
    def passa(self, registro): #registro é um objeto da classe Estante, que representa um livro na estante do usuário. O método passa verifica se o livro foi marcado como lido (registro.lido) e retorna True se for o caso, ou False caso contrário.
        return registro.lido


class FiltroFavorito(Filtro):
    def passa(self, registro):
        return registro.favorito


class FiltroQueroLer(Filtro):
    def passa(self, registro):
        return registro.quer_ler


# Dicionário nome -> classe. Permite escolher o filtro pelo texto que vem da tela (ex.: "lidos")
# sem uma fila de if/elif.
FILTROS_ESTANTE = {
    "todos": FiltroTodos,
    "lidos": FiltroLido,
    "favoritos": FiltroFavorito,
    "quero-ler": FiltroQueroLer,
}


# Com a lista vazia, all([]) é True e todo item passa (nenhum filtro = sem restrição).
def aplicar(filtros, itens):
    """Devolve só os itens que passam em todos os filtros."""
    return [item for item in itens if all(f.passa(item) for f in filtros)]
