class Avaliacao:
    def __init__(self, id, nota, data, usuario, livro, comentario=''):
        self.__id = id
        self.__nota = self.__validar_nota(nota) # valida a nota para garantir que esteja entre 1 e 5, levantando ValueError caso contrário
        self.__usuario = usuario
        self.__livro = livro
        self.__comentario = comentario
        self.__data = data

    @property
    def id(self):
        return self.__id

    @id.setter #metodo setter para o id, permitindo alterar o id da avaliação. 
    def id(self, id):
        self.__id = id

    @property #metodo getter para visualizar a nota da avaliação, permitindo acesso à nota sem permitir alteração direta
    def nota(self):
        return self.__nota

    @nota.setter #metodo setter para alterar a nota da avaliação, para quando atualizamos a nota.
    def nota(self, nota):
        self.__nota = self.__validar_nota(nota)

    @property
    def usuario(self):
        return self.__usuario

    @property
    def livro(self):
        return self.__livro

    @property
    def comentario(self):
        return self.__comentario

    @comentario.setter # settar o comentário, já que é possível alterar o comentário da avaliação.
    def comentario(self, comentario):
        self.__comentario = comentario

    @property
    def data(self):
        return self.__data

    @data.setter #nova data quando a avaliação é atualizada, para manter o registro da data da última atualização.
    def data(self, data):
        self.__data = data

    def __validar_nota(self, nota):
        if isinstance(nota, bool) or not isinstance(nota, int) or not 1 <= nota <= 5: # o isinstance(nota, bool) é necessário para evitar que valores booleanos (True/False) sejam aceitos como notas válidas, já que em Python, True é equivalente a 1 e False é equivalente a 0. Portanto, sem essa verificação, uma nota de True seria considerada válida, o que não é desejado.
            raise ValueError("a nota vai de 1 a 5")
        return nota

    def __str__(self):
        return f"[{self.__id}] ({self.__data}) - {self.__nota} \n{self.__comentario}"