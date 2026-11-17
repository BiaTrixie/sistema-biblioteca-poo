class Estante:
    def __init__(self, id, usuario, livro, favorito: bool = False, quer_ler: bool = False, lido: bool = False,):
        self.__id = id
        self.__usuario = usuario
        self.__livro = livro
        self.__favorito = self.__validar_booleano(favorito)
        self.__quer_ler = self.__validar_booleano(quer_ler)
        self.__lido = self.__validar_booleano(lido)
        if self.__lido and self.__quer_ler:
            raise ValueError("um livro não pode estar como lido e quero ler ao mesmo tempo")

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

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
    def favorito(self):
        return self.__favorito

    @property
    def quer_ler(self):
        return self.__quer_ler

    @property
    def lido(self):
        return self.__lido

    def definir_lido(self, valor: bool):
        self.__lido = self.__validar_booleano(valor)
        if self.__lido:  # quem já leu não "quer ler"
            self.__quer_ler = False

    def definir_favorito(self, valor: bool):
        self.__favorito = self.__validar_booleano(valor)

    def definir_quer_ler(self, valor: bool):
        self.__quer_ler = self.__validar_booleano(valor)
        if self.__quer_ler:  # quem quer ler ainda não leu
            self.__lido = False

    def __validar_booleano(self, valor: bool):
        if not isinstance(valor, bool):
            raise ValueError("valor precisa ser verdadeiro ou falso")
        return valor

    def __str__(self):
        favorito = "sim" if self.__favorito else "não"
        quer_ler = "sim" if self.__quer_ler else "não"
        lido = "sim" if self.__lido else "não"
        return (
            f"[{self.__id}] {self.__livro.nome} — favorito: {favorito}"
            f" — quero ler: {quer_ler} — lido: {lido}"
        )
