from modelos.estante import Estante
from servicos.filtros import FILTROS_ESTANTE, aplicar


class EstanteService:
    def __init__(self, repo):
        self.__repo = repo

    def registro(self, usuario, livro):
        return next(
            (r for r in self.__repo.estantes if r.usuario is usuario and r.livro is livro),
            None,
        )

    def alternar(self, usuario, livro, status):
        """Liga o status se estava desligado e desliga se estava ligado (lido, favorito, quer_ler)."""
        registro = self.registro(usuario, livro)
        if registro is None:
            novo_id = self.__repo.proximo_id(self.__repo.estantes)
            registro = Estante(novo_id, usuario, livro)
            self.__repo.estantes.append(registro)

        if status == "lido":
            registro.definir_lido(not registro.lido)
        elif status == "favorito":
            registro.definir_favorito(not registro.favorito)
        elif status == "quer_ler":
            registro.definir_quer_ler(not registro.quer_ler)
        else:
            raise ValueError("status inválido")

        # sem nenhum status marcado o livro sai da estante
        if not (registro.lido or registro.favorito or registro.quer_ler):
            self.__repo.estantes.remove(registro)
        return registro

    def listar(self, usuario, filtro="todos"):
        if filtro not in FILTROS_ESTANTE:
            raise ValueError("filtro inválido")
        meus = [r for r in self.__repo.estantes if r.usuario is usuario]
        return aplicar([FILTROS_ESTANTE[filtro]()], meus)

    def resumo(self, usuario):
        meus = self.listar(usuario)
        return {
            "total": len(meus),
            "favoritos": sum(r.favorito for r in meus),
            "quero_ler": sum(r.quer_ler for r in meus),
        }
