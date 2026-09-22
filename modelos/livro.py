from __future__ import annotations

import importlib.util
from datetime import date
from typing import TYPE_CHECKING

from modelos.genero import Genero

if TYPE_CHECKING:
    from modelos.editora import Editora


class Livro:
    def __init__(
        self,
        id: int,
        nome: str,
        ano: int,
        genero: Genero,
        sinopse: str,
        edicao: str,
        editora: Editora,
        lido: bool = False,
    ) -> None:
        self.__id = self.__validar_id(id)
        self.__nome = self.__validar_texto(nome, "nome do livro é obrigatório")
        self.__ano = self.__validar_ano(ano)
        self.__genero = self.__validar_genero(genero)
        self.__sinopse = self.__validar_texto(sinopse, "sinopse é obrigatória")
        self.__edicao = self.__validar_texto(edicao, "edição é obrigatória")
        self.__editora = self.__validar_editora(editora)
        self.__lido = self.__validar_lido(lido)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def ano(self) -> int:
        return self.__ano

    @property
    def genero(self) -> Genero:
        return self.__genero

    @property
    def sinopse(self) -> str:
        return self.__sinopse

    @property
    def edicao(self) -> str:
        return self.__edicao

    @property
    def editora(self) -> Editora:
        return self.__editora

    @property
    def lido(self) -> bool:
        return self.__lido

    def marcar_como_lido(self) -> None:
        self.__lido = True

    def desmarcar_lido(self) -> None:
        self.__lido = False

    def atualizar(
        self,
        nome: str,
        ano: int,
        genero: Genero,
        sinopse: str,
        edicao: str,
        editora: Editora,
    ) -> None:
        self.__nome = self.__validar_texto(nome, "nome do livro é obrigatório")
        self.__ano = self.__validar_ano(ano)
        self.__genero = self.__validar_genero(genero)
        self.__sinopse = self.__validar_texto(sinopse, "sinopse é obrigatória")
        self.__edicao = self.__validar_texto(edicao, "edição é obrigatória")
        self.__editora = self.__validar_editora(editora)

    def __validar_id(self, id: int) -> int:
        if isinstance(id, bool) or not isinstance(id, int) or id < 1:
            raise ValueError("id inválido")
        return id

    def __validar_texto(self, valor: str, mensagem: str) -> str:
        if not isinstance(valor, str):
            raise ValueError(mensagem)
        texto = valor.strip()
        if not texto:
            raise ValueError(mensagem)
        return texto

    def __validar_ano(self, ano: int) -> int:
        if isinstance(ano, bool) or not isinstance(ano, int):
            raise ValueError("ano inválido")
        if ano < 1 or ano > date.today().year:
            raise ValueError("ano inválido")
        return ano

    def __validar_genero(self, genero: Genero) -> Genero:
        if not isinstance(genero, Genero):
            raise ValueError("gênero inválido")
        return genero

    def __validar_editora(self, editora: Editora) -> Editora:
        if editora is None:
            raise ValueError("editora inválida")
        classe_editora = _carregar_classe_editora()
        if classe_editora is not None and not isinstance(editora, classe_editora):
            raise ValueError("editora inválida")
        return editora

    def __validar_lido(self, lido: bool) -> bool:
        if not isinstance(lido, bool):
            raise ValueError("lido inválido")
        return lido

    def __str__(self) -> str:
        situacao = "lido" if self.__lido else "não lido"
        return f"[{self.__id}] {self.__nome} ({self.__ano}) — {self.__genero.nome} — {situacao}"


def _carregar_classe_editora() -> type | None:
    if importlib.util.find_spec("modelos.editora") is None:
        return None
    from modelos.editora import Editora

    return Editora
