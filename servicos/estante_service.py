from modelos.estante import Estante
from servicos.filtros import FILTROS_ESTANTE, aplicar


# Cuida da estante de cada pessoa: marcar lido, favorito e quero ler, e listar com filtro.
class EstanteService:
    # Recebe o repositório (injeção de dependência).
    def __init__(self, repo):
        self.__repo = repo

    # O registro dessa pessoa para esse livro, ou None se o livro não está na estante.
    def registro(self, usuario, livro):
        return self.__repo.buscar_registro(usuario, livro)

    def alternar(self, usuario, livro, status):
        """Liga o status se estava desligado e desliga se estava ligado (lido, favorito, quer_ler)."""
        registro = self.registro(usuario, livro)
        # Primeira vez que a pessoa mexe nesse livro: cria um registro novo, com id gerado pelo repositório.
        if registro is None:
            registro = Estante(self.__repo.proximo_id("estantes"), usuario, livro)

        # Quem decide como ligar/desligar é a classe Estante (ex.: marcar lido desliga quero ler);
        # o serviço só escolhe qual método chamar.
        if status == "lido":
            registro.definir_lido(not registro.lido)
        elif status == "favorito":
            registro.definir_favorito(not registro.favorito)
        elif status == "quer_ler":
            registro.definir_quer_ler(not registro.quer_ler)
        else:
            raise ValueError("status inválido")

        # sem nenhum status marcado o livro sai da estante
        if registro.lido or registro.favorito or registro.quer_ler:
            self.__repo.salvar(registro)
        else:
            self.__repo.remover(registro)
        return registro

    # FILTROS_ESTANTE traduz o nome do filtro ("lidos", "favoritos"...) na classe de filtro certa.
    # Nome desconhecido gera erro em vez de devolver tudo calado.
    def listar(self, usuario, filtro="todos"):
        if filtro not in FILTROS_ESTANTE:
            raise ValueError("filtro inválido")
        return aplicar([FILTROS_ESTANTE[filtro]()], self.__repo.listar_registros(usuario))

    # Contagens para o topo da tela. sum() de booleanos conta os True (True vale 1).
    def resumo(self, usuario):
        meus = self.listar(usuario)
        return {
            "total": len(meus),
            "lidos": sum(r.lido for r in meus),
            "favoritos": sum(r.favorito for r in meus),
            "quero_ler": sum(r.quer_ler for r in meus),
        }
