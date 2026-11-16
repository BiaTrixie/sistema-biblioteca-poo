from modelos.usuario import Usuario


# Cuida de cadastro e login. Não sabe onde as contas ficam: pede ao repositório.
class ContaService:
    # O serviço recebe o repositório pronto (injeção de dependência) e não cria nada.
    def __init__(self, repo):
        self.__repo = repo

    # Regra do serviço: e-mail único. Os campos (nome, e-mail, senha) quem valida é a classe Usuario.
    def cadastrar(self, nome, email, senha):
        if self.__repo.buscar_usuario_por_email(email) is not None:
            raise ValueError("e-mail já cadastrado")
        novo_id = self.__repo.proximo_id("usuarios")
        usuario = Usuario(novo_id, nome, email, senha)  # a classe valida os campos
        self.__repo.salvar(usuario)
        return usuario

    # A mensagem de erro é a mesma para e-mail inexistente e senha errada, para não revelar quais e-mails existem.
    def entrar(self, email, senha):
        usuario = self.__repo.buscar_usuario_por_email(email)
        if usuario is None or not usuario.verificar_senha(senha):
            raise ValueError("e-mail ou senha incorretos")
        return usuario

    # Usado pelo Flask para recuperar quem está logado a partir do id guardado na sessão.
    def buscar_por_id(self, id_usuario):
        return self.__repo.buscar_usuario(id_usuario)
