from datetime import date


def estrelas(media):
    if media is None:
        return "sem avaliações"
    return f"{media:.1f} ★"


class MenuPrincipal:
    """Terminal do Estante. Só pergunta e mostra; as regras ficam nos serviços."""

    def __init__(self, sistema):
        self.sistema = sistema
        self.usuario = None

    def executar(self):
        print("\n=== estante — o diário dos seus livros ===")
        while True:
            while self.usuario is None:
                self.tela_entrada()
            if self.menu():  # True: a pessoa escolheu sair do programa; False: só saiu da conta
                return

    def menu(self):
        while self.usuario is not None:
            opcao = input(
                "\n1) Início  2) Buscar  3) Minha estante  4) Abrir livro  5) Meu perfil  0) Sair\n> "
            ).strip()
            if opcao == "1":
                self.inicio()
            elif opcao == "2":
                self.buscar()
            elif opcao == "3":
                self.minha_estante()
            elif opcao == "4":
                self.abrir_livro()
            elif opcao == "5":
                self.perfil()
            elif opcao == "0":
                print("Até a próxima!")
                return True
            else:
                print("Opção inválida.")
        return False

    def tela_entrada(self):
        opcao = input("\n1) Entrar  2) Criar conta  0) Sair\n> ").strip()
        try:
            if opcao == "1":
                email = input("E-mail: ")
                senha = input("Senha: ")
                self.usuario = self.sistema.conta.entrar(email, senha)
            elif opcao == "2":
                nome = input("Nome: ")
                email = input("E-mail: ")
                senha = input("Senha: ")
                self.usuario = self.sistema.conta.cadastrar(nome, email, senha)
            elif opcao == "0":
                raise SystemExit
        except ValueError as erro:
            print(f"Erro: {erro}")

    def inicio(self):
        destaque = self.sistema.catalogo.livro_do_dia(date.today())
        print(f"\nLIVRO DO DIA: {destaque.nome} — {destaque.autora.nome}")
        print(f"  {destaque.sinopse}")

        print("\nPOPULARES ESTA SEMANA")
        for livro in self.sistema.catalogo.populares():
            media = self.sistema.catalogo.media(livro)
            print(f"  {livro.nome} — {livro.autora.nome} — {estrelas(media)}")

        print("\nDIÁRIO RECENTE")
        for tipo, item in self.sistema.avaliacao.diario_recente():
            print(f"  {item.usuario.nome} {tipo} {item.livro.nome} ({item.data})")

        resumo = self.sistema.estante.resumo(self.usuario)
        print(
            f"\nSUA ESTANTE: {resumo['total']} total, "
            f"{resumo['favoritos']} favoritos, {resumo['quero_ler']} quero ler"
        )

    def buscar(self):
        texto = input("Buscar por título, autora, gênero ou editora: ")
        genero = input(f"Gênero ({', '.join(self.sistema.catalogo.generos())}) ou Enter: ")
        editora = input(f"Editora ({', '.join(self.sistema.catalogo.editoras())}) ou Enter: ")
        livros = self.sistema.catalogo.buscar(texto, genero.strip(), editora.strip())
        self.listar_livros(livros)

    def listar_livros(self, livros):
        if not livros:
            print("Nenhum livro encontrado.")
        for livro in livros:
            media = estrelas(self.sistema.catalogo.media(livro))
            print(
                f"  [{livro.id}] {livro.nome} — {livro.ano} — {livro.genero.nome}"
                f" — {livro.editora.nome} — {livro.autora.nome} — {media}"
            )

    def minha_estante(self):
        filtro = input("Filtro (todos, lidos, favoritos, quero-ler): ").strip() or "todos"
        try:
            registros = self.sistema.estante.listar(self.usuario, filtro)
        except ValueError as erro:
            print(f"Erro: {erro}")
            return
        for registro in registros:
            print(f"  {registro}")

    def perfil(self):
        pessoa = self.usuario
        resumo = self.sistema.estante.resumo(pessoa)
        avaliacoes, comentarios = self.sistema.avaliacao.do_usuario(pessoa)
        print(f"\nPERFIL\n  Nome: {pessoa.nome}\n  E-mail: {pessoa.email}")
        print(f"  Tipo de conta: {'administrador' if pessoa.admin else 'leitor'}")
        print(
            f"  Estante: {resumo['total']} no total · {resumo['lidos']} lidos · "
            f"{resumo['favoritos']} favoritos · {resumo['quero_ler']} quero ler"
        )
        print(f"  Avaliações: {len(avaliacoes)} · Comentários: {len(comentarios)}")
        if input("\nSair da conta? (s/N) ").strip().lower() == "s":
            self.usuario = None
            print("Você saiu da conta.")

    def abrir_livro(self):
        self.listar_livros(self.sistema.catalogo.listar())
        try:
            livro = self.sistema.catalogo.obter(int(input("Número do livro: ")))
        except ValueError:
            livro = None
        if livro is None:
            print("Livro não encontrado.")
            return

        print(f"\n{livro.nome} — {livro.autora.nome}\n{livro.sinopse}")
        avaliacoes, comentarios = self.sistema.avaliacao.do_livro(livro)
        for avaliacao in avaliacoes:
            print(f"  {avaliacao.usuario.nome} deu nota {avaliacao.nota}. {avaliacao.comentario}")
        for comentario in comentarios:
            print(
                f"  [{comentario.id}] {comentario.usuario.nome}: {comentario.texto}"
                f" ({comentario.numero_likes} curtidas)"
            )
        self.acoes_do_livro(livro)

    def acoes_do_livro(self, livro):
        opcao = input(
            "\n1) Lido  2) Favorito  3) Quero ler  4) Avaliar  5) Comentar  6) Curtir comentário  Enter) voltar\n> "
        ).strip()
        status = {"1": "lido", "2": "favorito", "3": "quer_ler"}
        try:
            if opcao in status:
                self.sistema.estante.alternar(self.usuario, livro, status[opcao])
                print("Estante atualizada.")
            elif opcao == "4":
                nota = int(input("Nota (1 a 5): "))
                texto = input("Comentário da nota: ")
                self.sistema.avaliacao.avaliar(self.usuario, livro, nota, texto)
                print("Avaliação publicada.")
            elif opcao == "5":
                self.sistema.avaliacao.comentar(self.usuario, livro, input("Comentário (substitui o seu anterior neste livro): "))
                print("Comentário publicado.")
            elif opcao == "6":
                comentario = self.sistema.avaliacao.curtir(int(input("Número do comentário: ")), self.usuario)
                print("Curtido." if comentario.curtido_por(self.usuario) else "Curtida desfeita.")
        except ValueError as erro:
            print(f"Erro: {erro}")
