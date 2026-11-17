from modelos.estante import Estante
from servicos.filtros import FILTROS_ESTANTE, aplicar


class EstanteService:
    def __init__(self, estantes):
        self.__estantes = estantes

    def registro(self, usuario, livro):
        return self.__estantes.buscar(usuario, livro)

    def alternar(self, usuario, livro, status):
        """Liga o status se estava desligado e desliga se estava ligado (lido, favorito, quer_ler)."""
        registro = self.registro(usuario, livro)
        if registro is None:
            registro = Estante(self.__estantes.proximo_id(), usuario, livro)

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
            self.__estantes.salvar(registro)
        else:
            self.__estantes.remover(registro)
        return registro

    def listar(self, usuario, filtro="todos"):
        if filtro not in FILTROS_ESTANTE:
            raise ValueError("filtro inválido")
        return aplicar([FILTROS_ESTANTE[filtro]()], self.__estantes.listar(usuario))

    def resumo(self, usuario):
        meus = self.listar(usuario)
        return {
            "total": len(meus),
            "lidos": sum(r.lido for r in meus),
            "favoritos": sum(r.favorito for r in meus),
            "quero_ler": sum(r.quer_ler for r in meus),
        }
