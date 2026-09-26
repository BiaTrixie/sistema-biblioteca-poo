class Editora:
    def __init__(self, id: int, nome: str) -> None:
        self.__id = id
        self.__nome = self.__validar_nome(nome)
        self.__autores: list["Autora"] = []

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def autores(self) -> list["Autora"]:
        return self.__autores

    def adicionar_autora(self, autora: "Autora") -> None:
        self.__autores.append(autora)

    def remover_autora(self, autora: "Autora") -> None:
        self.__autores.remove(autora)

    def __validar_nome(self, nome: str) -> str:
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("nome da editora é obrigatório")
        return nome_limpo

    def __str__(self) -> str:
        return f"[{self.__id}] {self.__nome}"