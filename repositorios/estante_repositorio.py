from modelos.estante import Estante


class EstanteRepositorio:
    def __init__(self, conexao, livros):
        self.__conexao = conexao
        self.__livros = livros

    def proximo_id(self):
        return self.__conexao.proximo_id("estantes")

    def salvar(self, registro):
        self.__conexao.gravar("estantes", {
            "id": registro.id,
            "usuario_id": registro.usuario.id,
            "livro_id": registro.livro.id,
            "lido": int(registro.lido),
            "favorito": int(registro.favorito),
            "quer_ler": int(registro.quer_ler),
        })

    def remover(self, registro):
        self.__conexao.remover("estantes", registro.id)

    def buscar(self, usuario, livro):
        linhas = self.__conexao.consultar(
            "SELECT * FROM estantes WHERE usuario_id = ? AND livro_id = ?", (usuario.id, livro.id)
        )
        return self.__para_registro(linhas[0], usuario) if linhas else None

    def listar(self, usuario):
        linhas = self.__conexao.consultar(
            "SELECT * FROM estantes WHERE usuario_id = ? ORDER BY id", (usuario.id,)
        )
        return [self.__para_registro(linha, usuario) for linha in linhas]

    def __para_registro(self, linha, usuario):
        livro = self.__livros.buscar(linha["livro_id"])
        return Estante(linha["id"], usuario, livro, favorito=bool(linha["favorito"]),
                       quer_ler=bool(linha["quer_ler"]), lido=bool(linha["lido"]))
