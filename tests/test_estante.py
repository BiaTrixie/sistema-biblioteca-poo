import unittest

from repositorios.semente import criar_repositorio
from servicos.estante_service import EstanteService


class TesteEstante(unittest.TestCase):
    def setUp(self):
        self.repo = criar_repositorio()
        self.estante = EstanteService(self.repo)
        self.ana, self.beto, _ = self.repo.usuarios
        self.hobbit = self.repo.livros[0]

    def test_status_vale_so_para_quem_marcou(self):  # R9
        self.estante.alternar(self.beto, self.hobbit, "lido")
        self.assertTrue(self.estante.registro(self.beto, self.hobbit).lido)
        self.assertEqual(len(self.estante.listar(self.beto)), 1)
        self.assertEqual(len(self.estante.listar(self.ana)), 6)

    def test_filtros_e_contadores(self):  # R10
        self.assertEqual(len(self.estante.listar(self.ana, "lidos")), 3)
        self.assertEqual(len(self.estante.listar(self.ana, "favoritos")), 2)
        self.assertEqual(len(self.estante.listar(self.ana, "quero-ler")), 3)
        self.assertEqual(
            self.estante.resumo(self.ana),
            {"total": 6, "favoritos": 2, "quero_ler": 3},
        )

    def test_marcar_de_novo_desmarca(self):  # R11
        self.estante.alternar(self.ana, self.hobbit, "favorito")
        self.assertFalse(self.estante.registro(self.ana, self.hobbit).favorito)
        self.assertEqual(len(self.estante.listar(self.ana)), 6)

    def test_sem_nenhum_status_o_livro_sai_da_estante(self):
        self.estante.alternar(self.ana, self.hobbit, "favorito")
        self.estante.alternar(self.ana, self.hobbit, "lido")
        self.assertIsNone(self.estante.registro(self.ana, self.hobbit))

    def test_filtro_invalido(self):
        with self.assertRaises(ValueError):
            self.estante.listar(self.ana, "inexistente")


if __name__ == "__main__":
    unittest.main()
