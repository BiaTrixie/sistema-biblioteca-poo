import unittest

from tests.fabricas import repo_memoria, repo_sqlite
from servicos.avaliacao_service import AvaliacaoService
from servicos.catalogo_service import CatalogoService


class TesteAvaliacao:  # os testes; abaixo rodam uma vez com cada repositório
    def setUp(self):
        self.repo = self.criar_repo()
        self.avaliacoes = AvaliacaoService(self.repo)
        self.catalogo = CatalogoService(self.repo)
        self.ana = self.repo.buscar_usuario(1)
        self.beto = self.repo.buscar_usuario(2)
        self.hobbit = self.repo.buscar_livro(1)

    def test_avaliar_recalcula_a_media(self):  # R12
        self.avaliacoes.avaliar(self.beto, self.hobbit, 3)
        self.assertEqual(self.catalogo.media(self.hobbit), 4.0)

    def test_nota_fora_de_1_a_5(self):  # R13
        for nota in (0, 6):
            with self.assertRaises(ValueError):
                self.avaliacoes.avaliar(self.beto, self.hobbit, nota)

    def test_avaliar_de_novo_substitui(self):  # R14
        self.avaliacoes.avaliar(self.ana, self.hobbit, 2, "mudei de ideia")
        avaliacoes, _ = self.avaliacoes.do_livro(self.hobbit)
        self.assertEqual(len(avaliacoes), 1)
        self.assertEqual(avaliacoes[0].nota, 2)

    def test_comentar(self):  # R15
        comentario = self.avaliacoes.comentar(self.beto, self.hobbit, "Muito bom")
        _, comentarios = self.avaliacoes.do_livro(self.hobbit)
        self.assertIn(comentario.id, [c.id for c in comentarios])
        with self.assertRaises(ValueError):
            self.avaliacoes.comentar(self.beto, self.hobbit, "   ")

    def test_curtir_soma_um(self):  # R16
        comentario = self.avaliacoes.curtir(1, self.beto)
        self.assertEqual(comentario.numero_likes, 1)

    def test_cada_pessoa_curte_uma_vez(self):  # R16
        self.avaliacoes.curtir(1, self.beto)
        comentario = self.avaliacoes.curtir(1, self.ana)  # outra pessoa soma
        self.assertEqual(comentario.numero_likes, 2)
        comentario = self.avaliacoes.curtir(1, self.beto)  # a mesma pessoa de novo desfaz, não soma
        self.assertEqual(comentario.numero_likes, 1)
        self.assertFalse(comentario.curtido_por(self.beto))

    def test_comentar_de_novo_substitui_o_antigo(self):  # R15
        primeiro = self.avaliacoes.comentar(self.beto, self.hobbit, "Muito bom")
        self.avaliacoes.curtir(primeiro.id, self.ana)
        segundo = self.avaliacoes.comentar(self.beto, self.hobbit, "Mudei de ideia")
        _, comentarios = self.avaliacoes.do_livro(self.hobbit)
        do_beto = [c for c in comentarios if c.usuario.id == self.beto.id]
        self.assertEqual(len(do_beto), 1)
        self.assertEqual(do_beto[0].texto, "Mudei de ideia")
        self.assertEqual(segundo.id, primeiro.id)
        self.assertEqual(do_beto[0].numero_likes, 0)  # as curtidas eram do texto antigo

    def test_diario_comeca_pelo_mais_novo(self):  # R17
        diario = self.avaliacoes.diario_recente()
        datas = [item.data for _, item in diario]
        self.assertEqual(datas, sorted(datas, reverse=True))


class TesteAvaliacaoMemoria(TesteAvaliacao, unittest.TestCase):
    criar_repo = staticmethod(repo_memoria)


class TesteAvaliacaoSQLite(TesteAvaliacao, unittest.TestCase):
    criar_repo = staticmethod(repo_sqlite)


if __name__ == "__main__":
    unittest.main()
