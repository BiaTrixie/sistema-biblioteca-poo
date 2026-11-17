class Autor:
    def __init__(self, id, nome, editoras=()):
        self.__id = id
        self.__nome = nome
        self.__editoras = set(editoras)

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
    def editoras(self):
        return set(self.__editoras)

    def adicionar_editora(self, editora):
        self.__editoras.add(editora)

    def remover_editora(self, editora):
        if editora not in self.__editoras:
            raise ValueError("editora não vinculada a este autor")
        self.__editoras.remove(editora)

    def __str__(self):
        return f"[{self.__id}] {self.__nome}"
