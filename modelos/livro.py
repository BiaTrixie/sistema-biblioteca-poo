class Livro:
    def __init__(self, id, nome, ano, genero, sinopse, edicao, editora, lido=False):
        self.__id = id
        self.__nome = nome
        self.__ano = ano
        self.__genero = genero
        self.__sinopse = sinopse
        self.__edicao = edicao
        self.__editora = editora
        self.__lido = lido

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome):
        self.__nome = nome

    @property
    def ano(self):
        return self.__ano

    @ano.setter
    def ano(self, ano):
        self.__ano = ano

    @property
    def genero(self):
        return self.__genero

    @genero.setter
    def genero(self, genero):
        self.__genero = genero

    @property
    def sinopse(self):
        return self.__sinopse

    @sinopse.setter
    def sinopse(self, sinopse):
        self.__sinopse = sinopse

    @property
    def edicao(self):
        return self.__edicao

    @edicao.setter
    def edicao(self, edicao):
        self.__edicao = edicao

    @property
    def editora(self):
        return self.__editora

    @editora.setter
    def editora(self, editora):
        self.__editora = editora

    @property
    def lido(self):
        return self.__lido

    @lido.setter
    def lido(self, lido):
        self.__lido = lido

    def __str__(self):
        if self.__lido:
            situacao = "lido"
        else:
            situacao = "não lido"
        return f"[{self.__id}] {self.__nome} ({self.__ano}) — {self.__genero.nome} — {situacao}"
