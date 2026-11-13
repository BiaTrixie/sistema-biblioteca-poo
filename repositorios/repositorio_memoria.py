from contextlib import nullcontext

from repositorios.repositorio import COLECAO_DE, Repositorio


class RepositorioMemoria(Repositorio):
    """Guarda tudo em listas, na memória. Ao fechar o programa os dados somem.
    É a implementação usada nos testes."""

    def __init__(self):
        self.__dados = {nome: [] for nome in COLECAO_DE.values()}

    def proximo_id(self, colecao):
        return max((item.id for item in self.__dados[colecao]), default=0) + 1

    def salvar(self, objeto):
        lista = self.__dados[COLECAO_DE[type(objeto)]]
        if not any(item is objeto for item in lista):  # objeto novo; os antigos já foram alterados no lugar
            lista.append(objeto)

    def remover(self, objeto):
        self.__dados[COLECAO_DE[type(objeto)]].remove(objeto)

    def transacao(self):
        return nullcontext()  # na memória não há o que desfazer

    def esta_vazio(self):
        return not self.__dados["livros"]

    def buscar_usuario(self, id_usuario):
        return next((u for u in self.__dados["usuarios"] if u.id == id_usuario), None)

    def buscar_usuario_por_email(self, email):
        email = str(email).strip().lower()
        return next((u for u in self.__dados["usuarios"] if u.email == email), None)

    def listar_livros(self):
        return list(self.__dados["livros"])

    def buscar_livro(self, id_livro):
        return next((l for l in self.__dados["livros"] if l.id == id_livro), None)

    def listar_generos(self):
        return list(self.__dados["generos"])

    def listar_editoras(self):
        return list(self.__dados["editoras"])

    def buscar_registro(self, usuario, livro):
        return next(
            (r for r in self.__dados["estantes"]
             if r.usuario.id == usuario.id and r.livro.id == livro.id),
            None,
        )

    def listar_registros(self, usuario):
        return [r for r in self.__dados["estantes"] if r.usuario.id == usuario.id]

    def buscar_avaliacao(self, usuario, livro):
        return next(
            (a for a in self.__dados["avaliacoes"]
             if a.usuario.id == usuario.id and a.livro.id == livro.id),
            None,
        )

    def listar_avaliacoes(self, livro=None):
        return [a for a in self.__dados["avaliacoes"] if livro is None or a.livro.id == livro.id]

    def buscar_comentario(self, id_comentario):
        return next((c for c in self.__dados["comentarios"] if c.id == id_comentario), None)

    def buscar_comentario_de(self, usuario, livro):
        return next(
            (c for c in self.__dados["comentarios"]
             if c.usuario.id == usuario.id and c.livro.id == livro.id),
            None,
        )

    def listar_comentarios(self, livro=None):
        return [c for c in self.__dados["comentarios"] if livro is None or c.livro.id == livro.id]
