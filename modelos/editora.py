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

    def adicionar_autora(self, autora):
        self.__autores.add(autora)

    def remover_autora(self, autora):
        if autora not in self.__autores:
            raise ValueError("autora não vinculada a esta editora")
        self.__autores.remove(autora)

    def __str__(self):
        return f"[{self.__id}] {self.__nome}"