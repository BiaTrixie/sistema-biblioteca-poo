class Genero:
    def __init__(self, id, nome):
        self.__id = id
        self.__nome = self.__validar_nome(nome)

    @property
    def id(self):
        return self.__id

    @property
    def nome(self):
        return self.__nome

    def __validar_nome(self, nome):
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("nome do gênero é obrigatório")
        return nome.strip()

    def __str__(self):
        return f"[{self.__id}] {self.__nome}"
