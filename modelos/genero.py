class Genero:
    def __init__(self, id: int, nome: str) -> None:
        self.__id = self.__validar_id(id)
        self.__nome = self.__validar_nome(nome)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    def atualizar_nome(self, nome: str) -> None:
        self.__nome = self.__validar_nome(nome)

    def __validar_id(self, id: int) -> int:
        if isinstance(id, bool) or not isinstance(id, int) or id < 1:
            raise ValueError("id inválido")
        return id

    def __validar_nome(self, nome: str) -> str:
        if not isinstance(nome, str):
            raise ValueError("nome do gênero é obrigatório")
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("nome do gênero é obrigatório")
        return nome_limpo

    def __str__(self) -> str:
        return f"[{self.__id}] {self.__nome}"
