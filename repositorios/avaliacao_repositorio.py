from datetime import date

from modelos.avaliacao import Avaliacao


class AvaliacaoRepositorio:
    def __init__(self, conexao, usuarios, livros):
        self.__conexao = conexao
        self.__usuarios = usuarios
        self.__livros = livros

    def proximo_id(self):
        return self.__conexao.proximo_id("avaliacoes")

    def salvar(self, avaliacao):
        self.__conexao.gravar("avaliacoes", {
            "id": avaliacao.id,
            "usuario_id": avaliacao.usuario.id,
            "livro_id": avaliacao.livro.id,
            "nota": avaliacao.nota,
            "data": avaliacao.data.isoformat(),
            "comentario": avaliacao.comentario,
        })

    def buscar(self, usuario, livro):
        linhas = self.__conexao.consultar(
            "SELECT * FROM avaliacoes WHERE usuario_id = ? AND livro_id = ?", (usuario.id, livro.id)
        )
        return self.__para_avaliacao(linhas[0], usuario, livro) if linhas else None

    def listar(self, livro=None):
        usuarios = self.__usuarios.por_id()
        livros = self.__livros.por_id()
        if livro is None:
            linhas = self.__conexao.consultar("SELECT * FROM avaliacoes ORDER BY id")
        else:
            linhas = self.__conexao.consultar(
                "SELECT * FROM avaliacoes WHERE livro_id = ? ORDER BY id", (livro.id,)
            )
        return [self.__para_avaliacao(linha, usuarios[linha["usuario_id"]], livros[linha["livro_id"]])
                for linha in linhas]

    def __para_avaliacao(self, linha, usuario, livro):
        return Avaliacao(linha["id"], linha["nota"], date.fromisoformat(linha["data"]),
                         usuario, livro, linha["comentario"])
