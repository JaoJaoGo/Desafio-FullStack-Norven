# Desafio FullStack - Norven

Projeto desenvolvido como parte do desafio FullStack da **Norven** para gerenciamento de produtos, estoque e movimentações.

Nesta etapa, o backend e o banco de dados estão implementados e sendo validados por testes de integração. O frontend será desenvolvido posteriormente.

## Tecnologias

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic
- asyncpg
- bcrypt
- JWT
- OAuth2 Bearer Token

### Banco de dados

- PostgreSQL

### Testes

- pytest
- pytest-asyncio
- HTTPX

### Containerização

- Docker
- Docker Compose

### Gerenciamento de dependências

- uv

### Frontend

Planejado conforme o desafio:

- Vue.js com Options API
- TypeScript
- Pinia
- Vuetify

---

## Arquitetura

O backend utiliza separação de responsabilidades por camadas:

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

- definição das rotas;
- parâmetros de path e query;
- dependências do FastAPI;
- autenticação;
- schemas de entrada e saída;
- códigos de status HTTP.

### Controllers

Coordenam a chamada da funcionalidade solicitada pelo endpoint e encaminham a execução para a camada de serviço.

### Services

Concentram as regras de negócio, validações entre entidades e controle das transações que precisam ser executadas de forma atômica.

### Repositories

Responsáveis pelas consultas e operações de persistência utilizando SQLAlchemy.

### Models

Representam as tabelas, constraints e relacionamentos do PostgreSQL.

### Schemas

Funcionam como DTOs da API por meio do Pydantic, validando dados de entrada, atualização, filtros e respostas.

---

## Estrutura principal

```text
backend/
├── migrations/
│   └── versions/
├── seeders/
│   ├── data/
│   │   ├── pais.sql
│   │   ├── estado.sql
│   │   └── cidade.sql
│   ├── database_seeder.py
│   └── geography_seeder.py
├── src/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── controllers/
│   ├── core/
│   │   ├── auth.py
│   │   ├── configs.py.example
│   │   ├── database.py
│   │   ├── deps.py
│   │   ├── enums.py
│   │   └── security.py
│   ├── models/
│   │   └── __all_models.py
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── integration/
│       └── api/
│           ├── helpers_movimentacoes.py
│           ├── payloads.py
│           ├── test_auth.py
│           ├── test_categorias.py
│           ├── test_contatos.py
│           ├── test_enderecos.py
│           ├── test_estoque.py
│           ├── test_entradas.py
│           ├── test_fornecedores.py
│           ├── test_informacoes_nutricionais.py
│           ├── test_lotes.py
│           ├── test_produtos.py
│           ├── test_saida.py
│           ├── test_unidades_medidas.py
│           └── test_usuarios.py
├── alembic.ini
├── docker-compose.yml.example
├── docker-compose.test.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── pytest.ini
├── uv.lock
└── README.md
```

> A árvore acima apresenta a estrutura principal do projeto. Arquivos auxiliares e `__init__.py` foram omitidos para facilitar a leitura.

---

# Como executar o projeto

## 1. Pré-requisitos

Para executar o projeto utilizando Docker:

- Docker
- Docker Compose

Verifique a instalação:

```bash
docker --version
docker compose version
```

Python e `uv` são utilizados dentro do container do backend e não são obrigatórios na máquina host para a execução normal da aplicação.

Para executar comandos Python diretamente no host durante o desenvolvimento, também será necessário possuir Python e `uv`.

---

## 2. Configurar os arquivos da aplicação

### 2.1 Docker Compose

Crie o arquivo de configuração a partir do exemplo:

```bash
cp docker-compose.yml.example docker-compose.yml
```

No PowerShell:

```powershell
Copy-Item docker-compose.yml.example docker-compose.yml
```

Configure no `docker-compose.yml` os dados do PostgreSQL, incluindo:

```text
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

Também confira o `healthcheck` do serviço PostgreSQL.

> **Importante:** não versione credenciais reais.

### 2.2 Configurações do backend

Crie o arquivo de configuração:

```bash
cp src/core/configs.py.example src/core/configs.py
```

No PowerShell:

```powershell
Copy-Item src/core/configs.py.example src/core/configs.py
```

Configure os valores necessários, principalmente a URL de conexão com o banco e o segredo JWT.

Exemplo de geração de segredo:

```python
import secrets

print(secrets.token_urlsafe(32))
```

> **Importante:** `src/core/configs.py` não deve conter segredos versionados.

---

## 3. Comunicação entre os containers

O PostgreSQL e o backend executam em containers diferentes e se comunicam pela rede criada pelo Docker Compose.

Por isso, dentro do container da API, a conexão com o PostgreSQL não deve utilizar `localhost`.

Exemplo:

```text
postgresql+asyncpg://postgres:senha@postgres:5432/norven
```

Nesse exemplo, o segundo `postgres` representa o nome do serviço do banco no Docker Compose:

```yaml
services:
  postgres:
```

Dentro do container do backend, `localhost` apontaria para o próprio container da API.

---

## 4. Criar e iniciar os containers

Na raiz de `backend/`:

```bash
docker compose up -d --build
```

O comando:

- cria a imagem do backend;
- inicia a API;
- inicia o PostgreSQL;
- cria a rede entre os serviços;
- configura o volume persistente do banco.

Verifique os serviços:

```bash
docker compose ps
```

### Logs do backend

```bash
docker compose logs -f backend
```

### Logs do PostgreSQL

```bash
docker compose logs -f postgres
```

### Parar os containers

```bash
docker compose down
```

Os dados permanecem no volume do PostgreSQL.

### Remover containers e dados persistidos

```bash
docker compose down -v
```

> **Atenção:** `-v` remove o volume do PostgreSQL. Depois disso, migrations e seeders deverão ser executados novamente.

---

## 5. Executar migrations

Esta etapa é obrigatória na primeira execução:

```bash
docker compose exec backend uv run alembic upgrade head
```

As principais tabelas da aplicação são:

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

O Alembic também mantém a tabela:

```text
alembic_version
```

### Verificar migration atual

```bash
docker compose exec backend uv run alembic current
```

### Ver histórico de migrations

```bash
docker compose exec backend uv run alembic history
```

---

## 6. Executar seeders

Após as migrations:

```bash
docker compose exec backend uv run python -m seeders.database_seeder
```

Os dados geográficos seguem a ordem:

```text
pais
 ↓
estado
 ↓
cidade
```

Os arquivos utilizados estão em:

```text
seeders/data/
├── pais.sql
├── estado.sql
└── cidade.sql
```

O processo de seed:

- popula os dados geográficos;
- respeita as dependências de chave estrangeira;
- pode atualizar registros já existentes;
- pode ser executado novamente;
- ajusta as sequences do PostgreSQL;
- prepara os dados iniciais necessários pela aplicação.

---

## 7. Acessar a API

Com os containers ativos e o banco preparado:

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

Não é necessário iniciar o Uvicorn manualmente no host quando o backend estiver sendo executado pelo Docker.

---

# Autenticação

A autenticação utiliza:

- OAuth2;
- Bearer Token;
- JWT;
- bcrypt para hash e validação de senha;
- recuperação do usuário autenticado por dependência do FastAPI.

Fluxo:

```text
e-mail + senha
     ↓
validação das credenciais
     ↓
JWT
     ↓
Bearer Token
     ↓
endpoint autenticado
```

O endpoint de login utiliza o fluxo OAuth2 Password e recebe o e-mail no campo `username`.

As rotas protegidas utilizam o usuário recuperado a partir do token para identificar o responsável pelas operações auditáveis.

---

# Regras de negócio principais

## Usuários

- cadastro com nome, e-mail, senha, contato e endereço;
- endereço vinculado a município;
- consulta de estado e município baseada nos dados geográficos;
- e-mail único;
- senha armazenada utilizando hash;
- autenticação via JWT.

## Fornecedores

- CNPJ único;
- cadastro e atualização com endereço e contato;
- reutilização de endereço ou contato quando os dados já existentes forem equivalentes.

## Produtos

- nome único;
- código identificador;
- preço de venda atual;
- categoria;
- unidade de medida;
- indicação de produto perecível;
- informação nutricional opcional;
- filtros e paginação;
- status calculado a partir de estoque e validade.

## Lotes

- vinculados a um produto;
- número único dentro do mesmo produto;
- produtos perecíveis exigem validade na criação do lote;
- produto e validade do lote não são alterados depois da criação;
- produtos não perecíveis podem possuir validade nula.

## Entradas

- vinculadas a produto, fornecedor, lote e usuário responsável;
- aceitam lote existente ou criação de novo lote durante a entrada;
- registram quantidade, custo, tipo, observação e data;
- criam o estoque correspondente automaticamente;
- alteração de quantidade atualiza o saldo do estoque;
- alterações que produziriam saldo inválido são bloqueadas;
- localização física do estoque pode ser informada e atualizada;
- transações não possuem exclusão.

## Estoques

- são originados por entradas;
- mantêm o saldo atual;
- possuem corredor, prateleira e seção;
- permitem filtros por produto, lote e saldo;
- utilizam bloqueio de linha (`FOR UPDATE`) nos fluxos em que o saldo será alterado;
- não são criados diretamente por endpoint público.

## Saídas

- vinculadas ao estoque, produto e usuário responsável;
- reduzem o saldo automaticamente;
- não permitem quantidade superior ao saldo disponível;
- não permitem data anterior à entrada correspondente;
- saídas do tipo `VENDA` podem utilizar preço informado ou o preço atual do produto;
- outros tipos de saída não possuem preço de venda;
- edição da quantidade recalcula o saldo do estoque;
- transações não possuem exclusão.

## Auditoria e histórico

Entradas e saídas registram:

- usuário responsável;
- data e hora;
- tipo de movimentação;
- quantidade;
- produto e lote relacionados.

O histórico de transações do produto reúne entradas e saídas e permite filtros para consulta e rastreabilidade.

---

# Paginação e filtros

As listagens principais utilizam paginação por `page` e `per_page`.

Exemplo:

```text
GET /api/v1/produtos?page=1&per_page=20
```

Os recursos implementam filtros próprios de acordo com o contexto, como:

- busca textual;
- produto;
- fornecedor;
- usuário;
- lote;
- tipo de movimentação;
- quantidade mínima e máxima;
- intervalo de preço;
- período de datas;
- status;
- saldo disponível.

---

# Testes automatizados

O projeto possui testes de integração da API utilizando banco PostgreSQL separado do ambiente de desenvolvimento.

A suíte cobre o fluxo HTTP completo:

```text
Request
   ↓
Endpoint
   ↓
Controller
   ↓
Service
   ↓
Repository
   ↓
PostgreSQL de teste
```

Os testes validam, entre outros cenários:

- autenticação e proteção de rotas;
- criação, consulta, edição, filtros e paginação;
- validações de unicidade;
- relacionamentos entre entidades;
- regras de perecibilidade e validade;
- criação automática de estoque;
- atualização de saldo por entrada e saída;
- bloqueio de estoque negativo;
- auditoria das movimentações;
- ausência de exclusão para entradas e saídas;
- histórico de transações.

## Ambiente de testes

O ambiente utiliza um PostgreSQL exclusivo para testes, evitando alterações no banco de desenvolvimento.

Para subir o ambiente:

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d --build
```

## Executar todos os testes de integração

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml exec backend uv run pytest tests/integration/api -v
```

## Executar um módulo específico

Entradas:

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml exec backend uv run pytest tests/integration/api/test_entradas.py -v
```

Estoques:

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml exec backend uv run pytest tests/integration/api/test_estoque.py -v
```

Saídas:

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml exec backend uv run pytest tests/integration/api/test_saida.py -v
```

Também é possível executar qualquer outro arquivo individual presente em `tests/integration/api/`.

> Antes de uma entrega ou commit de estabilização, recomenda-se executar a suíte completa de integração.

---

# Desenvolvimento

O backend utiliza volume do Docker para refletir alterações locais no container durante o desenvolvimento.

Com o Uvicorn em modo `--reload`, mudanças em arquivos Python podem ser detectadas sem reconstruir a imagem.

Uma nova build pode ser necessária quando houver mudanças em:

- `pyproject.toml`;
- `uv.lock`;
- `Dockerfile`;
- dependências do sistema.

Nesse caso:

```bash
docker compose up -d --build
```

---

# Migrations durante o desenvolvimento

Após criar ou alterar models SQLAlchemy:

```bash
docker compose exec backend uv run alembic revision --autogenerate -m "descricao da migration"
```

O Alembic compara os models registrados no metadata com a estrutura atual do PostgreSQL.

Todos os models utilizados pelas migrations devem estar registrados por meio de:

```text
src/models/__all_models.py
```

Após gerar uma migration, revise manualmente o arquivo em:

```text
migrations/versions/
```

Depois da revisão:

```bash
docker compose exec backend uv run alembic upgrade head
```

> O `--autogenerate` cria uma proposta de migration. O arquivo gerado deve ser revisado antes da aplicação.

---

# Banco de dados

O projeto utiliza SQLAlchemy assíncrono com PostgreSQL por meio do `asyncpg`.

A configuração da conexão está centralizada em:

```text
src/core/database.py
```

As configurações da aplicação ficam em:

```text
src/core/configs.py
```

---

# Convenções Git da Norven

O projeto segue o padrão de nomenclatura definido pela Norven.

## Branches

Branches variáveis seguem:

```text
<type>/[<id-task>/]<task-name>
```

Tipos permitidos para branches de trabalho:

```text
feat
fix
```

Exemplos:

```text
feat/implementacao-de-autenticacao
fix/correcao-de-fluxo-de-estoque
```

O nome da task deve utilizar `kebab-case`.

## Commits

Commits seguem:

```text
<type>: <description>
```

Tipos previstos:

```text
feat
fix
refactor
docs
test
build
review
```

Exemplos:

```text
feat: implementar autenticação de usuário
fix: corrigir atualização do saldo de estoque
test: adicionar testes de integração para movimentações
docs: atualizar instruções de execução do projeto
```

---

# Resumo para primeira execução

```bash
# 1. Criar os arquivos locais de configuração
cp docker-compose.yml.example docker-compose.yml
cp src/core/configs.py.example src/core/configs.py

# 2. Ajustar as configurações e credenciais

# 3. Subir os containers
docker compose up -d --build

# 4. Executar migrations
docker compose exec backend uv run alembic upgrade head

# 5. Executar seeders
docker compose exec backend uv run python -m seeders.database_seeder
```

Depois acesse:

```text
http://localhost:8000/docs
```

---

# Status

🚧 Projeto em desenvolvimento.

## Backend

- [x] Infraestrutura Docker
- [x] PostgreSQL
- [x] SQLAlchemy assíncrono
- [x] Alembic
- [x] Seeders
- [x] Autenticação JWT
- [x] Models
- [x] Schemas / DTOs
- [x] Repositories
- [x] Services
- [x] Controllers
- [x] Endpoints
- [x] Paginação e filtros
- [x] Entradas de estoque
- [x] Estoque atual
- [x] Saídas de estoque
- [x] Histórico de transações

## Testes de integração implementados

- [x] Autenticação
- [x] Categorias
- [x] Contatos
- [x] Endereços
- [x] Fornecedores
- [x] Informações nutricionais
- [x] Lotes
- [x] Produtos
- [x] Unidades de medida
- [x] Usuários / Funcionários
- [x] Entradas
- [x] Estoques
- [x] Saídas

## Qualidade

- [x] Banco de testes separado
- [x] Testes de integração HTTP
- [x] Transações para operações críticas de estoque
- [x] Bloqueio pessimista de estoque nos fluxos de movimentação
- [ ] Testes unitários
- [ ] Tratamento global de exceções

## Frontend

- [ ] Vue.js com Options API
- [ ] TypeScript
- [ ] Pinia
- [ ] Vuetify
- [ ] Integração com a API

---

A documentação será atualizada conforme novas funcionalidades forem adicionadas.
