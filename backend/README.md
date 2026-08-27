# Desafio FullStack - Norven

Projeto desenvolvido como parte do desafio FullStack da **Norven**.

Nesta primeira etapa, o foco está na construção do **backend e banco de dados**. O frontend será desenvolvido posteriormente.

## Tecnologias

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Alembic
* asyncpg
* bcrypt
* JWT

### Banco de Dados

* PostgreSQL
* Docker

### Gerenciamento de dependências

* uv

### Frontend

Será desenvolvido posteriormente utilizando:

* Vue.js
* TypeScript

---

## Estrutura do projeto

A estrutura atual do backend segue uma separação de responsabilidades inspirada em boas práticas utilizadas também em projetos Laravel.

```text
backend/
├── migrations/
│   └── versions/
│
├── seeders/
│   ├── data/
│   │   ├── pais.sql
│   │   ├── estado.sql
│   │   └── cidade.sql
│   ├── database_seeder.py
│   └── geography_seeder.py
│
├── src/
│   ├── api/
│   │   └── v1/
│   ├── controllers/
│   ├── core/
│   │   ├── auth.py
│   │   ├── configs.py.example
│   │   ├── database.py
│   │   ├── deps.py
│   │   └── security.py
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
│
├── alembic.ini
├── docker-compose.yml.example
├── Makefile
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# Como executar o projeto

## 1. Pré-requisitos

Antes de iniciar, certifique-se de possuir instalado:

* Python
* Docker
* Docker Compose
* uv

Para verificar:

```bash
python --version
docker --version
docker compose version
uv --version
```

---

## 2. Instalar as dependências

Na pasta `backend`, execute:

```bash
uv sync
```

O `uv` irá criar/utilizar o ambiente virtual do projeto e instalar as dependências definidas no `pyproject.toml` e `uv.lock`.

---

## 3. Configurar arquivos de configuração

Para configurar o banco de dados e as credenciais da aplicação, siga estes passos:

### 3.1 Configurar Docker Compose

Copie o arquivo de exemplo e ajuste as credenciais:

```bash
cp docker-compose.yml.example docker-compose.yml
```

Edite o `docker-compose.yml` e altere os seguintes campos:

- `POSTGRES_USER`: nome de usuário do PostgreSQL
- `POSTGRES_PASSWORD`: senha do PostgreSQL
- `POSTGRES_DB`: nome do banco de dados
- No `healthcheck`, atualize o usuário e banco de dados conforme configurado acima

> **Importante:** O arquivo `docker-compose.yml` está incluído no `.gitignore` para evitar que credenciais sejam versionadas no repositório.

### 3.2 Configurar aplicações

Copie o arquivo de exemplo e ajuste as configurações:

```bash
cp src/core/configs.py.example src/core/configs.py
```

Edite o `src/core/configs.py` e altere os seguintes campos:

- `DB_URL`: string de conexão com o PostgreSQL (deve coincidir com as credenciais do docker-compose.yml)
- `JWT_SECRET`: segredo para assinatura dos tokens JWT (gere um valor seguro usando `secrets.token_urlsafe(32)`)

> **Importante:** O arquivo `src/core/configs.py` está incluído no `.gitignore` para evitar que credenciais sejam versionadas no repositório.

---

## 4. Criar e iniciar o PostgreSQL

Na raiz do backend, execute:

```bash
docker compose up -d
```

O Docker irá criar e iniciar o container do PostgreSQL.

Para verificar se o banco está em execução:

```bash
docker compose ps
```

O container do PostgreSQL deve aparecer como ativo.

### Parar os containers

```bash
docker compose down
```

### Parar e remover também os dados persistidos

```bash
docker compose down -v
```

> O comando com `-v` remove o volume do PostgreSQL e, consequentemente, os dados armazenados nele.

---

## 5. Executar as migrations

Com o PostgreSQL em execução, aplique todas as migrations:

```bash
uv run alembic upgrade head
```

As migrations são responsáveis pela criação e alteração da estrutura do banco de dados.

Atualmente, entre as tabelas iniciais estão:

```text
pais
estado
cidade
```

Além delas, o Alembic cria a tabela:

```text
alembic_version
```

utilizada para controlar quais migrations já foram executadas.

### Verificar migration atual

```bash
uv run alembic current
```

### Ver histórico de migrations

```bash
uv run alembic history
```

---

## 6. Executar os seeders

**Esta etapa é obrigatória.**

As tabelas de localização utilizam dados reais e precisam ser populadas após a execução das migrations.

Execute:

```bash
uv run python -m seeders.database_seeder
```

O `DatabaseSeeder` atualmente executa o seeder de geografia na seguinte ordem:

```text
pais
 ↓
estado
 ↓
cidade
```

Essa ordem é necessária devido aos relacionamentos entre as tabelas.

Os dados utilizados estão em:

```text
seeders/data/
├── pais.sql
├── estado.sql
└── cidade.sql
```

O seeder:

* popula países;
* popula estados;
* popula cidades;
* respeita as chaves estrangeiras;
* atualiza os registros caso o seeder seja executado novamente;
* ajusta as sequences do PostgreSQL após a importação.

Portanto, o seeder pode ser executado novamente sem a necessidade de recriar o banco.

---

## 7. Executar a API

Com banco, migrations e seeders configurados, inicie o FastAPI.

Caso o objeto `app = FastAPI()` esteja em `src/main.py`:

```bash
uv run uvicorn src.main:app --reload
```

Caso o `main.py` esteja dentro de outro módulo, ajuste o caminho no comando conforme a estrutura do projeto.

Quando a aplicação estiver executando, por padrão o FastAPI estará disponível em:

```text
http://127.0.0.1:8000
```

Documentação Swagger:

```text
http://127.0.0.1:8000/docs
```

Documentação ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Resumo para primeira execução

Para configurar o projeto do zero:

```bash
# Instalar dependências
uv sync

# Configurar arquivos de configuração
cp docker-compose.yml.example docker-compose.yml
cp src/core/configs.py.example src/core/configs.py

# Editar os arquivos copiados com suas credenciais
# - docker-compose.yml
# - src/core/configs.py

# Criar/iniciar PostgreSQL
docker compose up -d

# Criar as tabelas
uv run alembic upgrade head

# Popular os dados iniciais - OBRIGATÓRIO
uv run python -m seeders.database_seeder

# Iniciar a API
uv run uvicorn src.main:app --reload
```

O fluxo é:

```text
Configuração de arquivos
  ↓
Docker
  ↓
PostgreSQL
  ↓
Alembic migrations
  ↓
Seeders
  ↓
FastAPI
```

---

# Migrations durante o desenvolvimento

Após criar ou alterar models SQLAlchemy, uma nova migration pode ser gerada utilizando:

```bash
uv run alembic revision --autogenerate -m "descricao da migration"
```

Revise o arquivo criado dentro de:

```text
migrations/versions/
```

e depois aplique:

```bash
uv run alembic upgrade head
```

---

# Banco de dados

O projeto utiliza SQLAlchemy de forma assíncrona através de:

```text
postgresql + asyncpg
```

A configuração central da conexão está em:

```text
src/core/database.py
```

As configurações da aplicação estão em:

```text
src/core/configs.py
```

---

# Autenticação

A estrutura inicial de autenticação utiliza:

* OAuth2 Bearer Token;
* JWT;
* bcrypt para hash de senhas;
* dependências do FastAPI para recuperação do usuário autenticado.

Os principais arquivos estão em:

```text
src/core/auth.py
src/core/deps.py
src/core/security.py
```

---

# Seeders e Factories

Os **seeders** são utilizados para dados reais ou necessários para o funcionamento inicial da aplicação.

Atualmente:

```text
DatabaseSeeder
└── GeographySeeder
    ├── países
    ├── estados
    └── cidades
```

Factories poderão ser adicionadas futuramente para geração de dados fictícios destinados principalmente a desenvolvimento e testes.

---

# Status

🚧 Projeto em desenvolvimento.

Atualmente:

* [x] Configuração inicial do backend
* [x] PostgreSQL com Docker
* [x] SQLAlchemy assíncrono
* [x] Alembic
* [x] Models iniciais de localização
* [x] Migrations iniciais
* [x] Seeder de países
* [x] Seeder de estados
* [x] Seeder de cidades
* [ ] Migrations de:
  * [ ] Endereços
  * [ ] Usuários (funcionários)
  * [ ] Fornecedores
  * [ ] Contatos
  * [ ] Categorias
  * [ ] Unidade de medida
  * [ ] Produtos
  * [ ] Informação Nutricional
  * [ ] Lotes
  * [ ] Entradas
  * [ ] Estoques
  * [ ] Saídas
  * Obs.: Sempre conferir o modelo lógico antes de criar as migrations.
* [ ] Models de:
  * [ ] Endereços
  * [ ] Usuários (funcionários)
  * [ ] Fornecedores
  * [ ] Contatos
  * [ ] Categorias
  * [ ] Unidade de medida
  * [ ] Produtos
  * [ ] Informação Nutricional
  * [ ] Lotes
  * [ ] Entradas
  * [ ] Estoques
  * [ ] Saídas
* [ ] Schemas de:
  * [ ] Endereços
  * [ ] Usuários (funcionários)
  * [ ] Fornecedores
  * [ ] Contatos
  * [ ] Categorias
  * [ ] Unidade de medida
  * [ ] Produtos
  * [ ] Informação Nutricional
  * [ ] Lotes
  * [ ] Entradas
  * [ ] Estoques
  * [ ] Saídas
* [ ] Endpoints da API
* [ ] Controllers, Services e Repositories de:
  * [ ] Endereços
  * [ ] Usuários (funcionários)
  * [ ] Fornecedores
  * [ ] Contatos
  * [ ] Categorias
  * [ ] Unidade de medida
  * [ ] Produtos
  * [ ] Informação Nutricional
  * [ ] Lotes
  * [ ] Entradas
  * [ ] Estoques
  * [ ] Saídas
* [ ] Testes
* [ ] Frontend Vue.js + TypeScript

A documentação será atualizada conforme novas funcionalidades forem adicionadas.
