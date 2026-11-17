from datetime import date

from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario


class AvaliacaoService:
    def __init__(self, avaliacoes, comentarios):
        self.__avaliacoes = avaliacoes
        self.__comentarios = comentarios

    def avaliar(self, usuario, livro, nota, texto=""):
        """Uma avaliação por pessoa: avaliar de novo troca a anterior."""
        avaliacao = self.__avaliacoes.buscar(usuario, livro)
        if avaliacao is not None:
            avaliacao.nota = nota  # o setter valida de 1 a 5
            avaliacao.comentario = texto.strip()
            avaliacao.data = date.today()
        else:
            avaliacao = Avaliacao(
                self.__avaliacoes.proximo_id(), nota, date.today(), usuario, livro, texto.strip()
            )
        self.__avaliacoes.salvar(avaliacao)
        return avaliacao

    def comentar(self, usuario, livro, texto):
        if not texto.strip():
            raise ValueError("escreva algo no comentário")
        comentario = self.__comentarios.buscar_de(usuario, livro)
        if comentario is not None:  # um comentário por pessoa e livro: o novo sobrescreve
            comentario.substituir(texto.strip(), date.today())
        else:
            comentario = Comentario(
                self.__comentarios.proximo_id(), texto.strip(), date.today(), usuario, livro
            )
        self.__comentarios.salvar(comentario)
        return comentario

    def curtir(self, id_comentario, usuario):
        """Cada pessoa curte uma vez; clicar de novo desfaz a curtida."""
        comentario = self.__comentarios.buscar(id_comentario)
        if comentario is None:
            raise ValueError("comentário não encontrado")
        comentario.alternar_curtida(usuario)
        self.__comentarios.salvar(comentario)
        return comentario

    def comentario_de(self, usuario, livro):
        return self.__comentarios.buscar_de(usuario, livro)

    def do_usuario(self, usuario):
        """Avaliações e comentários feitos por uma pessoa, para o perfil."""
        avaliacoes = [a for a in self.__avaliacoes.listar() if a.usuario.id == usuario.id]
        comentarios = [c for c in self.__comentarios.listar() if c.usuario.id == usuario.id]
        return avaliacoes, comentarios

    def do_livro(self, livro):
        """Avaliações e comentários de um livro, para a página do livro."""
        return self.__avaliacoes.listar(livro), self.__comentarios.listar(livro)

    def avaliacao_de(self, usuario, livro):
        return self.__avaliacoes.buscar(usuario, livro)

    def diario_recente(self, quantidade=5):
        """Últimas avaliações e comentários juntos, do mais novo para o mais antigo."""
        eventos = [("avaliou", a) for a in self.__avaliacoes.listar()]
        eventos += [("comentou", c) for c in self.__comentarios.listar()]
        eventos.sort(key=lambda evento: evento[1].data, reverse=True)
        return eventos[:quantidade]
