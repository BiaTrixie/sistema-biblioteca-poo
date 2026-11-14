import unittest

from tests.fabricas import repo_memoria, repo_sqlite
from servicos.conta_service import ContaService


class TesteConta:  # os testes; abaixo rodam uma vez com cada repositório
    def setUp(self):
        self.contas = ContaService(self.criar_repo())

    def test_entrar_com_dados_certos(self):  # R1
        usuario = self.contas.entrar("ana@email.com", "123456")
        self.assertEqual(usuario.nome, "Ana")

    def test_conta_do_roberto_existe_na_semente(self):
        self.assertEqual(self.contas.entrar("roberto@email.com", "123456").nome, "Roberto")

    def test_senha_nao_fica_legivel(self):
        usuario = self.contas.cadastrar("Duda", "duda@email.com", "abc123")
        self.assertNotIn("abc123", usuario.senha_protegida)
        self.assertTrue(usuario.verificar_senha("abc123"))

    def test_entrar_com_senha_errada(self):  # R2
        with self.assertRaises(ValueError):
            self.contas.entrar("ana@email.com", "errada")

    def test_cadastrar_cria_usuario(self):  # R3
        usuario = self.contas.cadastrar("Duda", "duda@email.com", "abc123")
        self.assertEqual(self.contas.buscar_por_id(usuario.id).email, "duda@email.com")

    def test_email_repetido_e_recusado(self):  # R4
        with self.assertRaises(ValueError):
            self.contas.cadastrar("Outra Ana", "ANA@email.com", "abc123")


class TesteContaMemoria(TesteConta, unittest.TestCase):
    criar_repo = staticmethod(repo_memoria)


class TesteContaSQLite(TesteConta, unittest.TestCase):
    criar_repo = staticmethod(repo_sqlite)


if __name__ == "__main__":
    unittest.main()
