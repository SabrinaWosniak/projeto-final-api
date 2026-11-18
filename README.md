# API Financeira — Projeto Final

API REST em Django REST Framework para controle financeiro pessoal.

## Domínio e entidades
- **Categoria**: classifica os lançamentos (ex.: Alimentação, Lazer). Campos: `nome` (único).
- **Conta**: conta bancária. Campos: `nome`, `banco`, `criada_em`, `saldo` (calculado: entradas − saídas).
- **Lancamento**: movimentação da conta. Campos: `conta`, `categoria` (opcional), `tipo` (`entrada` ou `saida`), `descricao`, `valor`, `data`.

## Regras de negócio e validações
- Uma **saída não pode deixar a conta com saldo negativo** (também vale ao editar um lançamento, ao movê-lo para outra conta e ao excluir uma entrada).
- `valor` deve ser maior que zero; `descricao` deve ter ao menos 3 caracteres; `tipo` deve ser `entrada` ou `saida`.
- Erros de validação retornam **400** com JSON explicando o problema.

## Instalação e execução
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    DJANGO_SUPERUSER_PASSWORD=professor123 python manage.py createsuperuser --noinput --username professor --email professor@teste.com
    python manage.py runserver

O banco é SQLite (`db.sqlite3`, criado pelo `migrate`) e os dados permanecem após reiniciar o servidor. Documentação navegável em `http://127.0.0.1:8000/api/`.

## Credenciais de teste
- Usuário: `professor`
- Senha: `professor123` (somente para teste)

## Autenticação (token)
    POST /api/login/    corpo: {"username": "professor", "password": "professor123"}
    resposta 200: {"token": "abc123..."}

Enviar nas requisições protegidas o cabeçalho `Authorization: Token abc123...`.
**GET é público**; **POST, PUT, PATCH e DELETE exigem token** (sem token: 401).

## Endpoints
Cada recurso (`/api/categorias/`, `/api/contas/`, `/api/lancamentos/`) possui:

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| GET | /api/{recurso}/ | Lista paginada | 200 |
| GET | /api/{recurso}/{id}/ | Um registro | 200 (404 se não existir) |
| POST | /api/{recurso}/ | Cria | 201 (400 se inválido) |
| PUT | /api/{recurso}/{id}/ | Atualização completa | 200 |
| PATCH | /api/{recurso}/{id}/ | Atualização parcial | 200 |
| DELETE | /api/{recurso}/{id}/ | Exclui | 204 |

### Exemplo de corpo (POST/PUT de lançamento)
    {"conta": 1, "categoria": 2, "tipo": "saida", "descricao": "Supermercado", "valor": "250.00", "data": "2026-11-10"}

### Exemplo de resposta (GET de conta)
    {"id": 1, "nome": "Conta Corrente", "banco": "Banco do Brasil", "criada_em": "2026-11-18T10:00:00-03:00", "saldo": "1947.60"}

### Exemplo de erro (400 — regra de negócio)
    {"valor": ["Saldo insuficiente. Saldo disponível: 1947.60."]}

## Consulta de dados
Resposta paginada (5 por página): `{"count": 11, "next": "...", "previous": null, "results": [...]}`

| Parâmetro | Recurso | Função | Exemplo |
|---|---|---|---|
| `page` | todos | Página | `?page=2` |
| `search` | lançamentos (descrição), contas (nome, banco), categorias (nome) | Busca textual | `?search=mercado` |
| `ordering` | lançamentos (`data`, `valor`, `id`), contas (`nome`, `criada_em`), categorias (`nome`) | Ordenação (`-` = decrescente) | `?ordering=-valor` |
| `tipo` | lançamentos | Filtra entrada/saida | `?tipo=saida` |
| `conta`, `categoria` | lançamentos | Filtra por id | `?conta=1` |
| `data_inicio`, `data_fim` | lançamentos | Período (AAAA-MM-DD) | `?data_inicio=2026-11-01` |
| `valor_min`, `valor_max` | lançamentos | Faixa de valor | `?valor_min=100` |

Os parâmetros podem ser combinados: `/api/lancamentos/?tipo=saida&search=mercado&ordering=-valor&page=1`

---

## Apresentação do projeto (explicação por texto)

Olá, professor!

Eu tenho uma ansiedade social bastante forte e, por isso, tenho muita dificuldade de falar em público. Para conseguir mostrar de verdade o que eu fiz, decidi explicar o projeto por texto, aqui no README. Espero que essa explicação ajude na avaliação.

Antes de começar, quero ser transparente: usei inteligência artificial como ferramenta de apoio. Ela me ajudou a montar a estrutura do código, a escrever as tabelas e a documentação deste README e a corrigir erros que apareceram durante o desenvolvimento. Sei que o enunciado permite isso, desde que eu compreenda o que entreguei. Por isso escrevi esta parte: para explicar com as minhas palavras como o projeto funciona.

### Domínio escolhido

Escolhi um sistema de controle financeiro pessoal. Já tinha trabalhado com essa ideia (contas, categorias e lançamentos) em outra disciplina, e ela combina bem com este trabalho, porque permite criar uma regra de negócio clara: o dinheiro de uma conta não pode ficar negativo.

### Entidades (models)

São três tabelas, definidas em `financeiro/models.py`:

- **Categoria**: serve para organizar os gastos e ganhos, como Alimentação ou Lazer. Tem só o campo `nome`, que é único.
- **Conta**: representa uma conta bancária, com `nome`, `banco` e `criada_em`. O **saldo não é guardado no banco**: ele é calculado na hora, somando as entradas e subtraindo as saídas dos lançamentos. Fiz assim para o saldo nunca ficar diferente dos lançamentos.
- **Lancamento**: é cada movimentação. Tem `tipo` (entrada ou saída), `descricao`, `valor` e `data`, e está ligado a uma Conta e, opcionalmente, a uma Categoria. Se a conta for excluída, os lançamentos dela também são. Se a categoria for excluída, o lançamento continua existindo, só fica sem categoria.

### Como a API funciona

Usei o Django REST Framework. Cada recurso (`categorias`, `contas` e `lancamentos`) tem uma classe em `financeiro/views.py` que oferece todas as operações, e o arquivo `config/urls.py` cria as rotas automaticamente com um router. O arquivo `financeiro/serializers.py` converte os dados entre o banco e o JSON e também faz as validações.

### Operações principais (CRUD)

Cada recurso tem:

- `GET /api/{recurso}/` lista os registros (200);
- `GET /api/{recurso}/{id}/` mostra um registro (200, ou 404 se não existir);
- `POST` cria um registro (201, ou 400 se os dados forem inválidos);
- `PUT` atualiza o registro por completo (200);
- `PATCH` atualiza só alguns campos (200);
- `DELETE` exclui (204).

As respostas são em JSON. A tabela com todos os endpoints e exemplos está mais acima neste README.

### Persistência

Os dados ficam em um banco SQLite (`db.sqlite3`), acessado pelo ORM do Django. Os models geram as migrations (`financeiro/migrations/0001_initial.py`), e o comando `python manage.py migrate` cria as tabelas. Os dados continuam lá depois de desligar e ligar o servidor. O arquivo do banco não vai para o GitHub, por isso o README explica como criar o banco do zero.

### Validação

O serializer valida o que chega na API:

- o `valor` precisa ser maior que zero;
- a `descricao` precisa ter pelo menos 3 caracteres;
- o `tipo` só pode ser `entrada` ou `saida`;
- campos obrigatórios não podem faltar, e a conta e a categoria precisam existir.

Quando algo está errado, a API devolve **400** com uma mensagem em JSON dizendo qual campo tem problema.

### Regra de negócio

Uma **saída não pode deixar a conta com saldo negativo**. Essa regra está no método `validate` do `LancamentoSerializer`: antes de salvar, ele calcula quanto ficaria o saldo depois do lançamento e, se ficar abaixo de zero, recusa com a mensagem "Saldo insuficiente" e mostra o saldo disponível.

Ela vale em outras situações também: ao **editar** um lançamento (o efeito antigo é desconsiderado antes de calcular o novo), ao **mover** uma entrada para outra conta, e ao **excluir uma entrada** quando isso deixaria o saldo negativo (essa checagem está no `perform_destroy` da view). Dá para ver a regra funcionando tentando criar uma saída com valor muito maior que o saldo: a API responde 400.

### Filtro, busca, ordenação e paginação

- **Paginação**: as listas vêm de 5 em 5, com `count`, `next`, `previous` e `results`. Para trocar de página, usa-se `?page=2`.
- **Busca textual**: `?search=mercado` procura na descrição dos lançamentos (nas contas, procura no nome e no banco).
- **Ordenação**: `?ordering=-valor` ordena pelo valor, do maior para o menor. O `-` inverte a ordem.
- **Filtros** nos lançamentos: `tipo`, `conta`, `categoria`, `data_inicio`, `data_fim`, `valor_min` e `valor_max`. Eles podem ser combinados, e valores inválidos (por exemplo, uma data fora do formato) devolvem 400 com explicação.

### Recursos opcionais que implementei

- **Três ou mais models**: Categoria, Conta e Lançamento, todos usados pela API.
- **Autenticação**: o login é feito em `POST /api/login/`, que devolve um token. Consultar (GET) é público, mas criar, alterar e excluir exigem o cabeçalho `Authorization: Token ...`. Sem o token, a API responde 401. As credenciais de teste estão na seção acima.

Não fiz o frontend nem a publicação na internet, por falta de tempo.

### Como testei

Segui as instruções deste README do zero em uma pasta separada (clonando o repositório, instalando as dependências, rodando as migrations e subindo o servidor) para ter certeza de que qualquer pessoa consegue executar o projeto.

Muito obrigada pela atenção! Fico à disposição para esclarecer qualquer ponto do projeto.

Sabrina Wosniak
