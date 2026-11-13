class Comentario:
    def __init__(self, id, texto, data, usuario, livro, numero_likes=0):
        self.__id = id
        self.__usuario = usuario
        self.__livro = livro
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
    def usuario(self):
        return self.__usuario

    @property
    def livro(self):
        return self.__livro

    @property
    def numero_likes(self):
        return self.__numero_likes

    def curtir(self):
        self.__numero_likes += 1

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data

    def __str__(self):
        return f"[{self.__id}] ({self.__data}) - {self.__numero_likes} \n{self.__texto}"