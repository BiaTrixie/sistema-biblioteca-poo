import sqlite3
import tempfile
import threading
import unittest
from datetime import date
from pathlib import Path

from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario
from modelos.usuario import Usuario
from repositorios.repositorio_sqlite import RepositorioSQLite
from repositorios.semente import LIVROS, criar_repositorio
from servicos.sistema import Sistema


class TestePersistencia(unittest.TestCase):
    """Coisas que só o SQLite faz: guardar em arquivo e proteger os dados."""

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = Path(self.pasta.name) / "estante.db"
        self.abertos = []

    def tearDown(self):
        for repo in self.abertos:
            repo.fechar()
        self.pasta.cleanup()

    def abrir(self):
        repo = RepositorioSQLite(self.caminho)
        self.abertos.append(repo)
        return repo

    def test_conta_sobrevive_a_reabrir_o_arquivo(self):
        Sistema(self.abrir()).conta.cadastrar("Duda", "duda@email.com", "abc123")
        outro = Sistema(self.abrir())  # como se o programa tivesse sido fechado e aberto de novo
        self.assertEqual(outro.conta.entrar("duda@email.com", "abc123").nome, "Duda")

    def test_alteracoes_tambem_persistem(self):
        sistema = Sistema(self.abrir())
        ana, hobbit = sistema.conta.buscar_por_id(1), sistema.catalogo.obter(1)
        sistema.avaliacao.avaliar(ana, hobbit, 2, "mudei de ideia")
        sistema.estante.alternar(ana, hobbit, "quer_ler")

        outro = Sistema(self.abrir())
        self.assertEqual(outro.avaliacao.avaliacao_de(ana, hobbit).nota, 2)
        self.assertTrue(outro.estante.registro(ana, hobbit).quer_ler)

    def test_reabrir_nao_duplica_a_semente(self):
        for _ in range(3):
            Sistema(self.abrir())
        self.assertEqual(len(self.abrir().listar_livros()), len(LIVROS))

    def test_duas_execucoes_semeando_juntas(self):
        """O Flask com debug carrega o app em dois processos ao mesmo tempo."""
        def abrir_e_semear():
            criar_repositorio(self.abrir())
        threads = [threading.Thread(target=abrir_e_semear) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(self.abrir().listar_livros()), len(LIVROS))

    def test_terminal_e_flask_enxergam_os_dados_um_do_outro(self):
        a, b = Sistema(self.abrir()), Sistema(self.abrir())
        a.conta.cadastrar("Duda", "duda@email.com", "abc123")
        self.assertEqual(b.conta.entrar("duda@email.com", "abc123").nome, "Duda")

    def test_senha_fica_como_hash_no_arquivo(self):
        Sistema(self.abrir()).conta.cadastrar("Duda", "duda@email.com", "abc123")
        banco = sqlite3.connect(self.caminho)
        (senha,) = banco.execute("SELECT senha FROM usuarios WHERE email = 'duda@email.com'").fetchone()
        banco.close()
        self.assertNotIn("abc123", senha)

    def test_banco_recusa_email_repetido(self):
        repo = criar_repositorio(self.abrir())
        with self.assertRaises(ValueError):
            repo.salvar(Usuario(99, "Outra Ana", "ana@email.com", "abc123"))

    def test_banco_recusa_segunda_avaliacao_da_mesma_pessoa(self):
        repo = criar_repositorio(self.abrir())
        ana, hobbit = repo.buscar_usuario(1), repo.buscar_livro(1)  # a Ana já avaliou o Hobbit na semente
        with self.assertRaises(ValueError):
            repo.salvar(Avaliacao(99, 3, date.today(), ana, hobbit))

    def test_curtida_persiste(self):
        sistema = Sistema(self.abrir())
        beto, arvores = sistema.conta.buscar_por_id(2), sistema.catalogo.obter(8)
        sistema.avaliacao.curtir(3, beto)  # comentário do Lucas no livro de árvores

        _, comentarios = Sistema(self.abrir()).avaliacao.do_livro(arvores)
        self.assertEqual(comentarios[0].numero_likes, 1)
        self.assertTrue(comentarios[0].curtido_por(beto))

    def test_comentario_substituido_persiste_sem_as_curtidas_antigas(self):
        sistema = Sistema(self.abrir())
        ana, hora = sistema.conta.buscar_por_id(1), sistema.catalogo.obter(4)
        self.assertEqual(sistema.avaliacao.comentario_de(ana, hora).numero_likes, 5)  # da semente
        sistema.avaliacao.comentar(ana, hora, "Reli e gostei mais ainda")

        comentario = Sistema(self.abrir()).avaliacao.comentario_de(ana, hora)
        self.assertEqual(comentario.texto, "Reli e gostei mais ainda")
        self.assertEqual(comentario.numero_likes, 0)

    def test_banco_recusa_segundo_comentario_da_mesma_pessoa(self):
        repo = criar_repositorio(self.abrir())
        ana, hobbit = repo.buscar_usuario(1), repo.buscar_livro(1)  # a Ana já comentou o Hobbit na semente
        with self.assertRaises(ValueError):
            repo.salvar(Comentario(99, "outro", date.today(), ana, hobbit))

    def test_banco_da_versao_1_e_migrado_sem_perder_contas(self):
        criar_repositorio(self.abrir()).fechar()
        banco = sqlite3.connect(self.caminho)  # volta o arquivo para o formato antigo (versão 1)
        banco.executescript("""
            DROP TABLE curtidas; DROP TABLE comentarios;
            CREATE TABLE comentarios (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL,
                livro_id INTEGER NOT NULL, texto TEXT NOT NULL, data TEXT NOT NULL,
                numero_likes INTEGER NOT NULL);
            INSERT INTO comentarios VALUES (1, 1, 1, 'antigo', '2026-09-25', 3),
                (2, 1, 1, 'novo', '2026-09-26', 0), (3, 2, 3, 'outro', '2026-09-27', 7);
            UPDATE estantes SET lido = 1, quer_ler = 1 WHERE id = 1;
            PRAGMA user_version = 1;""")
        banco.close()

        sistema = Sistema(self.abrir())  # abre com o código novo e migra
        ana, hobbit = sistema.conta.buscar_por_id(1), sistema.catalogo.obter(1)
        self.assertEqual(sistema.conta.entrar("ana@email.com", "123456").nome, "Ana")  # conta preservada
        self.assertEqual(sistema.avaliacao.comentario_de(ana, hobbit).texto, "novo")  # ficou o mais novo
        registro = sistema.estante.registro(ana, hobbit)
        self.assertTrue(registro.lido and not registro.quer_ler)
        self.assertEqual(sistema.avaliacao.curtir(3, ana).numero_likes, 1)  # as curtidas antigas zeraram

    def test_arquivo_de_versao_antiga_e_recusado(self):
        self.abrir().fechar()
        banco = sqlite3.connect(self.caminho)
        banco.execute("PRAGMA user_version = 99")
        banco.close()
        with self.assertRaises(RuntimeError):
            RepositorioSQLite(self.caminho)


if __name__ == "__main__":
    unittest.main()
