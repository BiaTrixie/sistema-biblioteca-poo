from menus.menu_catalogo import menu_catalogo
from menus.menu_estante import menu_estante
from menus.menu_interacoes import menu_interacoes
from menus.menu_publicacao import menu_publicacao
from menus.menu_usuarios import menu_usuarios
from modelos.sessao import Sessao
from servicos.autenticacao import Autenticacao
from servicos.catalogo import Catalogo
from servicos.estantes import GestaoEstante
from servicos.interacoes import Interacoes
from servicos.publicacao import Publicacao


def main() -> None:
    sessao = Sessao()
    autenticacao = Autenticacao()
    catalogo = Catalogo()
    publicacao = Publicacao()
    interacoes = Interacoes()
    estantes = GestaoEstante()

    opcoes = {
        "1": lambda: menu_usuarios(sessao, autenticacao),
        "2": lambda: menu_catalogo(sessao, catalogo, publicacao),
        "3": lambda: menu_publicacao(sessao, publicacao),
        "4": lambda: menu_interacoes(sessao, interacoes, catalogo),
        "5": lambda: menu_estante(sessao, estantes, catalogo),
    }

    while True:
        print("\n=== Biblioteca ===")
        print("1. Conta (entrar, sair, cadastrar, perfil)")
        print("2. Catálogo (gêneros e livros)")
        print("3. Autoras e editoras")
        print("4. Comentários e avaliações")
        print("5. Minha estante")
        print("0. Sair")
        opcao = input("Opção: ").strip()

        if opcao == "0":
            print("Até logo!")
            break
        if opcao not in opcoes:
            print("Opção inválida.")
            continue
        try:
            opcoes[opcao]()
        except ValueError as erro:
            print("Erro:", erro)


if __name__ == "__main__":
    main()
