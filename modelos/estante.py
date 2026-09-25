from modelos.livro import Livro
from modelos.usuario import Usuario


class Estante:
    """Um registro da estante: um livro na estante de uma pessoa."""

    def __init__(
        self,
        id: int,
        usuario: Usuario,
        livro: Livro,
        favorito: bool = False,
        quer_ler: bool = False,
    ) -> None:
        if usuario is None:
            raise ValueError("usuário é obrigatório")
        if livro is None:
            raise ValueError("livro é obrigatório")
        self.__id = id
        self.__usuario = usuario
        self.__livro = livro
        self.__favorito = self.__validar_booleano(favorito)
        self.__quer_ler = self.__validar_booleano(quer_ler)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def usuario(self) -> Usuario:
        return self.__usuario

    @property
    def livro(self) -> Livro:
        return self.__livro

    @property
    def favorito(self) -> bool:
        return self.__favorito

    @property
    def quer_ler(self) -> bool:
        return self.__quer_ler

    def definir_favorito(self, valor: bool) -> None:
        self.__favorito = self.__validar_booleano(valor)

    def definir_quer_ler(self, valor: bool) -> None:
        self.__quer_ler = self.__validar_booleano(valor)

    def __validar_booleano(self, valor: bool) -> bool:
        if not isinstance(valor, bool):
            raise ValueError("valor precisa ser verdadeiro ou falso")
        return valor

    def __str__(self) -> str:
        favorito = "sim" if self.__favorito else "não"
        quer_ler = "sim" if self.__quer_ler else "não"
        lido = "sim" if self.__livro.lido else "não"
        return (
            f"[{self.__id}] {self.__livro.nome} — favorito: {favorito}"
            f" — quero ler: {quer_ler} — lido: {lido}"
        )
