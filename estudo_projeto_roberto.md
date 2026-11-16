# ====================================================
## 1. Mapa das pastas e conceitos relacionados

```
modelos/        as classes do domínio (Livro, Usuario, Estante...)
repositorios/   o acesso aos dados (DAO): a interface, a versão em memória, a versão SQLite e a semente
servicos/       as regras do sistema (avaliar, buscar, marcar status...)
  filtros.py      o padrão Strategy
menus/          o terminal (só pergunta e mostra)
app/            o Flask: rotas.py (controller), view/ (HTML), static/ (CSS)
tests/          um arquivo de teste por serviço (cada um roda com os dois repositórios)
dados/          o banco do sistema, um por máquina que roda o sistema, estante.db (criado na 1ª execução, fora do git)
docs/uml/       os diagramas de classes
```

Por que dividir assim: cada pasta responde a uma pergunta só. "O que é um livro?" está em `modelos`. "Onde guardo?" está em `repositorios`. "Qual a regra?" está em `servicos`. "Como mostro?" está em `menus` e `app`. Se a regra de nota mudar, você mexe em um lugar só. Isso é o princípio de responsabilidade única (SRP) que o professor cobra.

- **DAO**: Data Access Object.
    1. Um objeto DAO serve para encapsular o acesso a dados, de forma que a lógica de negócios não precise saber como os dados são armazenados ou recuperados.
    Em linguagem simples, cuida da busca e do armazenamento de dados, isso é POO, pois: 
        1.1 **Abstração**: a interface esconde o "como" e mostra só o "o quê".
        1.2 **Polimorfismo**: duas classes diferentes respondem aos mesmos métodos, e o serviço usa qualquer uma.
        1.3 **Baixo acoplamento**: as regras de negócio não ficam presas ao SQLite. Por isso os testes dos serviços rodam com os dois repositórios (os de persistência testam só o SQLite).

    2. É um padrão de projeto que separa a lógica de acesso a dados da lógica de negócios. No nosso caso, temos uma interface `Repositorio` e duas implementações (classes filhas): `RepositorioMemoria` e `RepositorioSQLite`. O aplicativo real usa `RepositorioSQLite` (arquivo definido pela variável `ESTANTE_DB`, ou o caminho padrão em `servicos/sistema.py`). Os testes dos serviços usam `RepositorioMemoria` e também o SQLite em `:memory:`.

# ====================================================
## 2. Rodmap nas pastas e arquivos: 

### 1. Modelos/: 

- Essa pasta contém as classes (com excessão das de DAO, que ficam em `repositorios/`) que representam os conceitos do domínio do sistema, com seus dados e as regras de cada uma. Domínio do sistema é o conjunto de conceitos que o sistema manipula. Por exemplo, no nosso caso, os conceitos são: Livro, Usuario, Estante, Avaliacao, etc. Ela não sabe guardar em banco (responsabilidade DAO), não mostra nada na tela (responsabilidade da pasta menis/menu_principal.py no caso de uso pelo terminal (Main.py) e pasta app/rotas.py,view/ e static/ para web(flask)) e não decide fluxo de telas (menus/ no terminal e app/ no Flask.). Só diz o que é cada coisa e o que ela aceita ou recusa. 

- **Camada de interface** é a parte do sistema que conversa com quem usa: recebe o que a pessoa pede e mostra o resultado. Ela não guarda dados nem aplica as regras do sistema, só faz a ponte entre a pessoa e os serviços. Não tem a ver com as classes de interface (classes que só tem métodos abstratos).

- A seta -> nas funções (métodos das classes) indica o que a função devolve. Exemplo: 

```python
def __init__(self, id: int, nome: str) -> None: # não devolve nada
def id(self) -> int: # devolve um inteiro
def buscar_por_id(self, id: int) -> "Livro": # retorna um objeto da classe Livro
```

### 2. Serviços/: 

- Essa pasta contém as regras do sistema, que usam os modelos e os repositórios. Cada serviço é uma classe que implementa uma regra **(regra = ação)** do sistema, como avaliar um livro, buscar livros, marcar status de leitura, etc. 

- Cada serviço tem um método principal (ex: `avaliar()`, `buscar()`, `marcar_status()`) que é chamado pela interface (terminal ou web). Os serviços não sabem como os dados são guardados (isso é responsabilidade dos repositórios) nem como são mostrados (isso é responsabilidade da interface). Eles só aplicam as regras do sistema. 

- Para cada regra aplicada, o serviço pode chamar métodos dos modelos (ex: `Livro`, `Usuario`, `Avaliacao`) e métodos do repositório (ex: `Repositorio.buscar_livro_por_id()`, `Repositorio.salvar_avaliacao()`). Exemplo: 

```python
class ServicoAvaliacao:
    def avaliar(self, id_usuario: int, id_livro: int, nota: int) -> None:
        usuario = self.repositorio.buscar_usuario_por_id(id_usuario)
        livro = self.repositorio.buscar_livro_por_id(id_livro)
        avaliacao = Avaliacao(usuario, livro, nota)
        self.repositorio.salvar_avaliacao(avaliacao)
```

- O serviço pede, o repositório entrega ou grava, e nenhum faz o trabalho do outro.

- **Sistema.py**: Arquivo com a função de montar o sistema, cria um Sistema() para a versão de terminal e um Sistema para a versão de Flask. A função dele é:
    1. Escolher onde os dadods ficam (em memória ou SQLite)
    2. Chama criar_repositorio() para criar o repositório escolhido e, se for a primeira vez, encher o banco com a semente.
    3. Criar os quatro serviços (ContaService, CatalogoService, EstanteService e AvaliacaoService) com o mesmo repositório, e entrega cada um como atributo do Sistema() criado. Assim, o terminal e o Flask só precisam de Sistema() e usam sistema.conta, .catalogo, .estante, .avaliacao.


### 3. Repositórios/: 

- Essa pasta contém as classes que implementam o acesso a dados (DAO). Cada repositório(`repositorio_memoria.py` e `repositorio_sqlite`) é uma classe que implementa a interface `Repositorio`, que define os métodos que devem ser implementados para acessar ou armazenar os dados. O repositório não sabe como os dados são mostrados (isso é responsabilidade da interface (em app/ para webFlask)) nem como as regras do sistema são aplicadas (isso é responsabilidade dos serviços). Ele só cuida de buscar e guardar os dados.

- `semente.py` é um módulo que cria dados de teste para o repositório SQLite, para que o sistema tenha algo para mostrar na primeira execução. Ele é chamado pelo `RepositorioSQLite` quando o banco de dados não existe.

- A principal diferença entre os repositórios é que `RepositorioMemoria` guarda os dados em memória (em listas e dicionários) e `RepositorioSQLite` guarda os dados em um banco de dados SQLite (um arquivo chamado estante.db). Com isso, no arquivo do REPOSQLITE, precisamos definir as tabelas do banco, e alguns métodos adicionais de conexão com o banco, fora que os métodos de busca e gravação de dados são diferentes, pois um usa listas e dicionários e o outro usa SQL.



### 4. Tests/: 

- Essa pasta contém os arquivos de teste para cada serviço. Cada arquivo de teste (`test_servico_avaliacao.py`, `test_servico_busca.py`, `test_servico_estante.py`) testa os métodos do serviço correspondente. Os testes usam o repositório em memória (`RepositorioMemoria`) e também o repositório SQLite em memória (`:memory:`) para garantir que os serviços funcionam corretamente com ambos os tipos de repositórios.

- Nessa pasta temos testes unitários (testam uma função ou método isoladamente) e testes de integração (testam a interação entre diferentes partes do sistema, como serviços e repositórios). **Com excessão do test_persistencia (que é um teste de integração que utiliza o sqlite de verdade), todos os outros testes são unitários e agem em cima dos serviços, pois usam o repositório em memória e não dependem do banco de dados SQLite.** 

- O arquivo fabricas.py cria repositórios de teste (tanto de memória quanto SQLite) e popula com dados de teste, para que os testes possam ser executados sem depender de dados reais. Ele é usado pelos arquivos de teste. 

### 5. Dados/:

- Essa pasta contém o banco de dados SQLite do sistema, que é um arquivo chamado estante.db. Cada pessoa que roda o sistema tem seu próprio arquivo de banco de dados, que é criado na primeira execução do sistema. O arquivo estante.db não é versionado no git, para evitar conflitos entre diferentes usuários.

- O .db  tem 10 tabelas: 

┌──────────────────────────────┬───────────┐
│            Tabela            │  Linhas   │
├──────────────────────────────┼───────────┤
│ livros                       │ 9         │
├──────────────────────────────┼───────────┤
│ generos / editoras / autoras │ 7 / 9 / 9 │
├──────────────────────────────┼───────────┤
│ usuarios                     │ 7         │
├──────────────────────────────┼───────────┤
│ estantes                     │ 7         │
├──────────────────────────────┼───────────┤
│ avaliacoes                   │ 18        │
├──────────────────────────────┼───────────┤
│ comentarios / curtidas       │ 5 / 2     │
└──────────────────────────────┴───────────┘

A semente cria 6 contas, 15 avaliações e 3 comentários. Você tem 7 usuários, 18 avaliações e 5 comentários, então já foi usado: tem uma conta, três avaliações e dois comentários criados à mão.

- **"E se a estrutura do banco mudar?":** VERSAO_DO_ESQUEMA guarda a versão no arquivo, e o repositório sabe migrar da 1 para a 2 sem perder contas.

### 6. Menus/:

- Essa pasta contém os arquivos que implementam a interface do terminal (linha de comando). Cada arquivo de menu (`menu_principal.py`, `menu_usuario.py`, `menu_livro.py`, etc.) implementa um menu específico do sistema, com suas opções e submenus. Os menus chamam os serviços para executar as ações solicitadas pelo usuário.

- Quem usa o quê: 

┌────────────────────────────────┬────────────────────────┬──────────────────────────────────────┐
│              Peça              │   Terminal (main.py)   │         Flask (mainFlask.py)         │
├────────────────────────────────┼────────────────────────┼──────────────────────────────────────┤
│ Ponto de partida               │ main.py                │ mainFlask.py, que importa app        │
├────────────────────────────────┼────────────────────────┼──────────────────────────────────────┤
│ Interface                      │ MenuPrincipal (menus/) │ app/rotas.py e app/view/*.html       │
├────────────────────────────────┼────────────────────────┼──────────────────────────────────────┤
│ Cria o Sistema()               │ main.py                │ app/__init__.py:9 (variável sistema) │
├────────────────────────────────┼────────────────────────┼──────────────────────────────────────┤
│ Serviços, modelos, repositório │ Os mesmos              │ Os mesmos                            │
└────────────────────────────────┴────────────────────────┴──────────────────────────────────────┘



### 7. App/:

- **É a interface web do sistema, em Flask.** Recebe cliques e formulários no navegador, chama os serviços e devolve páginas HTML. Ela não sabe guardar dados nem aplicar regras do sistema, só faz a ponte entre o navegador e os serviços. Basicamente, pega a resposta dos serviços e devolve para o navegador, que mostra para a pessoa.

- **Um exemplo completo**: clicar em "Favorito"

    1. O navegador envia POST /livro/1/status com status=favorito.
    2. exigir_login confere se há usuario_id na sessão. Se não houver, manda para o login.
    3. mudar_status busca o livro e chama sistema.estante.alternar(usuario, livro, "favorito").
    4. Essa é a mesma chamada que a opção 2 do terminal faz. A regra vive no serviço.
    5. O redirect manda o navegador para GET /livro/1.
    6. livro() recarrega os dados e renderiza livro.html, onde o botão aparece destacado.

**Os arquivos**: 

┌──────────────────────────┬────────────────────────────────────────────────────┐
│         Arquivo          │                       Papel                        │
├──────────────────────────┼────────────────────────────────────────────────────┤
│ mainFlask.py (raiz)      │ Ponto de partida: importa o app e roda o servidor  │
│                          │ com app.run(debug=True)                            │
├──────────────────────────┼────────────────────────────────────────────────────┤
│ app/__init__.py          │ Cria o objeto Flask, define a chave da sessão e    │
│                          │ cria um Sistema() que todas as rotas usam          │
├──────────────────────────┼────────────────────────────────────────────────────┤
│ app/rotas.py             │ As rotas (URLs), cada uma ligada a uma função. É o │
│                          │  controlador da arquitetura                        │
├──────────────────────────┼────────────────────────────────────────────────────┤
│ app/view/*.html          │ Páginas HTML (templates). Usam a sintaxe {{ }} e   │
│                          │ {% %} do Jinja, que o Flask preenche com dados     │
├──────────────────────────┼────────────────────────────────────────────────────┤
│ app/view/base.html       │ Esqueleto comum: cabeçalho, menu, mensagens de     │
│                          │ aviso. As outras páginas herdam dele               │
├──────────────────────────┼────────────────────────────────────────────────────┤
│ app/view/_macros.html    │ Pedaços reutilizáveis: a capa do livro, as         │
│                          │ estrelas, a miniatura                              │
├──────────────────────────┼────────────────────────────────────────────────────┤
│ app/static/css/style.css │ Estilo visual                                      │
├──────────────────────────┼────────────────────────────────────────────────────┤
│ app/static/img/capas/    │ Uma capa SVG por livro (1.svg a 9.svg) e uma       │
│                          │ padrão                                             │
└──────────────────────────┴────────────────────────────────────────────────────┘

**As rotas e os serviços que cada uma chama:**

┌────────────────────┬──────┬─────────────────────────┬──────────────────────┐
│      Endereço      │ Méto │        O que faz        │   Serviço chamado    │
│                    │  do  │                         │                      │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│                    │ GET, │ Mostra o formulário e   │                      │
│ /login             │      │ confe
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│                    │ GET, │                         │                      │
│ /cadastro          │      │ Cria conta              │ conta.cadastrar      │
│                    │ POST │                         │                      │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│ /sair              │ POST │ Limpa a sessão          │ nenhum               │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│                    │      │ Início: livro do dia,   │ catalogo, avaliacao. │
│ /                  │ GET  │ populares, diário,      │ diario_recente,      │
│                    │      │ resumo                  │ estante.resumo       │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│ /buscar            │ GET  │ Busca co
│                    │      │ =...&editora=...        │                      │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│ /estante           │ GET  │ Estante com filtro      │ estante.listar       │
│                    │      │ (?filtro=lidos)         │                      │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│                    │      │                         │ catalogo.obter,      │
│ /livro/<id>        │ GET  │ Página do livro         │ avaliacao.do_livro,  │
│                    │      │                         │ estante.registro     │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│ /livro/<id>/status │ POST │ Lido, favorito ou quero │ estante.alternar     │
│                    │      │  ler
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│ /livro/<id>/avalia │ GET, │ Formulário e publicação │                      │
│ r                  │      │  da nota                │ avaliacao.avaliar    │
│                    │ POST │                         │                      │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│ /livro/<id>/coment │ POST │ Publica ou substitui o  │ avaliacao.comentar   │
│ ar                 │      │ comentário              │                      │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│ /comentario/<id>/c │ POST │ Curte ou desfaz         │ avaliacao.curtir     │
│ urtir              │      │                         │                      │
├────────────────────┼──────┼─────────────────────────┼──────────────────────┤
│ /perfil            │ GET  │ Dados da conta e opção  │ estante.resumo,      │
│                    │      │ de sair                 │ avaliacao.do_usuario │
└────────────────────┴──────┴─────────────────────────┴──────────────────────┘

