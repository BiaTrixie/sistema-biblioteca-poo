import unittest
from datetime import date, timedelta

from tests.fabricas import repo_memoria, repo_sqlite
from servicos.catalogo_service import CatalogoService


class TesteCatalogo:  # os testes; abaixo rodam uma vez com cada repositório
    def setUp(self):
        self.catalogo = CatalogoService(self.criar_repo())

    def nomes(self, livros):
        return [livro.nome for livro in livros]

    def test_lista_todos_os_livros(self):  # R6
        self.assertEqual(len(self.catalogo.listar()), 9)

    def test_busca_por_texto_ignora_maiusculas(self):  # R7
        self.assertEqual(self.nomes(self.catalogo.buscar("HOBBIT")), ["O Hobbit"])

    def test_busca_por_autora(self):  # R7
        self.assertEqual(self.nomes(self.catalogo.buscar("miller")), ["Circe"])

    def test_filtro_de_genero_e_editora(self):  # R8
        fantasia = self.catalogo.buscar(genero="Fantasia")
        self.assertEqual(len(fantasia), 2)
        so_arqueiro = self.catalogo.buscar(genero="Fantasia", editora="Arqueiro")
        self.assertEqual(self.nomes(so_arqueiro), ["O Nome do Vento"])

    def test_populares_comecam_pela_maior_media(self):  # R17
        primeiro = self.catalogo.populares()[0]
        self.assertEqual(self.catalogo.media(primeiro), 5.0)

    def test_livro_do_dia_muda_a_cada_dia(self):  # R17
        hoje = date(2026, 11, 13)
        self.assertEqual(self.catalogo.livro_do_dia(hoje).id, self.catalogo.livro_do_dia(hoje).id)
        amanha = self.catalogo.livro_do_dia(hoje + timedelta(days=1))
        self.assertNotEqual(self.catalogo.livro_do_dia(hoje).id, amanha.id)
        self.assertIn(amanha.id, [l.id for l in self.catalogo.listar()])


class TesteCatalogoMemoria(TesteCatalogo, unittest.TestCase):
    criar_repo = staticmethod(repo_memoria)


class TesteCatalogoSQLite(TesteCatalogo, unittest.TestCase):
    criar_repo = staticmethod(repo_sqlite)


if __name__ == "__main__":
    unittest.main()
