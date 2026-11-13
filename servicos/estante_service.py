from modelos.estante import Estante
from servicos.filtros import FILTROS_ESTANTE, aplicar


class EstanteService:
    def __init__(self, repo):
        self.__repo = repo

    def registro(self, usuario, livro):
        return self.__repo.buscar_registro(usuario, livro)

    def alternar(self, usuario, livro, status):
        """Liga o status se estava desligado e desliga se estava ligado (lido, favorito, quer_ler)."""
        registro = self.registro(usuario, livro)
        if registro is None:
            registro = Estante(self.__repo.proximo_id("estantes"), usuario, livro)

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

    def listar(self, usuario, filtro="todos"):
        if filtro not in FILTROS_ESTANTE:
            raise ValueError("filtro inválido")
        return aplicar([FILTROS_ESTANTE[filtro]()], self.__repo.listar_registros(usuario))

    def resumo(self, usuario):
        meus = self.listar(usuario)
        return {
            "total": len(meus),
            "favoritos": sum(r.favorito for r in meus),
            "quero_ler": sum(r.quer_ler for r in meus),
        }
