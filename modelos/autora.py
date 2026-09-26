class Autora:
    def __init__(self, id: int, nome: str) -> None:
        self.__id = id
        self.__nome = self.__validar_nome(nome)
        self.__editoras: list["Editora"] = []

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def editoras(self) -> list["Editora"]:
        return self.__editoras

    def adicionar_editora(self, editora: "Editora") -> None:
        self.__editoras.append(editora)

    def remover_editora(self, editora: "Editora") -> None:
        self.__editoras.remove(editora)

    def __validar_nome(self, nome: str) -> str:
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("nome da autora é obrigatório")
        return nome_limpo

    def __str__(self) -> str:
        return f"[{self.__id}] {self.__nome}"