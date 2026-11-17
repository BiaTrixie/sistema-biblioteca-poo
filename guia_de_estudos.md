# Guia de estudos: Estante

Use este guia para entender o sistema e apresentá-lo. Leia de cima para baixo: primeiro a visão geral, depois as pastas, depois um caminho completo, depois arquivo por arquivo.

## Resumo do que está no código

| Parte | O que é |
|---|---|
| Modelos | `Usuario`, `Livro`, `Genero`, `Editora`, `Autor`, `Estante`, `Avaliacao` e `Comentario`. A nota vai de 1 a 5. A senha fica só como hash. Lido, favorito e quero ler são da `Estante`, não do `Livro` |
| Repositórios | Uma classe por entidade, mais `Conexao`, que abre o SQLite `dados/estante.db` |
| Serviços | Conta, catálogo, estante e avaliação. A busca e o filtro da estante usam Strategy em `servicos/filtros.py` |
| API | `api/rotas.py` responde JSON em `/api`, com `GET`, `POST` e `PATCH`. O login devolve um token |
| Páginas | `app/view/*.html` são o desenho. `app/static/js/api.js` chama a API |
| UML | `docs/uml/diagrama_de_classes.md`: domínio, Strategy, repositórios e camadas |

## 1. O que é o sistema

O Estante é um diário de livros. Cada pessoa tem uma conta, marca livros como lido, favorito ou quero ler, dá nota de 1 a 5 e comenta.

Pense numa biblioteca de bairro. O acervo é da biblioteca: o livro existe para todo mundo. "Já li" e "quero ler" são de cada leitor. Por isso o sistema separa o `Livro` (o acervo) da `Estante` (a ficha de uma pessoa sobre um livro).

Para subir o site:

```text
python mainFlask.py
```

Abra `http://127.0.0.1:5000`. As telas pedem os dados em `/api`

Se o arquivo `dados/estante.db` já existir no seu computador, ele continua com o acervo e as contas antigas.

## 2. Mapa das pastas

```text
modelos/        as classes do domínio (Livro, Usuario, Estante...)
repositorios/   Conexao e um repositório por entidade
servicos/       as regras (avaliar, buscar, marcar status...)
  filtros.py      o padrão Strategy
api/            as rotas JSON e a tradução objeto -> JSON
app/view/       as páginas HTML
app/static/     CSS, JavaScript e capas
dados/          estante.db, fora do git
docs/uml/       os diagramas de classes
mainFlask.py    sobe o servidor
```

Cada pasta responde a uma pergunta. "O que é um livro?" está em `modelos`. "Onde guardo?" está em `repositorios`. "Qual a regra?" está em `servicos`. "Como a pessoa vê e como a API entrega?" está em `app` e `api`. Se a regra da nota mudar, a mudança é no modelo e no serviço.

## 3. Um caminho completo: avaliar um livro

| Passo | Onde | O que acontece |
|---|---|---|
| 1 | `app/view/avaliar.html` | A pessoa escolhe a nota, escreve e clica em publicar. O JavaScript manda `POST /api/livros/<id>/avaliacoes` com `{nota, texto}` e o token |
| 2 | `api/rotas.py`, `avaliar` | Confere o token, lê o JSON e chama o serviço. Não decide a regra |
| 3 | `servicos/avaliacao_service.py`, `avaliar` | Se essa pessoa já avaliou o livro, atualiza. Se não, cria |
| 4 | `modelos/avaliacao.py` | O setter de `nota` exige um inteiro de 1 a 5. Fora disso, lança `ValueError` |
| 5 | `repositorios/avaliacao_repositorio.py` | `salvar` grava na tabela `avaliacoes`. O mesmo id atualiza a linha |
| 6 | de volta na rota | O JSON da avaliação volta com 201 (nova) ou 200 (substituiu). A página vai para `/livro/<id>`. Se der erro, a mensagem aparece no aviso |

A página não valida a nota. Quem valida é o modelo; quem decide "uma avaliação por pessoa" é o serviço.

## 4. Arquivo por arquivo

### modelos/

| Arquivo | O que é | Detalhe importante |
|---|---|---|
| `usuario.py` | Pessoa com conta | Valida e-mail e senha no construtor. Guarda só o hash (`senha_protegida`). `verificar_senha` compara com o hash. `protegida=True` é para quando o hash já veio do banco |
| `livro.py` | Um livro do acervo | Tem gênero, editora e autor. Não sabe se foi lido |
| `genero.py`, `editora.py`, `autor.py` | Dados do livro | `Editora` e `Autor` se conhecem (agregação) |
| `estante.py` | A ficha de uma pessoa sobre um livro | `lido`, `favorito` e `quer_ler`. Lido e quero ler não ficam juntos: marcar um desmarca o outro |
| `avaliacao.py` | Nota de 1 a 5 | A validação está no construtor e no setter |
| `comentario.py` | Texto sobre um livro | `curtidas` é um conjunto de ids. `alternar_curtida` curte e, de novo, desfaz. `substituir` troca o texto e zera as curtidas |

Os atributos importantes são privados (`self.__nota`) e saem por `@property`. Isso é o encapsulamento.

### repositorios/

| Arquivo | O que faz |
|---|---|
| `conexao.py` | Abre o SQLite, cria as tabelas na versão 3 e faz as migrações da 1 para a 2 e da 2 para a 3. `gravar` insere ou atualiza pelo id. `transacao` agrupa vários comandos |
| `usuario_repositorio.py` | Salva e busca pessoa, por id ou por e-mail |
| `livro_repositorio.py` | Livro, gênero, editora e autor. Lê o catálogo uma vez e segura em memória até alguém salvar |
| `estante_repositorio.py` | A ficha de uma pessoa. Precisa do repositório de livros para remontar o `Livro` |
| `avaliacao_repositorio.py` | Notas. Remonta usuário e livro ao ler |
| `comentario_repositorio.py` | Comentário e, na mesma transação, as linhas de `curtidas` |

Cada serviço recebe só o repositório da sua entidade. `CatalogoService` é a exceção que recebe dois, livros e avaliações, porque a média não está no livro.

### servicos/

| Arquivo | Regras |
|---|---|
| `conta_service.py` | Cadastro (e-mail único) e login |
| `catalogo_service.py` | Listar, buscar, média, populares e o livro do dia (um por dia, pela data) |
| `estante_service.py` | Liga e desliga status. Sem nenhum status, a ficha sai da estante. Lista por filtro e conta o resumo |
| `avaliacao_service.py` | Uma avaliação por pessoa. Um comentário por pessoa e livro: o novo substitui. Curtir é um interruptor. Diário recente e a atividade do perfil |
| `filtros.py` | Strategy, na próxima seção |
| `sistema.py` | Abre o banco e entrega os repositórios aos serviços. A API usa esta classe |

### api/ e app/

| Arquivo | O que faz |
|---|---|
| `api/__init__.py` | Cria o Flask, o `Sistema` e registra os dois blueprints |
| `api/rotas.py` | Um endpoint por ação. `exigir_login` lê o token. Rotas públicas seguem sem conta; as outras respondem 401 |
| `api/serializacao.py` | Transforma o objeto em dicionário para o JSON |
| `app/paginas.py` | Entrega o HTML. Não busca livro nem estante |
| `app/static/js/api.js` | `fetch` em `/api`, guarda `estante_token` no `localStorage` e monta o topo |
| `app/view/*.html` | As telas. O script de cada uma preenche a página com a resposta da API |
| `app/static/css/style.css` | O visual |
| `app/static/img/capas/` | Capa SVG dos livros 1 a 9. O JavaScript pede `/static/img/capas/<id>.svg` |
| `mainFlask.py` | Sobe o servidor em modo debug |

O token fica num dicionário na memória do processo (`TOKENS` em `api/rotas.py`). Reiniciar o Flask pede login de novo. Os dados do banco continuam.

Rotas públicas, sem token: `POST /api/contas`, `POST /api/login`, `GET /api/livros`, `GET /api/livros/<id>`, `GET /api/livros/populares`, `GET /api/livros/do-dia`, `GET /api/generos`, `GET /api/editoras`, avaliações, comentários e `GET /api/diario`.

Rotas da conta, com `Authorization: Bearer <token>`: `GET /api/perfil`, `POST /api/sair`, `GET` e `PATCH` da estante, `POST` de avaliação e de comentário, `PATCH /api/comentarios/<id>` para curtir.

As páginas de início, estante, livro, avaliar e perfil chamam `exigirLogin()` e voltam para `/login` se não houver token. Buscar, entrar e criar conta abrem sem sessão. O catálogo em si é público; a estante é de quem entrou.

## 5. O padrão de projeto: Strategy

Buscar livros tem várias regras: por texto, por gênero, por editora. A estante também: todos, lidos, favoritos, quero ler. Cada regra é uma classe com `passa(item)`. O serviço monta a lista e `aplicar` deixa passar só quem passa em todas.

```python
class Filtro(ABC):
    @abstractmethod
    def passa(self, item) -> bool: ...

class FiltroGenero(Filtro):
    def passa(self, livro):
        return livro.genero.nome.lower() == self.__nome
```

| Parte do Strategy | No código |
|---|---|
| Classe abstrata | `Filtro` |
| Estratégias | `FiltroTexto`, `FiltroGenero`, `FiltroEditora`, `FiltroTodos`, `FiltroLido`, `FiltroFavorito`, `FiltroQueroLer` |
| Quem usa | `CatalogoService.buscar` e `EstanteService.listar` |

No catálogo o item é um `Livro`. Na estante é um registro `Estante`. O método é o mesmo.

## 6. UML

Os diagramas estão em `docs/uml/diagrama_de_classes.md`: domínio, Strategy, repositórios e camadas.

## 7. Perguntas que o professor pode fazer

| Pergunta | Resposta com este código |
|---|---|
| Encapsulamento | Em `Avaliacao`, `__nota` é privado. Só muda pelo setter, que exige inteiro de 1 a 5 |
| Classe abstrata | `Filtro` declara `passa`. Cada filtro concreto implementa a sua regra |
| SRP e camadas | O modelo guarda e valida o dado. O serviço aplica a regra. A rota só traduz HTTP e JSON. A página só mostra |
| Composição e herança | Os filtros herdam de `Filtro`. O serviço usa os filtros, não herda deles |
| Classe e objeto | `Livro` é a classe. Cada linha da tabela `livros` vira um objeto |
| Agregação | `Editora` conhece `Autor`. Apagar a editora não apaga o autor |
| Navegabilidade | `Estante` conhece `Usuario` e `Livro`. O `Livro` não conhece a `Estante` |
| Polimorfismo | `aplicar` chama `f.passa(item)` sem saber qual filtro recebeu |
| Associação | Estante, avaliação e comentário ligam uma pessoa a um livro |
| Acoplamento | A rota depende de `Sistema`. Cada serviço depende do repositório da sua entidade |

## 8. Onde os dados ficam

O arquivo é `dados/estante.db`. A pasta `dados/` não entra no git. Na primeira abertura, se o arquivo não existe, `Conexao` cria as tabelas e grava `user_version = 3`. Não há carga automática de livros nem de contas.

| Situação | O que acontece |
|---|---|
| `POST /api/contas` com nome, e-mail e senha | A pessoa entra na tabela `usuarios` e continua depois de fechar o programa |
| O Flask reinicia, inclusive o reload do debug | O banco fica. O token da memória some e a pessoa entra de novo |
| Outro computador roda o projeto | Cria o próprio `estante.db`, vazio, até alguém cadastrar |
| Apagar `dados/estante.db` | O próximo start cria as tabelas de novo, sem o acervo anterior |

Tabelas: `usuarios`, `generos`, `editoras`, `autores`, `editora_autor`, `livros`, `estantes`, `avaliacoes`, `comentarios`, `curtidas`. O banco também segura regras: e-mail único, uma avaliação por pessoa e livro, um comentário por pessoa e livro, nota de 1 a 5. O código valida antes e devolve a mensagem; o banco é a segunda trava.

Ao ler, o repositório monta um objeto novo. Duas leituras da mesma pessoa não são o mesmo objeto na memória. Por isso a comparação é pelo `id`.

A versão do esquema é o `user_version` do SQLite. Versão 0 cria as tabelas. Versão 1 roda `__migrar_da_versao_1`: separa lido de quero ler, recria comentários com uma linha por pessoa e livro, e zera curtidas que eram só um número. Versão 2 roda `__migrar_da_versao_2`: `autora` vira `autor` nas tabelas. Outra versão faz o programa recusar o arquivo e pedir para apagá-lo.

## 9. Limitações

- O banco é local. Dois computadores não compartilham contas.
- As migrações escritas são da versão 1 para a 2 e da 2 para a 3.
- Não há endpoint para cadastrar livro. O acervo que aparece hoje já estava no arquivo.
- O token vive na memória do processo. Reiniciar o servidor desloga todo mundo.
- As contas antigas de demonstração usam a senha `123456`.
- A capa é pedida pelo id do livro. Sem o SVG, o cartão fica sem imagem. `padrao.svg` está na pasta, e a página não troca para ele sozinha.
- Os livros 7, 8 e 9, com autores e editoras inventados, existem só no banco que já estava neste computador.
