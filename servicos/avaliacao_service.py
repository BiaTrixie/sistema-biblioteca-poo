from datetime import date

from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario


class AvaliacaoService:
    def __init__(self, repo):
        self.__repo = repo

    def avaliar(self, usuario, livro, nota, texto=""):
        """Uma avaliação por pessoa: avaliar de novo troca a anterior."""
        anterior = next(
            (a for a in self.__repo.avaliacoes if a.usuario is usuario and a.livro is livro),
            None,
        )
        if anterior is not None:
            anterior.nota = nota  # o setter valida de 1 a 5
            anterior.comentario = texto.strip()
            anterior.data = date.today()
            return anterior

        novo_id = self.__repo.proximo_id(self.__repo.avaliacoes)
        avaliacao = Avaliacao(novo_id, nota, date.today(), usuario, livro, texto.strip())
        self.__repo.avaliacoes.append(avaliacao)
        return avaliacao

    def comentar(self, usuario, livro, texto):
        if not texto.strip():
            raise ValueError("escreva algo no comentário")
        novo_id = self.__repo.proximo_id(self.__repo.comentarios)
        comentario = Comentario(novo_id, texto.strip(), date.today(), usuario, livro)
        self.__repo.comentarios.append(comentario)
        return comentario

    def curtir(self, id_comentario):
        comentario = next((c for c in self.__repo.comentarios if c.id == id_comentario), None)
        if comentario is None:
            raise ValueError("comentário não encontrado")
        comentario.curtir()
        return comentario

    def do_livro(self, livro):
        """Avaliações e comentários de um livro, para a página do livro."""
        avaliacoes = [a for a in self.__repo.avaliacoes if a.livro is livro]
        comentarios = [c for c in self.__repo.comentarios if c.livro is livro]
        return avaliacoes, comentarios

    def avaliacao_de(self, usuario, livro):
        return next(
            (a for a in self.__repo.avaliacoes if a.usuario is usuario and a.livro is livro),
            None,
        )

    def diario_recente(self, quantidade=5):
        """Últimas avaliações e comentários juntos, do mais novo para o mais antigo."""
        eventos = [("avaliou", a) for a in self.__repo.avaliacoes]
        eventos += [("comentou", c) for c in self.__repo.comentarios]
        eventos.sort(key=lambda evento: evento[1].data, reverse=True)
        return eventos[:quantidade]
