import unittest
from datetime import date, timedelta

from repositorios.semente import criar_repositorio
from servicos.catalogo_service import CatalogoService


class TesteCatalogo(unittest.TestCase):
    def setUp(self):
        self.catalogo = CatalogoService(criar_repositorio())

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
        self.assertIs(self.catalogo.livro_do_dia(hoje), self.catalogo.livro_do_dia(hoje))
        amanha = self.catalogo.livro_do_dia(hoje + timedelta(days=1))
        self.assertIsNot(self.catalogo.livro_do_dia(hoje), amanha)
        self.assertIn(amanha, self.catalogo.listar())


if __name__ == "__main__":
    unittest.main()
