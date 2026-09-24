class Avaliacao:
    def __init__(self, id, nota, comentario, data):
        self.__id = id
        self.__nota = nota
        self.__comentario = comentario
        self.__data = data

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def nota(self):
        return self.__nota

    @nota.setter
    def nota(self, nota):
        self.__nota = nota

    @property
    def comentario(self):
        return self.__comentario

    @comentario.setter
    def comentario(self, comentario):
        self.__comentario = comentario

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data

    def __str__(self):
        return f"[{self.__id}] ({self.__data}) - {self.__nota} \n{self.__comentario}"