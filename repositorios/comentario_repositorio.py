from datetime import date

from modelos.comentario import Comentario


class ComentarioRepositorio:
    def __init__(self, conexao, usuarios, livros):
        self.__conexao = conexao
        self.__usuarios = usuarios
        self.__livros = livros

    def proximo_id(self):
        return self.__conexao.proximo_id("comentarios")

    def salvar(self, comentario):
        with self.__conexao.transacao():
            self.__conexao.gravar("comentarios", {
                "id": comentario.id,
                "usuario_id": comentario.usuario.id,
                "livro_id": comentario.livro.id,
                "texto": comentario.texto,
                "data": comentario.data.isoformat(),
            })
            self.__conexao.executar("DELETE FROM curtidas WHERE comentario_id = ?", (comentario.id,))
            for id_usuario in comentario.curtidas:
                self.__conexao.executar(
                    "INSERT INTO curtidas VALUES (?, ?)", (comentario.id, id_usuario)
                )

    def buscar(self, id_comentario):
        linhas = self.__conexao.consultar("SELECT * FROM comentarios WHERE id = ?", (id_comentario,))
        if not linhas:
            return None
        usuario = self.__usuarios.buscar(linhas[0]["usuario_id"])
        livro = self.__livros.buscar(linhas[0]["livro_id"])
        return self.__para_comentario(linhas[0], usuario, livro, self.__curtidas())

    def buscar_de(self, usuario, livro):
        linhas = self.__conexao.consultar(
            "SELECT * FROM comentarios WHERE usuario_id = ? AND livro_id = ?", (usuario.id, livro.id)
        )
        if not linhas:
            return None
        return self.__para_comentario(linhas[0], usuario, livro, self.__curtidas())

    def listar(self, livro=None):
        usuarios = self.__usuarios.por_id()
        livros = self.__livros.por_id()
        curtidas = self.__curtidas()
        if livro is None:
            linhas = self.__conexao.consultar("SELECT * FROM comentarios ORDER BY id")
        else:
            linhas = self.__conexao.consultar(
                "SELECT * FROM comentarios WHERE livro_id = ? ORDER BY id", (livro.id,)
            )
        return [self.__para_comentario(linha, usuarios[linha["usuario_id"]], livros[linha["livro_id"]], curtidas)
                for linha in linhas]

    def __curtidas(self):
        curtidas = {}
        for linha in self.__conexao.consultar("SELECT comentario_id, usuario_id FROM curtidas"):
            curtidas.setdefault(linha["comentario_id"], set()).add(linha["usuario_id"])
        return curtidas

    def __para_comentario(self, linha, usuario, livro, curtidas):
        return Comentario(linha["id"], linha["texto"], date.fromisoformat(linha["data"]),
                          usuario, livro, curtidas.get(linha["id"], ()))
