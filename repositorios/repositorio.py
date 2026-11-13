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


class Repositorio(ABC):
    """DAO: o contrato de acesso aos dados. Os serviços só conhecem esta interface,
    então tanto faz se os dados estão na memória ou no SQLite."""

    # --- escrita ---

    @abstractmethod
    def proximo_id(self, colecao): ...

    @abstractmethod
    def salvar(self, objeto):
        """Grava o objeto: insere se for novo, atualiza se já existir."""

    @abstractmethod
    def remover(self, objeto): ...

    @abstractmethod
    def transacao(self):
        """Agrupa várias gravações: ou entram todas ou nenhuma."""

    @abstractmethod
    def esta_vazio(self): ...

    # --- consultas ---

    @abstractmethod
    def buscar_usuario(self, id_usuario): ...

    @abstractmethod
    def buscar_usuario_por_email(self, email): ...

    @abstractmethod
    def listar_livros(self): ...

    @abstractmethod
    def buscar_livro(self, id_livro): ...

    @abstractmethod
    def listar_generos(self): ...

    @abstractmethod
    def listar_editoras(self): ...

    @abstractmethod
    def buscar_registro(self, usuario, livro): ...

    @abstractmethod
    def listar_registros(self, usuario): ...

    @abstractmethod
    def buscar_avaliacao(self, usuario, livro): ...

    @abstractmethod
    def listar_avaliacoes(self, livro=None): ...

    @abstractmethod
    def buscar_comentario(self, id_comentario): ...

    @abstractmethod
    def buscar_comentario_de(self, usuario, livro): ...

    @abstractmethod
    def listar_comentarios(self, livro=None): ...
