from datetime import date

from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario


class AvaliacaoService:
    def __init__(self, repo):
        self.__repo = repo

    def avaliar(self, usuario, livro, nota, texto=""):
        """Uma avaliação por pessoa: avaliar de novo troca a anterior."""
        avaliacao = self.__repo.buscar_avaliacao(usuario, livro)
        if avaliacao is not None:
            avaliacao.nota = nota  # o setter valida de 1 a 5
            avaliacao.comentario = texto.strip()
            avaliacao.data = date.today()
        else:
            novo_id = self.__repo.proximo_id("avaliacoes")
            avaliacao = Avaliacao(novo_id, nota, date.today(), usuario, livro, texto.strip())
        self.__repo.salvar(avaliacao)
        return avaliacao

    def comentar(self, usuario, livro, texto):
        if not texto.strip():
            raise ValueError("escreva algo no comentário")
        novo_id = self.__repo.proximo_id("comentarios")
        comentario = Comentario(novo_id, texto.strip(), date.today(), usuario, livro)
        self.__repo.salvar(comentario)
        return comentario

    def curtir(self, id_comentario):
        comentario = self.__repo.buscar_comentario(id_comentario)
        if comentario is None:
            raise ValueError("comentário não encontrado")
        comentario.curtir()
        self.__repo.salvar(comentario)
        return comentario

    def do_livro(self, livro):
        """Avaliações e comentários de um livro, para a página do livro."""
        return self.__repo.listar_avaliacoes(livro), self.__repo.listar_comentarios(livro)

    def avaliacao_de(self, usuario, livro):
        return self.__repo.buscar_avaliacao(usuario, livro)

    def diario_recente(self, quantidade=5):
        """Últimas avaliações e comentários juntos, do mais novo para o mais antigo."""
        eventos = [("avaliou", a) for a in self.__repo.listar_avaliacoes()]
        eventos += [("comentou", c) for c in self.__repo.listar_comentarios()]
        eventos.sort(key=lambda evento: evento[1].data, reverse=True)
        return eventos[:quantidade]
