class Comentario:
    def __init__(self, id, texto, data, usuario, livro, curtidas=()):
        self.__id = id
        self.__usuario = usuario
        self.__livro = livro
        self.__texto = texto
        self.__data = data
        self.__curtidas = set(curtidas)  # ids de quem curtiu: cada pessoa conta uma vez

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
    def curtidas(self):
        return frozenset(self.__curtidas)

    @property
    def numero_likes(self):
        return len(self.__curtidas)

    def curtido_por(self, usuario):
        return usuario.id in self.__curtidas

    def alternar_curtida(self, usuario):
        """Curte se a pessoa ainda não curtiu; se já tinha curtido, desfaz."""
        if self.curtido_por(usuario):
            self.__curtidas.discard(usuario.id)
        else:
            self.__curtidas.add(usuario.id)

    def substituir(self, texto, data):
        """Um novo comentário no lugar do antigo; as curtidas eram do texto velho e se perdem."""
        self.__texto = texto
        self.__data = data
        self.__curtidas.clear()

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data

    def __str__(self):
        return f"[{self.__id}] ({self.__data}) - {self.numero_likes} \n{self.__texto}"