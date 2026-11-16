from datetime import date

from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario


# Cuida de notas, comentários e curtidas, e dos resumos que aparecem no perfil e na página do livro.
class AvaliacaoService:
    def __init__(self, repo):
        self.__repo = repo # recebe o repositório (banco de dados) que será usado para salvar e buscar avaliações e comentários

    def avaliar(self, usuario, livro, nota, texto=""):
        """Uma avaliação por pessoa: avaliar de novo troca a anterior."""
        avaliacao = self.__repo.buscar_avaliacao(usuario, livro) #busca a avaliação existente do usuário para o livro
        if avaliacao is not None:
            avaliacao.nota = nota  # o setter valida de 1 a 5
            avaliacao.comentario = texto.strip()
            avaliacao.data = date.today()
        else:
            novo_id = self.__repo.proximo_id("avaliacoes")
            avaliacao = Avaliacao(novo_id, nota, date.today(), usuario, livro, texto.strip()) #strip remove espaços em branco do início e do fim do texto.
        self.__repo.salvar(avaliacao)
        return avaliacao

    # Regra: um comentário por pessoa e livro. Comentar de novo troca o texto (e zera as curtidas, ver Comentario.substituir).
    def comentar(self, usuario, livro, texto):
        if not texto.strip():
            raise ValueError("escreva algo no comentário")
        comentario = self.__repo.buscar_comentario_de(usuario, livro)
        if comentario is not None:  # um comentário por pessoa e livro: o novo sobrescreve
            comentario.substituir(texto.strip(), date.today())
        else:
            novo_id = self.__repo.proximo_id("comentarios")
            comentario = Comentario(novo_id, texto.strip(), date.today(), usuario, livro)
        self.__repo.salvar(comentario)
        return comentario

    # Delega a regra (cada pessoa conta uma vez) ao próprio Comentario e depois manda salvar.
    def curtir(self, id_comentario, usuario):
        """Cada pessoa curte uma vez; clicar de novo desfaz a curtida."""
        comentario = self.__repo.buscar_comentario(id_comentario)
        if comentario is None:
            raise ValueError("comentário não encontrado")
        comentario.alternar_curtida(usuario) # alterna a curtida do usuário no comentário (curtir/descurtir)
        self.__repo.salvar(comentario)
        return comentario

    # Essa função é usada para buscar o comentário de um usuário específico para um livro específico. Se o usuário não tiver comentado sobre o livro, retorna None.
    def comentario_de(self, usuario, livro):
        return self.__repo.buscar_comentario_de(usuario, livro)

    # Filtra pelo id da pessoa (comparar ids é mais seguro que comparar objetos).
    def do_usuario(self, usuario):
        """Avaliações e comentários feitos por uma pessoa, para o perfil."""
        avaliacoes = [a for a in self.__repo.listar_avaliacoes() if a.usuario.id == usuario.id] # o a aqui é cada avaliação na lista de avaliações do repositório. O filtro seleciona apenas as avaliações cujo usuário tem o mesmo id que o usuário fornecido.
        comentarios = [c for c in self.__repo.listar_comentarios() if c.usuario.id == usuario.id] # c = comentarios 
        return avaliacoes, comentarios

    # Duas listas de uma vez; o repositório já filtra por livro.
    def do_livro(self, livro):
        """Avaliações e comentários de um livro, para a página do livro."""
        return self.__repo.listar_avaliacoes(livro), self.__repo.listar_comentarios(livro)

    # A nota que essa pessoa já deu a esse livro, ou None.
    def avaliacao_de(self, usuario, livro):
        return self.__repo.buscar_avaliacao(usuario, livro)

    # Mistura avaliações e comentários numa lista só de pares ("avaliou"/"comentou", objeto),
    # ordena pela data (do mais novo ao mais antigo) e pega os primeiros.
    #funciona para mostrar as últimas atividades do sistema, como avaliações e comentários recentes.
    # filtra por livro e usuario? A resposta é não, ele pega todas as avaliações e comentários do repositório, independentemente do livro ou usuário. A filtragem por livro e usuário é feita em outros métodos, como do_usuario() e do_livro().
    def diario_recente(self, quantidade=5):
        """Últimas avaliações e comentários juntos, do mais novo para o mais antigo."""
        eventos = [("avaliou", a) for a in self.__repo.listar_avaliacoes()]
        eventos += [("comentou", c) for c in self.__repo.listar_comentarios()]
        eventos.sort(key=lambda evento: evento[1].data, reverse=True) #lambda evento: evento[1].data é uma função anônima que recebe um evento (uma tupla com o tipo de evento e o objeto) e retorna a data do objeto (evento[1]). O parâmetro reverse=True faz com que a lista seja ordenada do mais novo para o mais antigo.
        return eventos[:quantidade]
