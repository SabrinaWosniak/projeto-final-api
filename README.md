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
