from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modelos.sessao import Sessao
    from servicos.catalogo import Catalogo
    from servicos.estantes import GestaoEstante


def _escolher_livro(catalogo: Catalogo):
    id = int(input("Id do livro: "))
    return catalogo.buscar_livro(id)


def _perguntar_sim_nao(pergunta: str) -> bool:
    resposta = input(f"{pergunta} (s/n): ").strip().lower()
    if resposta not in ("s", "n"):
        raise ValueError("responda s ou n")
    return resposta == "s"


def _imprimir_itens(itens) -> None:
    if not itens:
        print("Nenhum livro aqui.")
    for item in itens:
        print(item)


def menu_estante(sessao: Sessao, estantes: GestaoEstante, catalogo: Catalogo) -> None:
    while True:
        print("\n--- Minha estante ---")
        print("1. Adicionar livro")
        print("2. Marcar ou desmarcar favorito")
        print("3. Marcar ou desmarcar quero ler")
        print("4. Listar estante")
        print("5. Listar favoritos")
        print("6. Listar quero ler")
        print("7. Resumo")
        print("8. Remover livro da estante")
        print("0. Voltar")
        opcao = input("Opção: ").strip()

        if opcao == "0":
            return

        try:
            if opcao == "1":
                item = estantes.adicionar(sessao, _escolher_livro(catalogo))
                print("Adicionado:", item)
            elif opcao == "2":
                livro = _escolher_livro(catalogo)
                valor = _perguntar_sim_nao("Favorito?")
                print("Atualizado:", estantes.definir_favorito(sessao, livro, valor))
            elif opcao == "3":
                livro = _escolher_livro(catalogo)
                valor = _perguntar_sim_nao("Quero ler?")
                print("Atualizado:", estantes.definir_quer_ler(sessao, livro, valor))
            elif opcao == "4":
                _imprimir_itens(estantes.listar_do_usuario(sessao.exigir_login()))
            elif opcao == "5":
                _imprimir_itens(estantes.listar_favoritos(sessao.exigir_login()))
            elif opcao == "6":
                _imprimir_itens(estantes.listar_quero_ler(sessao.exigir_login()))
            elif opcao == "7":
                resumo = estantes.resumo(sessao.exigir_login())
                print(f"Total: {resumo['total']}")
                print(f"Favoritos: {resumo['favoritos']}")
                print(f"Quero ler: {resumo['quero_ler']}")
            elif opcao == "8":
                estantes.remover(sessao, _escolher_livro(catalogo))
                print("Removido da estante.")
            else:
                print("Opção inválida.")
        except ValueError as erro:
            print("Erro:", erro)
