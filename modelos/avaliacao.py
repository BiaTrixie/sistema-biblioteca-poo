class Avaliacao:
    def __init__(self, id, nota, data, usuario, livro, comentario=''):
        self.__id = id
        self.__nota = self.__validar_nota(nota)
        self.__usuario = usuario
        self.__livro = livro
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
        self.__nota = self.__validar_nota(nota)

    @property
    def usuario(self):
        return self.__usuario

    @usuario.setter
    def usuario(self, usuario):
        self.__usuario = usuario

    @property
    def livro(self):
        return self.__livro

    @livro.setter
    def livro(self, livro):
        self.__livro = livro

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

    def __validar_nota(self, nota):
        if isinstance(nota, bool) or not isinstance(nota, int) or not 1 <= nota <= 5:
            raise ValueError("a nota vai de 1 a 5")
        return nota

    def __str__(self):
        return f"[{self.__id}] ({self.__data}) - {self.__nota} \n{self.__comentario}"