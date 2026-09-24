class Comentario:
    def __init__(self, id, texto, data, numero_likes=0):
        self.__id = id
        self.__texto = texto
        self.__data = data
        self.__numero_likes = numero_likes

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def texto(self):
        return self.__texto

    @texto.setter
    def texto(self, texto):
        self.__texto = texto

    @property
    def numeros_likes(self):
        return self.__numeros_likes

    @numeros_likes.setter
    def numeros_likes(self, numeros_likes):
        self.__numeros_likes = numeros_likes

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data

    def __str__(self):
        return f"[{self.__id}] ({self.__data}) - {self.__numero_likes} \n{self.__texto}"