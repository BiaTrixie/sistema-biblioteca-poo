from werkzeug.security import check_password_hash, generate_password_hash


class Usuario:
    def __init__(
        self,
        id: int,
        nome: str,
        email: str,
        senha: str,
        admin: bool = False,
        protegida: bool = False, # Para senha protegida (hash) vinda do banco, não refaz o hash
    ) -> None:
        self.__id = self.__validar_id(id)
        self.__nome = self.__validar_texto(nome, "nome de usuário é obrigatório")
        self.__email = self.__validar_email(email)
        senha = self.__validar_texto(senha, "senha é obrigatória")
        # protegida=True: a senha já veio como hash (lida do banco), então não refaz o hash
        self.__senha = senha if protegida else generate_password_hash(senha)
        self.__admin = self.__validar_admin(admin)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def email(self) -> str:
        return self.__email

    @property
    def admin(self) -> bool:
        return self.__admin

    @property
    def senha_protegida(self) -> str:
        """O hash da senha, que é o que se grava no banco. A senha em si ninguém lê."""
        return self.__senha

    def atualizar_nome(self, nome: str) -> None:
        self.__nome = self.__validar_texto(nome, "nome de usuário é obrigatório")

    def atualizar_email(self, email: str) -> None:
        self.__email = self.__validar_email(email)

    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.__senha, senha)

    def alterar_senha(self, senha_atual: str, senha_nova: str) -> None:
        if not self.verificar_senha(senha_atual):
            raise ValueError("senha atual incorreta")
        self.__senha = generate_password_hash(self.__validar_texto(senha_nova, "senha é obrigatória"))

    def __validar_id(self, id: int) -> int:
        if isinstance(id, bool) or not isinstance(id, int) or id < 1:
            raise ValueError("id inválido")
        return id

    def __validar_texto(self, valor: str, mensagem: str) -> str:
        if not isinstance(valor, str):
            raise ValueError(mensagem)
        texto = valor.strip()
        if not texto:
            raise ValueError(mensagem)
        return texto

    def __validar_email(self, email: str) -> str:
        email_limpo = self.__validar_texto(email, "email é obrigatório").lower()
        usuario, arroba, dominio = email_limpo.partition("@")
        if not usuario or not arroba or "." not in dominio or " " in email_limpo:
            raise ValueError("email inválido")
        return email_limpo

    def __validar_admin(self, admin: bool) -> bool:
        if not isinstance(admin, bool):
            raise ValueError("admin inválido")
        return admin

    def __str__(self) -> str:
        perfil = "admin" if self.__admin else "usuário"
        return f"[{self.__id}] {self.__nome} <{self.__email}> — {perfil}"
