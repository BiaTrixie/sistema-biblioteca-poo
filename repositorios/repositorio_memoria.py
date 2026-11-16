from contextlib import nullcontext

from repositorios.repositorio import COLECAO_DE, Repositorio


class RepositorioMemoria(Repositorio):
    """Guarda tudo em listas, na memória. Ao fechar o programa os dados somem.
    É a implementação usada nos testes."""

    # __dados é um dicionário com uma lista por coleção: {"livros": [], "usuarios": [], ...}.
    # O "__" deixa o atributo privado: de fora só se mexe nele pelos métodos abaixo (encapsulamento).
    def __init__(self):
        self.__dados = {nome: [] for nome in COLECAO_DE.values()}

    # max(...) pega o maior id da lista; default=0 vale para lista vazia (o primeiro id vira 1).
    def proximo_id(self, colecao):
        return max((item.id for item in self.__dados[colecao]), default=0) + 1

    # COLECAO_DE[type(objeto)] descobre a lista certa pelo tipo (Livro -> "livros").
    # Só insere se o objeto ainda não está na lista (`is` compara o MESMO objeto, não um parecido).
    # Objeto que já estava na lista foi alterado no lugar pelo serviço, então não há o que atualizar.
    def salvar(self, objeto):
        lista = self.__dados[COLECAO_DE[type(objeto)]]
        if not any(item is objeto for item in lista):  # objeto novo; os antigos já foram alterados no lugar
            lista.append(objeto)

    # Tira o objeto da lista da sua coleção.
    def remover(self, objeto):
        self.__dados[COLECAO_DE[type(objeto)]].remove(objeto)

    # nullcontext é um `with` que não faz nada. Na memória não há como desfazer, então basta isso
    # para o código `with repo.transacao():` funcionar igual nos dois repositórios.
    def transacao(self):
        return nullcontext()  # na memória não há o que desfazer

    # Vazio = sem nenhum livro.
    def esta_vazio(self):
        return not self.__dados["livros"]

    # next(gerador, None): devolve o primeiro que combina ou None se nenhum combinar.
    def buscar_usuario(self, id_usuario):
        return next((u for u in self.__dados["usuarios"] if u.id == id_usuario), None)

    # Normaliza (tira espaços e põe em minúsculas) porque o Usuario guarda o e-mail assim.
    def buscar_usuario_por_email(self, email):
        email = str(email).strip().lower()
        return next((u for u in self.__dados["usuarios"] if u.email == email), None)

    # list(...) devolve uma CÓPIA, para quem chama não mexer na lista interna sem querer.
    def listar_livros(self):
        return list(self.__dados["livros"])

    def buscar_livro(self, id_livro):
        return next((l for l in self.__dados["livros"] if l.id == id_livro), None)

    def listar_generos(self):
        return list(self.__dados["generos"])

    def listar_editoras(self):
        return list(self.__dados["editoras"])

    # Compara por id (e não pelo objeto) porque o mesmo usuário pode estar em objetos diferentes.
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

    # Sem livro, devolve todas; com livro, só as desse livro.
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
