import unittest

from tests.fabricas import repo_memoria, repo_sqlite
from servicos.estante_service import EstanteService


class TesteEstante:  # os testes; abaixo rodam uma vez com cada repositório
    def setUp(self):
        self.repo = self.criar_repo()
        self.estante = EstanteService(self.repo)
        self.ana = self.repo.buscar_usuario(1)
        self.beto = self.repo.buscar_usuario(2)
        self.hobbit = self.repo.buscar_livro(1)

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


class TesteEstanteMemoria(TesteEstante, unittest.TestCase):
    criar_repo = staticmethod(repo_memoria)


class TesteEstanteSQLite(TesteEstante, unittest.TestCase):
    criar_repo = staticmethod(repo_sqlite)


if __name__ == "__main__":
    unittest.main()
