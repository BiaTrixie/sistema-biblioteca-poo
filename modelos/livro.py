class Livro:
    def __init__(self, id, nome, ano, genero, sinopse, edicao, editora, autora):
        self.__id = id
        self.__nome = self.__validar_nome(nome)
        self.__ano = self.__validar_ano(ano)
        self.__genero = genero
        self.__sinopse = sinopse
        self.__edicao = edicao
        self.__editora = editora
        self.__autora = autora

    @property
    def id(self):
        return self.__id

    @property
    def nome(self):
        return self.__nome

    @property
    def ano(self):
        return self.__ano

    @property
    def genero(self):
        return self.__genero

    @property
    def sinopse(self):
        return self.__sinopse

    @property
    def edicao(self):
        return self.__edicao

    @property
    def editora(self):
        return self.__editora

    @property
    def autora(self):
        return self.__autora

    def __validar_nome(self, nome):
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("nome do livro é obrigatório")
        return nome.strip()

    def __validar_ano(self, ano):
        if isinstance(ano, bool) or not isinstance(ano, int):
            raise ValueError("ano do livro inválido")
        return ano

    def __str__(self):
        return f"[{self.__id}] {self.__nome} ({self.__ano}) — {self.__autora.nome} — {self.__genero.nome}"
