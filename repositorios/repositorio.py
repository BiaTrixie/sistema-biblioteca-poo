from abc import ABC, abstractmethod

from modelos.autora import Autora
from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario
from modelos.editora import Editora
from modelos.estante import Estante
from modelos.genero import Genero
from modelos.livro import Livro
from modelos.usuario import Usuario

# em qual lista (ou tabela) cada tipo de objeto é guardado
COLECAO_DE = {
    Usuario: "usuarios", Genero: "generos", Editora: "editoras", Autora: "autoras",
    Livro: "livros", Estante: "estantes", Avaliacao: "avaliacoes", Comentario: "comentarios",
}


# ABC + @abstractmethod: esta classe é só um CONTRATO. Ela lista o que todo repositório precisa
# saber fazer, mas não faz nada. Não dá para criar Repositorio() direto, e uma classe filha que
# esquecer algum método abstrato também não pode ser criada. Quem implementa de verdade são
# RepositorioMemoria e RepositorioSQLite.
class Repositorio(ABC):
    """DAO: o contrato de acesso aos dados. Os serviços só conhecem esta interface,
    então tanto faz se os dados estão na memória ou no SQLite."""

    # --- escrita ---

    # Devolve o próximo id livre da coleção (ex.: "livros"): o maior id que existe + 1.
    @abstractmethod
    def proximo_id(self, colecao): ...

    # Serve para criar e para atualizar. Quem chama não precisa saber qual dos dois acontece.
    @abstractmethod
    def salvar(self, objeto):
        """Grava o objeto: insere se for novo, atualiza se já existir."""

    # Apaga o objeto do armazenamento.
    @abstractmethod
    def remover(self, objeto): ... # os 3 pontos indicam que o método não tem implementação, só a assinatura

    # Usado com `with repo.transacao():`. No SQLite vira BEGIN/COMMIT/ROLLBACK; na memória não faz nada.
    @abstractmethod
    def transacao(self):
        """Agrupa várias gravações: ou entram todas ou nenhuma."""

    # True se ainda não há livros. A semente usa isso para saber se precisa carregar os dados iniciais.
    @abstractmethod
    def esta_vazio(self): ...

    # Métodos que só leem. Os buscar_* devolvem UM objeto (ou None se não achar);
    # os listar_* devolvem uma lista (vazia se não houver nada).
    # --- consultas ---

    # Procura a conta pelo id.
    @abstractmethod
    def buscar_usuario(self, id_usuario): ...

    # Procura a conta pelo e-mail (usado no cadastro, para barrar e-mail repetido, e no login).
    @abstractmethod
    def buscar_usuario_por_email(self, email): ...

    # Todos os livros do catálogo.
    @abstractmethod
    def listar_livros(self): ...

    # Um livro pelo id.
    @abstractmethod
    def buscar_livro(self, id_livro): ...

    # Todos os gêneros (para os filtros do catálogo).
    @abstractmethod
    def listar_generos(self): ...

    # Todas as editoras (para os filtros do catálogo).
    @abstractmethod
    def listar_editoras(self): ...

    # O registro de estante de UMA pessoa para UM livro (None se o livro não está na estante dela).
    @abstractmethod
    def buscar_registro(self, usuario, livro): ...

    # Toda a estante de uma pessoa.
    @abstractmethod
    def listar_registros(self, usuario): ...

    # A avaliação que essa pessoa deu a esse livro (só existe uma por pessoa e livro).
    @abstractmethod
    def buscar_avaliacao(self, usuario, livro): ...

    # Avaliações de um livro; sem passar livro (None), devolve as de todos.
    @abstractmethod
    def listar_avaliacoes(self, livro=None): ...

    # Um comentário pelo id (usado para curtir).
    @abstractmethod
    def buscar_comentario(self, id_comentario): ...

    # O comentário dessa pessoa nesse livro (só existe um por pessoa e livro).
    @abstractmethod
    def buscar_comentario_de(self, usuario, livro): ...

    # Comentários de um livro; sem passar livro (None), devolve os de todos.
    @abstractmethod
    def listar_comentarios(self, livro=None): ...
