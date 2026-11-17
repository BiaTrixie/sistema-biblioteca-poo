from modelos.autor import Autor
from modelos.editora import Editora
from modelos.genero import Genero
from modelos.livro import Livro


class LivroRepositorio:
    """Livro, gênero, editora e autor. O catálogo é lido uma vez e fica em memória."""

    def __init__(self, conexao):
        self.__conexao = conexao
        self.__catalogo = None

    def listar(self):
        return list(self.__ler()["livros"].values())

    def buscar(self, id_livro):
        return self.__ler()["livros"].get(id_livro)

    def por_id(self):
        return self.__ler()["livros"]

    def listar_generos(self):
        return list(self.__ler()["generos"].values())

    def listar_editoras(self):
        return list(self.__ler()["editoras"].values())

    def salvar(self, objeto):
        if isinstance(objeto, Genero):
            self.__conexao.gravar("generos", {"id": objeto.id, "nome": objeto.nome})
        elif isinstance(objeto, Editora):
            with self.__conexao.transacao():
                self.__conexao.gravar("editoras", {"id": objeto.id, "nome": objeto.nome})
                for autor in objeto.autores:
                    self.__conexao.executar(
                        "INSERT OR IGNORE INTO editora_autor VALUES (?, ?)", (objeto.id, autor.id)
                    )
        elif isinstance(objeto, Autor):
            self.__conexao.gravar("autores", {"id": objeto.id, "nome": objeto.nome})
        elif isinstance(objeto, Livro):
            self.__conexao.gravar("livros", {
                "id": objeto.id, "nome": objeto.nome, "ano": objeto.ano,
                "genero_id": objeto.genero.id, "sinopse": objeto.sinopse, "edicao": objeto.edicao,
                "editora_id": objeto.editora.id, "autor_id": objeto.autor.id,
            })
        else:
            raise TypeError("objeto não faz parte do catálogo")
        self.__catalogo = None

    def __ler(self):
        if self.__catalogo is None:
            generos = {r["id"]: Genero(r["id"], r["nome"])
                       for r in self.__conexao.consultar("SELECT * FROM generos ORDER BY id")}
            editoras = {r["id"]: Editora(r["id"], r["nome"])
                        for r in self.__conexao.consultar("SELECT * FROM editoras ORDER BY id")}
            autores = {r["id"]: Autor(r["id"], r["nome"])
                       for r in self.__conexao.consultar("SELECT * FROM autores ORDER BY id")}
            for r in self.__conexao.consultar("SELECT * FROM editora_autor"):
                editoras[r["editora_id"]].adicionar_autor(autores[r["autor_id"]])
                autores[r["autor_id"]].adicionar_editora(editoras[r["editora_id"]])
            livros = {
                r["id"]: Livro(r["id"], r["nome"], r["ano"], generos[r["genero_id"]], r["sinopse"],
                               r["edicao"], editoras[r["editora_id"]], autores[r["autor_id"]])
                for r in self.__conexao.consultar("SELECT * FROM livros ORDER BY id")
            }
            self.__catalogo = {"generos": generos, "editoras": editoras, "livros": livros}
        return self.__catalogo
