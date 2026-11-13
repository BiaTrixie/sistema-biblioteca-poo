# Guia de estudos: Estante

Use este guia para entender o sistema e apresentá-lo. Leia de cima para baixo: primeiro a visão geral, depois as pastas, depois um caminho completo, depois arquivo por arquivo.

## Resumo do que foi construído

| Etapa | Resultado |
|---|---|
| 1. Modelos | `Autora` restaurada, `lido` movido de `Livro` para `Estante`, bug dos likes corrigido, `Avaliacao` e `Comentario` guardam usuário e livro, nota validada de 1 a 5, `Usuario` com hash de senha |
| 2. Repositório (DAO) | Interface `Repositorio` com duas implementações: memória (testes) e SQLite em `dados/estante.db`. A semente tem 9 livros (3 inventados), 6 contas e a estante da Ana (6 no total, 2 favoritos, 3 quero ler) |
| 3. Serviços | Conta, catálogo (com o livro do dia), estante e avaliação, mais o padrão Strategy em `servicos/filtros.py` |
| 4. Terminal | `python3 main.py` percorre o roteiro completo |
| 5. Flask | As 6 telas no formato do professor (`app/`, `view/`, `static/`), com capas em SVG |
| 6. Testes | 55 testes: cada serviço roda com os dois repositórios, mais os testes de persistência |
| 7. UML | `docs/uml/diagrama_de_classes.md`, em Mermaid: domínio, Strategy, DAO e camadas |
| 8. Guia | Este arquivo, com as 10 perguntas da revisão respondidas com o nosso código |

## 1. O que é o sistema

O Estante é um diário de livros. Cada pessoa tem uma conta, marca livros como lido, favorito ou quero ler, dá nota de 1 a 5 e comenta.

Pense numa biblioteca de bairro. O acervo é da biblioteca: o livro existe para todo mundo. Mas "já li" e "quero ler" são de cada leitor. Por isso o sistema separa duas coisas: o `Livro` (do acervo) e a `Estante` (a ficha de uma pessoa sobre um livro).

Dois jeitos de usar, com as mesmas regras por baixo:

| Jeito | Comando | Para que serve |
|---|---|---|
| Terminal | `python3 main.py` | Roteiro completo em menu |
| Web (Flask) | `python3 mainFlask.py` e abrir `http://127.0.0.1:5000` | As 6 telas do protótipo |

Contas de teste (todas com a senha `123456`): `ana@email.com` (estante já cheia), `beto@email.com`, `carla@email.com`, `juliana@email.com`, `lucas@email.com` (Lucas Arruda) e `roberto@email.com` (estante vazia). As contas novas que você criar ficam gravadas no seu computador (seção 8). Testes: `python3 -m unittest discover tests`.

## 2. Mapa das pastas

```
modelos/        as classes do domínio (Livro, Usuario, Estante...)
repositorios/   o acesso aos dados (DAO): a interface, a versão em memória, a versão SQLite e a semente
servicos/       as regras do sistema (avaliar, buscar, marcar status...)
  filtros.py      o padrão Strategy
menus/          o terminal (só pergunta e mostra)
app/            o Flask: rotas.py (controller), view/ (HTML), static/ (CSS)
tests/          um arquivo de teste por serviço (cada um roda com os dois repositórios)
dados/          o banco de cada pessoa, estante.db (criado na 1ª execução, fora do git)
docs/uml/       os diagramas de classes
```

Por que dividir assim: cada pasta responde a uma pergunta só. "O que é um livro?" está em `modelos`. "Onde guardo?" está em `repositorios`. "Qual a regra?" está em `servicos`. "Como mostro?" está em `menus` e `app`. Se a regra de nota mudar, você mexe em um lugar só. Isso é o princípio de responsabilidade única (SRP) que o professor cobra.

## 3. Um caminho completo: a Ana avalia O Hobbit

Siga uma ação do clique até o objeto. É a melhor forma de entender como as pastas se conversam.

| Passo | Onde | O que acontece |
|---|---|---|
| 1 | `app/view/avaliar.html` | A Ana escolhe 5 estrelas, escreve e clica em "Publicar avaliação". O formulário envia um POST |
| 2 | `app/rotas.py`, função `avaliar` | Lê `nota` e `texto` do formulário e chama o serviço. Não decide nada |
| 3 | `servicos/avaliacao_service.py`, `avaliar` | Procura se a Ana já avaliou esse livro. Se sim, atualiza; se não, cria |
| 4 | `modelos/avaliacao.py` | O `Avaliacao` valida que a nota é de 1 a 5. Se não for, lança `ValueError` |
| 5 | `repositorios/repositorio_sqlite.py` | O serviço chama `repo.salvar(avaliacao)` e o repositório grava a linha na tabela `avaliacoes` (se a Ana já tinha avaliado, atualiza a mesma linha) |
| 6 | de volta na rota | Sem erro, redireciona para a página do livro. Com erro, mostra a mensagem na tela (`flash`) |

O terminal faz o mesmo caminho a partir do passo 3. O passo 3 em diante é idêntico nos dois, e é por isso que `menus/` e `app/` não têm regra de negócio.

## 4. Arquivo por arquivo

### modelos/ (o domínio)

| Arquivo | O que é | Detalhe importante |
|---|---|---|
| `usuario.py` | Pessoa com conta | Valida e-mail e senha no construtor. Guarda só o **hash** da senha (`senha_protegida`), nunca a senha; `verificar_senha` compara usando o hash |
| `livro.py` | Um livro do acervo | Tem gênero, editora e autora. Não sabe se foi lido: isso é da `Estante` |
| `genero.py`, `editora.py`, `autora.py` | Dados do livro | `Editora` e `Autora` se conhecem (agregação) |
| `estante.py` | A ficha de uma pessoa sobre um livro | Guarda `lido`, `favorito` e `quer_ler`. Uma ficha por par usuário e livro |
| `avaliacao.py` | Nota de 1 a 5 de uma pessoa sobre um livro | Valida a nota no construtor e no setter |
| `comentario.py` | Texto de uma pessoa sobre um livro | Tem `curtir()` que soma 1 |

Todas usam atributos privados (`self.__nome`) e `@property`. É o encapsulamento: de fora ninguém mexe direto no dado, só pelo caminho que a classe oferece e valida.

### repositorios/

| Arquivo | O que faz |
|---|---|
| `repositorio.py` | A **interface** (`Repositorio`, classe abstrata): lista o que os serviços podem pedir (`salvar`, `buscar_livro`, `listar_avaliacoes`...) sem dizer como é feito |
| `repositorio_memoria.py` | Uma implementação que guarda tudo em listas. Os dados somem ao fechar; usada nos testes |
| `repositorio_sqlite.py` | A outra implementação: guarda num arquivo SQLite (`dados/estante.db`), então os dados sobrevivem |
| `semente.py` | Cria o conteúdo inicial (livros, contas, estante da Ana, avaliações). Só roda quando o repositório está vazio |

Por que existe: os serviços só conhecem a interface `Repositorio`, não sabem se os dados estão na memória ou no arquivo. Isso é o **DAO** que o professor ensinou (interface mais uma implementação por tecnologia) e é polimorfismo na prática: trocar de implementação não muda uma linha dos serviços.

### servicos/ (as regras)

| Arquivo | Regras que cuida |
|---|---|
| `conta_service.py` | Cadastro (e-mail único) e login |
| `catalogo_service.py` | Listar, buscar, média das notas, populares e o livro do dia (um por dia, pela data) |
| `estante_service.py` | Marcar e desmarcar status, listar por filtro, contadores |
| `avaliacao_service.py` | Avaliar (uma por pessoa), comentar, curtir, diário recente |
| `filtros.py` | O padrão Strategy (próxima seção) |
| `sistema.py` | Abre o banco (`dados/estante.db`), enche com a semente no primeiro uso e monta os serviços. Terminal e Flask usam esta classe |

### menus/ e app/ (a fronteira com a pessoa)

| Arquivo | O que faz |
|---|---|
| `menus/menu_principal.py` | Menu de terminal: pergunta, chama o serviço, imprime |
| `app/__init__.py` | Cria o `app` Flask. `template_folder="view"` é como no exemplo do professor |
| `app/rotas.py` | Uma função por tela ou ação. Lê o formulário, chama o serviço, escolhe a página |
| `app/view/*.html` | As telas. `base.html` é o esqueleto (topo e mensagens); as outras o estendem |
| `app/static/css/style.css` | Tema escuro e verde do protótipo |
| `app/static/img/capas/N.svg` | Capa do livro de id N, desenhada à mão em SVG (sem texto; o título é escrito pelo HTML por cima). Livro sem arquivo usa `padrao.svg` |
| `mainFlask.py` | Duas linhas que sobem o servidor |

A rota `exigir_login` (em `rotas.py`) manda qualquer pessoa sem sessão para o login, menos as telas de entrada e cadastro.

## 5. O padrão de projeto: Strategy

**O problema.** Buscar livros tem várias regras: por texto, por gênero, por editora. A estante também: todos, lidos, favoritos, quero ler. Sem padrão, o serviço viraria uma pilha de `if/elif`.

**A solução.** Cada regra vira uma classe pequena com o mesmo método, `passa(item)`, que responde sim ou não. O serviço monta uma lista de filtros e o `aplicar` deixa passar só quem passa em todos.

```python
class Filtro(ABC):
    @abstractmethod
    def passa(self, item) -> bool: ...

class FiltroGenero(Filtro):
    def passa(self, livro):
        return livro.genero.nome.lower() == self.__nome
```

**Por que escolhemos este.** Ele aparece em duas telas do protótipo (estante e busca), e acrescentar um filtro novo é criar uma classe, sem mexer no serviço. Observer e Singleton caberiam, mas seriam forçados.

| Parte do Strategy | No nosso código |
|---|---|
| Interface da estratégia | `Filtro` (classe abstrata) |
| Estratégias concretas | `FiltroTexto`, `FiltroGenero`, `FiltroEditora`, `FiltroTodos`, `FiltroLido`, `FiltroFavorito`, `FiltroQueroLer` |
| Quem usa | `CatalogoService.buscar` e `EstanteService.listar` |

Detalhe honesto: nos filtros do catálogo o item é um `Livro`; nos da estante é um registro `Estante`. A ideia é a mesma, só muda o tipo do item.

## 6. UML

Os diagramas estão em `docs/uml/diagrama_de_classes.md`: classes do domínio, o Strategy e as camadas. Lá há uma tabela de leitura das setas.

## 7. Perguntas que o professor pode fazer (com a resposta do nosso código)

| Pergunta da revisão | Resposta usando o Estante |
|---|---|
| Encapsulamento | `Avaliacao`: o atributo `__nota` é privado; só se muda pelo setter, que valida de 1 a 5 |
| Interface x classe abstrata | `Filtro` e `Repositorio` são abstratas: só dizem "o que sabem fazer" (`passa`, `salvar`...), cada filha decide o como |
| SRP e camadas | Modelo guarda dado, serviço aplica regra, rota só liga formulário e serviço |
| Composição x herança | Herança: filtros herdam de `Filtro`. Composição: o serviço usa filtros, não herda deles |
| Classe x objeto | `Livro` é a classe; "O Hobbit" é um objeto dela |
| Agregação x composição | `Editora` tem `Autora` (agregação): apagar a editora não apaga a autora |
| Navegabilidade | `Estante` conhece `Usuario` e `Livro`, mas o `Livro` não conhece a `Estante` |
| Polimorfismo | `aplicar` chama `f.passa(item)` sem saber qual filtro é. E os serviços chamam `repo.salvar(x)` sem saber se é memória ou SQLite |
| Tipos de associação | Estante, Avaliação e Comentário ligam Usuário e Livro (muitos para um) |
| Acoplamento e coesão | O terminal e o Flask só dependem de `Sistema`; cada serviço cuida de um assunto |

## 8. Onde os dados ficam

Os dados ficam num arquivo SQLite no seu computador: `dados/estante.db`. Na primeira execução o arquivo é criado e a semente o enche (livros, contas de teste, a estante da Ana). Daí em diante tudo que você faz é gravado nele.

| Situação | O que acontece |
|---|---|
| Você cria a conta `fulano@email.com` | Ela é gravada na tabela `usuarios` e continua lá depois de fechar o programa |
| Você reinicia o Flask (ou o modo `debug` recarrega ao salvar um arquivo) | Nada se perde: o arquivo continua o mesmo |
| Outra pessoa roda o projeto no computador dela | Ela cria o próprio `estante.db` e só vê as contas da semente: o arquivo não vai para o git |
| Você usa o terminal e o Flask | Os dois leem o mesmo arquivo, então veem as mesmas contas |
| Você quer começar do zero | Feche o programa e apague `dados/estante.db`; ele volta com a semente |

Como o banco é organizado: uma tabela para cada tipo de objeto (`usuarios`, `livros`, `estantes`, `avaliacoes`, `comentarios`...). As regras importantes também são protegidas pelo próprio banco: e-mail único, uma avaliação por pessoa e por livro, nota de 1 a 5. O código valida primeiro e dá a mensagem; o banco é a segunda trava.

Dois cuidados que o SQLite exigiu e que valem na apresentação:

- **Objeto novo a cada leitura.** Ao ler do banco, `Usuario` e `Livro` são reconstruídos, então dois objetos "iguais" não são o mesmo objeto na memória. Por isso o sistema compara por `id`, nunca por identidade (`is`).
- **Os testes rodam nos dois repositórios.** Cada teste de serviço executa com `RepositorioMemoria` e com `RepositorioSQLite`; se os dois passam, os serviços de fato não dependem de onde os dados estão.

Se os colegas mudarem as classes e as tabelas, o arquivo antigo fica incompatível: o programa avisa e pede para apagar `dados/estante.db`. Não apaga sozinho, para não destruir contas.

## 9. Limitações conhecidas

- Os dados são locais (seção 8): dois computadores nunca compartilham contas. Compartilhar exigiria um banco em servidor.
- Não há migração de banco: se as tabelas mudarem, é preciso apagar `dados/estante.db` e perder as contas criadas nele.
- A senha usa hash, mas as contas da semente têm todas a senha `123456` (e o mesmo hash), só para demonstração.
- A chave da sessão do Flask está escrita no código. Aceitável num trabalho acadêmico.
- No protótipo, a busca "fantasia" mostra Circe (Mitologia), mas a busca real só devolve os 2 livros de fantasia. O desenho tinha essa inconsistência.
- Os livros 7, 8 e 9 (baleias, árvores e cosmos), seus autores e editoras são inventados para a demonstração.
- Os modelos dos colegas foram alterados (Autora restaurada, `lido` movido para `Estante`, bug dos likes, usuário e livro nas avaliações e comentários). Combinar com o grupo antes de subir.
- O `Usuario` ganhou hash de senha (`protegida` e `senha_protegida`).
