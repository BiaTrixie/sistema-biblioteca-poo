from __future__ import annotations

from typing import TYPE_CHECKING

from modelos.estante import Estante

if TYPE_CHECKING:
    from modelos.livro import Livro
    from modelos.sessao import Sessao
    from modelos.usuario import Usuario


class GestaoEstante:
    def __init__(self) -> None:
        self.__itens: list[Estante] = []
        self.__proximo_id = 1

    def adicionar(self, sessao: Sessao, livro: Livro) -> Estante:
        usuario = sessao.exigir_login()
        if self.__procurar(usuario, livro) is not None:
            raise ValueError("este livro já está na sua estante")
        item = Estante(self.__proximo_id, usuario, livro)
        self.__proximo_id += 1
        self.__itens.append(item)
        return item

    def buscar(self, usuario: Usuario, livro: Livro) -> Estante:
        item = self.__procurar(usuario, livro)
        if item is None:
            raise ValueError("este livro não está na estante; adicione antes")
        return item

    def definir_favorito(self, sessao: Sessao, livro: Livro, valor: bool) -> Estante:
        item = self.buscar(sessao.exigir_login(), livro)
        item.definir_favorito(valor)
        return item

    def definir_quer_ler(self, sessao: Sessao, livro: Livro, valor: bool) -> Estante:
        item = self.buscar(sessao.exigir_login(), livro)
        item.definir_quer_ler(valor)
        return item

    def listar_do_usuario(self, usuario: Usuario) -> list[Estante]:
        return [item for item in self.__itens if item.usuario.id == usuario.id]

    def listar_favoritos(self, usuario: Usuario) -> list[Estante]:
        return [item for item in self.listar_do_usuario(usuario) if item.favorito]

    def listar_quero_ler(self, usuario: Usuario) -> list[Estante]:
        return [item for item in self.listar_do_usuario(usuario) if item.quer_ler]

    def resumo(self, usuario: Usuario) -> dict[str, int]:
        return {
            "total": len(self.listar_do_usuario(usuario)),
            "favoritos": len(self.listar_favoritos(usuario)),
            "quero_ler": len(self.listar_quero_ler(usuario)),
        }

    def remover(self, sessao: Sessao, livro: Livro) -> None:
        # Só tira o item da lista; não mexe em livro.lido.
        item = self.buscar(sessao.exigir_login(), livro)
        self.__itens.remove(item)

    def __procurar(self, usuario: Usuario, livro: Livro) -> Estante | None:
        for item in self.__itens:
            if item.usuario.id == usuario.id and item.livro.id == livro.id:
                return item
        return None


# Testes manuais da Juliana (seção 5 e passo 5 da seção 8).
# Rodar com: python -m servicos.estantes
# Usa objetos simples no lugar de Usuario, Livro e Sessao, só para testar a regra.
if __name__ == "__main__":
    from types import SimpleNamespace

    usuario = SimpleNamespace(id=1, nome="Pessoa comum")
    sessao = SimpleNamespace(exigir_login=lambda: usuario)
    livro1 = SimpleNamespace(id=1, nome="O Hobbit", lido=False)
    livro2 = SimpleNamespace(id=2, nome="Duna", lido=True)
    estantes = GestaoEstante()

    # Teste 1: adicionar o mesmo livro duas vezes levanta ValueError.
    estantes.adicionar(sessao, livro1)
    try:
        estantes.adicionar(sessao, livro1)
        print("FALHOU: aceitou o mesmo livro duas vezes")
    except ValueError as erro:
        print("ok, teste 1:", erro)

    # Teste 2: favorito e quero ler verdadeiros no mesmo item.
    estantes.definir_favorito(sessao, livro1, True)
    item = estantes.definir_quer_ler(sessao, livro1, True)
    assert item.favorito and item.quer_ler
    print("ok, teste 2:", item)

    # Teste 3: 2 itens, 1 favorito, 2 quero ler.
    estantes.adicionar(sessao, livro2)
    estantes.definir_quer_ler(sessao, livro2, True)
    resumo = estantes.resumo(usuario)
    assert resumo == {"total": 2, "favoritos": 1, "quero_ler": 2}, resumo
    print("ok, teste 3:", resumo)
