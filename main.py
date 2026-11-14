from menus.menu_principal import MenuPrincipal
from servicos.sistema import Sistema


def main():
    MenuPrincipal(Sistema()).executar()


if __name__ == "__main__":
    main()
