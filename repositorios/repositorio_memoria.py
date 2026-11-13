class RepositorioMemoria:
    """Guarda tudo em listas, na memória. Ao fechar o programa os dados somem."""

    def __init__(self):
        self.usuarios = []
        self.generos = []
        self.editoras = []
        self.autoras = []
        self.livros = []
        self.estantes = []
        self.avaliacoes = []
        self.comentarios = []

    def proximo_id(self, colecao):
        return max((item.id for item in colecao), default=0) + 1
