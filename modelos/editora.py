class Editora:
    def __init__(self, id, nome, autores=()):
        self.__id = id
        self.__nome = nome
        self.__autores = set(autores)

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
    def autores(self):
        return set(self.__autores)

    def adicionar_autor(self, autor):
        self.__autores.add(autor)

    def remover_autor(self, autor):
        if autor not in self.__autores:
            raise ValueError("autor não vinculado a esta editora")
        self.__autores.remove(autor)

    def __str__(self):
        return f"[{self.__id}] {self.__nome}"