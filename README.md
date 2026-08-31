# Desafio FullStack - Norven

Projeto desenvolvido como parte do desafio FullStack da **Norven**.

Nesta primeira etapa, o foco está na construção do **backend e banco de dados**. O frontend será desenvolvido posteriormente.

O ambiente da aplicação é executado utilizando **Docker**, com containers separados para:

* API FastAPI;
* PostgreSQL.

---

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

### Containerização

* Docker
* Docker Compose

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
│   │       └── endpoints/
│   │
│   ├── controllers/
│   │
│   ├── core/
│   │   ├── auth.py
│   │   ├── configs.py.example
│   │   ├── database.py
│   │   ├── deps.py
│   │   ├── enums.py
│   │   └── security.py
│   │
│   ├── desafio_fullstack_norven/
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── models/
│   │   └── __all_models.py
│   │
│   ├── repositories/
│   ├── schemas/
│   └── services/
│
├── alembic.ini
├── docker-compose.yml.example
├── Dockerfile
├── Makefile
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# Como executar o projeto

## 1. Pré-requisitos

Para executar o projeto utilizando Docker, certifique-se de possuir:

* Docker
* Docker Compose

Para verificar:

```bash
docker --version
docker compose version
```

Python e `uv` são utilizados internamente pelo container do backend, portanto não são obrigatórios na máquina host para a execução normal da aplicação.

Caso deseje executar comandos Python diretamente fora do Docker durante o desenvolvimento, também será necessário possuir:

* Python
* uv

---

## 2. Configurar os arquivos da aplicação

Antes de subir os containers, crie os arquivos de configuração a partir dos exemplos fornecidos.

### 2.1 Docker Compose

Copie:

```bash
cp docker-compose.yml.example docker-compose.yml
```

No Windows PowerShell, caso o comando `cp` não esteja disponível:

```powershell
Copy-Item docker-compose.yml.example docker-compose.yml
```

Edite o `docker-compose.yml` e configure os dados do PostgreSQL:

```text
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

Também confira o `healthcheck` do PostgreSQL para garantir que o usuário e banco informados correspondam às configurações acima.

> **Importante:** o arquivo `docker-compose.yml` deve permanecer fora do versionamento caso contenha credenciais reais.

---

### 2.2 Configurações da aplicação

Copie:

```bash
cp src/core/configs.py.example src/core/configs.py
```

No PowerShell:

```powershell
Copy-Item src/core/configs.py.example src/core/configs.py
```

Edite:

```text
src/core/configs.py
```

e configure principalmente:

* `DB_URL`
* `JWT_SECRET`

Para gerar um segredo JWT seguro:

```python
import secrets

print(secrets.token_urlsafe(32))
```

> **Importante:** o arquivo `src/core/configs.py` deve permanecer fora do versionamento caso contenha credenciais reais.

---

## 3. Configuração da conexão entre os containers

O PostgreSQL e o backend são executados em containers diferentes.

O Docker Compose cria automaticamente uma rede interna para comunicação entre os serviços.

Por isso, dentro do container do backend, a URL do banco **não deve utilizar `localhost`**.

Exemplo:

```text
postgresql+asyncpg://postgres:senha@postgres:5432/norven
```

Onde:

```text
postgresql+asyncpg://
        │
        ├── postgres → usuário
        ├── senha    → senha
        ├── postgres → nome do serviço PostgreSQL no Docker Compose
        ├── 5432     → porta
        └── norven   → banco
```

O host:

```text
postgres
```

corresponde ao serviço definido no `docker-compose.yml`:

```yaml
services:
  postgres:
```

Dentro do container do backend:

```text
localhost
```

representaria o próprio container da API, e não o PostgreSQL.

---

# 4. Criar e iniciar os containers

Na raiz da pasta `backend`, execute:

```bash
docker compose up -d --build
```

O comando:

* cria a imagem do backend;
* inicia o container da API;
* inicia o PostgreSQL;
* cria a rede entre os serviços;
* cria o volume persistente do banco.

Para verificar:

```bash
docker compose ps
```

O resultado deve apresentar os dois serviços em execução, por exemplo:

```text
backend     running
postgres    running
```

---

## Visualizar logs da API

```bash
docker compose logs -f backend
```

## Visualizar logs do PostgreSQL

```bash
docker compose logs -f postgres
```

---

## Parar os containers

```bash
docker compose down
```

Os dados do PostgreSQL permanecem armazenados no volume.

---

## Parar e remover os dados persistidos

```bash
docker compose down -v
```

> **Atenção:** o parâmetro `-v` remove também o volume do PostgreSQL. Todos os dados armazenados no banco serão apagados.

Após remover o volume, será necessário executar novamente as migrations e os seeders.

---

# 5. Executar as migrations

**Esta etapa é obrigatória na primeira execução do projeto.**

Com os containers em funcionamento:

```bash
docker compose exec backend uv run alembic upgrade head
```

As migrations são responsáveis pela criação e alteração da estrutura do banco de dados.

Atualmente, as principais tabelas criadas são:

```text
pais
estado
cidade

enderecos
contatos
funcionarios
fornecedores

categorias
unidades_medidas
informacoes_nutricionais
produtos

lotes
entradas
estoques
saidas
```

Além delas, o Alembic cria:

```text
alembic_version
```

Essa tabela registra qual versão das migrations está aplicada ao banco.

---

## Verificar migration atual

```bash
docker compose exec backend uv run alembic current
```

---

## Ver histórico de migrations

```bash
docker compose exec backend uv run alembic history
```

---

# 6. Executar os seeders

**Esta etapa também é obrigatória na primeira execução.**

Após as migrations:

```bash
docker compose exec backend uv run python -m seeders.database_seeder
```

Atualmente, o `DatabaseSeeder` executa o seeder responsável pelos dados geográficos.

A ordem é:

```text
pais
 ↓
estado
 ↓
cidade
```

A ordem é necessária devido às relações de chave estrangeira.

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
* pode atualizar registros já existentes;
* pode ser executado novamente;
* ajusta as sequences do PostgreSQL após a importação.

---

# 7. Acessar a API

Após:

```bash
docker compose up -d --build
```

e a execução das migrations e seeders, a API estará disponível em:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Não é necessário executar o Uvicorn manualmente na máquina host, pois a API é iniciada dentro do container `backend`.

---

# Resumo para primeira execução

Para executar o projeto do zero:

```bash
# 1. Criar arquivos de configuração
cp docker-compose.yml.example docker-compose.yml
cp src/core/configs.py.example src/core/configs.py

# 2. Ajustar as credenciais nos arquivos copiados

# 3. Criar e iniciar os containers
docker compose up -d --build

# 4. Executar as migrations - OBRIGATÓRIO
docker compose exec backend uv run alembic upgrade head

# 5. Executar os seeders - OBRIGATÓRIO
docker compose exec backend uv run python -m seeders.database_seeder
```

Depois:

```text
http://localhost:8000/docs
```

O fluxo completo é:

```text
Configuração
     ↓
Docker Compose
     ↓
┌─────────────────────┐
│                     │
↓                     ↓
Backend              PostgreSQL
FastAPI              Banco
│                     ↑
└──── rede Docker ────┘
     ↓
Migrations
     ↓
Seeders
     ↓
API disponível
```

---

# Desenvolvimento

O projeto utiliza um volume para compartilhar os arquivos do backend com o container durante o desenvolvimento.

Dessa forma, alterações feitas no código local podem ser detectadas pelo Uvicorn utilizando:

```text
--reload
```

Não é necessário reconstruir a imagem após cada alteração em arquivos Python.

Uma reconstrução pode ser necessária quando houver mudanças em itens como:

* `pyproject.toml`;
* `uv.lock`;
* `Dockerfile`;
* dependências do sistema.

Nesse caso:

```bash
docker compose up -d --build
```

---

# Migrations durante o desenvolvimento

Após criar ou alterar models do SQLAlchemy:

```bash
docker compose exec backend uv run alembic revision --autogenerate -m "descricao da migration"
```

O Alembic compara:

```text
Models SQLAlchemy
       ↓
DBBaseModel.metadata
       ↓
estrutura atual do PostgreSQL
       ↓
nova migration
```

Todos os models são centralizados em:

```text
src/models/__all_models.py
```

O `env.py` do Alembic importa esse módulo para garantir que todos os models sejam registrados no metadata do SQLAlchemy.

Após gerar uma migration, revise manualmente o arquivo criado em:

```text
migrations/versions/
```

O `--autogenerate` cria uma proposta de migration e pode identificar alterações que não devem ser aplicadas.

Depois de revisar:

```bash
docker compose exec backend uv run alembic upgrade head
```

---

# Banco de dados

O projeto utiliza SQLAlchemy de forma assíncrona através de:

```text
PostgreSQL
    +
asyncpg
```

A configuração da conexão está em:

```text
src/core/database.py
```

As configurações gerais estão em:

```text
src/core/configs.py
```

---

# Arquitetura do backend

O backend utiliza separação por responsabilidades:

```text
HTTP Request
     ↓
Endpoint
     ↓
Controller
     ↓
Service
     ↓
Repository
     ↓
SQLAlchemy Model
     ↓
PostgreSQL
```

### Endpoints

Responsáveis pela camada HTTP:

* rotas;
* parâmetros;
* dependências do FastAPI;
* schemas de entrada e saída;
* status HTTP.

### Controllers

Coordenam a chamada da funcionalidade solicitada pelo endpoint.

### Services

Responsáveis pelas regras de negócio da aplicação.

### Repositories

Responsáveis pelo acesso e persistência dos dados.

### Models

Representam as tabelas e relações do PostgreSQL através do SQLAlchemy.

### Schemas

Representam os dados de entrada e saída da API utilizando Pydantic.

---

# Autenticação

A estrutura inicial de autenticação utiliza:

* OAuth2 Bearer Token;
* JWT;
* bcrypt para hash de senhas;
* dependências do FastAPI;
* recuperação do usuário autenticado pelo token.

Os principais arquivos estão em:

```text
src/core/auth.py
src/core/deps.py
src/core/security.py
```

O fluxo esperado é:

```text
Login
 ↓
e-mail + senha
 ↓
validação da senha com bcrypt
 ↓
JWT
 ↓
Bearer Token
 ↓
endpoints autenticados
```

---

# Seeders e Factories

Os **seeders** são utilizados para inserir dados reais ou necessários para o funcionamento inicial da aplicação.

Atualmente:

```text
DatabaseSeeder
└── GeographySeeder
    ├── países
    ├── estados
    └── cidades
```

Factories poderão ser adicionadas posteriormente para geração de dados fictícios destinados principalmente a:

* desenvolvimento;
* testes automatizados.

---

# Status

🚧 Projeto em desenvolvimento.

## Infraestrutura

* [x] Configuração inicial do backend
* [x] PostgreSQL com Docker
* [x] Container próprio para o backend
* [x] Docker Compose para backend + PostgreSQL
* [x] SQLAlchemy assíncrono
* [x] Alembic
* [x] Seeders

## Dados geográficos

* [x] Model de país
* [x] Model de estado
* [x] Model de cidade
* [x] Migration de país, estado e cidade
* [x] Seeder de países
* [x] Seeder de estados
* [x] Seeder de cidades

## Models

* [x] Endereços
* [x] Usuários / Funcionários
* [x] Fornecedores
* [x] Contatos
* [x] Categorias
* [x] Unidades de medida
* [x] Produtos
* [x] Informações nutricionais
* [x] Lotes
* [x] Entradas
* [x] Estoques
* [x] Saídas

## Schemas

* [x] Endereços
* [x] Usuários / Funcionários
* [x] Fornecedores
* [x] Contatos
* [x] Categorias
* [x] Unidades de medida
* [x] Produtos
* [x] Informações nutricionais
* [x] Lotes
* [x] Entradas
* [x] Estoques
* [x] Saídas

## Migrations

* [x] Endereços
* [x] Usuários / Funcionários
* [x] Fornecedores
* [x] Contatos
* [x] Categorias
* [x] Unidades de medida
* [x] Produtos
* [x] Informações nutricionais
* [x] Lotes
* [x] Entradas
* [x] Estoques
* [x] Saídas

> Sempre revisar o modelo lógico e o arquivo gerado pelo Alembic antes de executar uma nova migration.

## Endpoints

* [x] Endereços
* [x] Usuários / Funcionários
* [x] Contatos
* [x] Categorias
* [x] Unidades de medida
* [x] Produtos
* [x] Informações nutricionais
* [x] Fornecedores
* [x] Lotes
* [x] Entradas
* [x] Estoques
* [x] Saídas

## Controllers

* [x] Endereços
* [x] Usuários / Funcionários
* [x] Contatos
* [x] Categorias
* [x] Unidades de medida
* [x] Produtos
* [x] Informações nutricionais
* [x] Fornecedores
* [x] Lotes
* [x] Entradas
* [x] Estoques
* [x] Saídas

## Services

* [x] Endereços
* [x] Usuários / Funcionários
* [x] Contatos
* [x] Categorias
* [x] Unidades de medida
* [x] Produtos
* [x] Informações nutricionais
* [x] Fornecedores
* [x] Lotes
* [x] Entradas
* [x] Estoques
* [x] Saídas

## Repositories

* [x] Endereços
* [x] Usuários / Funcionários
* [x] Contatos
* [x] Categorias
* [x] Unidades de medida
* [x] Produtos
* [x] Informações nutricionais
* [x] Fornecedores
* [x] Lotes
* [x] Entradas
* [x] Estoques
* [x] Saídas

## Qualidade

* [ ] Testes automatizados
* [ ] Tratamento global de exceções

## Frontend

* [ ] Vue.js
* [ ] TypeScript
* [ ] Integração com a API

---

A documentação será atualizada conforme novas funcionalidades forem adicionadas.
