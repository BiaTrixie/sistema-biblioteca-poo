import unittest

from repositorios.semente import criar_repositorio
from servicos.avaliacao_service import AvaliacaoService
from servicos.catalogo_service import CatalogoService


class TesteAvaliacao(unittest.TestCase):
    def setUp(self):
        self.repo = criar_repositorio()
        self.avaliacoes = AvaliacaoService(self.repo)
        self.catalogo = CatalogoService(self.repo)
        self.ana, self.beto, _ = self.repo.usuarios
        self.hobbit = self.repo.livros[0]

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
        self.assertIn(comentario, comentarios)
        with self.assertRaises(ValueError):
            self.avaliacoes.comentar(self.beto, self.hobbit, "   ")

    def test_curtir_soma_um(self):  # R16
        comentario = self.avaliacoes.curtir(1)
        self.assertEqual(comentario.numero_likes, 1)

    def test_diario_comeca_pelo_mais_novo(self):  # R17
        diario = self.avaliacoes.diario_recente()
        datas = [item.data for _, item in diario]
        self.assertEqual(datas, sorted(datas, reverse=True))


if __name__ == "__main__":
    unittest.main()
