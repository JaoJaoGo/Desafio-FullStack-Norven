# Desafio FullStack - Norven

Projeto desenvolvido como parte do desafio FullStack da **Norven** para gerenciamento de produtos, estoque e movimentações.

Nesta etapa, o backend, o banco de dados e o frontend estão implementados. O backend é validado por testes de integração, e o frontend está integrado com a API.

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

- Vue.js com Options API
- TypeScript
- Pinia
- Vuetify
- Vue Router
- Vite

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

### Frontend

```text
frontend/
├── src/
│   ├── plugins/
│   │   └── vuetify.ts
│   ├── router/
│   │   └── index.ts
│   ├── services/
│   │   ├── api.ts
│   │   └── authService.ts
│   ├── stores/
│   │   └── auth.ts
│   ├── types/
│   │   └── auth.ts
│   ├── views/
│   │   ├── InicioView.vue
│   │   └── LoginView.vue
│   ├── App.vue
│   └── main.ts
├── .env.example
├── ._gitignore
├── Dockerfile
├── eslint.config.mjs
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
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

A execução normal da aplicação é feita pelos containers. Portanto, **Python, `uv`, Node.js e npm não são obrigatórios no host apenas para subir o sistema com Docker**, desde que as imagens sejam construídas corretamente.

Entretanto, para desenvolvimento local e para que o editor/IDE reconheça as dependências do projeto, é recomendado instalar também:

- Python compatível com a versão definida no `pyproject.toml`;
- `uv`;
- Node.js;
- npm.

Isso é especialmente útil no VS Code/Pylance. Caso o editor mostre erros como:

```text
Import "sqlalchemy" could not be resolved
Import "fastapi" could not be resolved
```

mesmo com o backend funcionando no Docker, normalmente significa que o **ambiente Python local do editor ainda não possui as dependências instaladas**. As dependências do container e as dependências reconhecidas pelo editor no host são ambientes diferentes.

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

### 2.3 Configurações do frontend

Entre na pasta `frontend` e crie o arquivo de configuração:

```bash
cd frontend
cp .env.example .env
```

No PowerShell:

```powershell
Set-Location frontend
Copy-Item .env.example .env
```

Se você já estiver dentro de `frontend`, execute apenas o comando de cópia.

Configure a URL da API:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

> **Importante:** `.env` não deve conter segredos versionados.

---

## 3. Instalar / sincronizar dependências para desenvolvimento

> Esta etapa é necessária quando você deseja executar ferramentas no host ou fazer o editor reconhecer corretamente as dependências. Para apenas executar a aplicação pelos containers, o `docker compose up -d --build` já deve instalar as dependências dentro das imagens.

### 3.1 Backend

Entre na pasta `backend`:

```bash
cd backend
```

Sincronize as dependências Python definidas no `pyproject.toml` e no `uv.lock`:

```bash
uv sync
```

No Windows/PowerShell, o comando é o mesmo:

```powershell
uv sync
```

O `uv` criará/sincronizará o ambiente virtual local, normalmente em:

```text
backend/.venv
```

Se estiver utilizando VS Code com Pylance e os imports continuarem aparecendo como não encontrados, selecione o interpretador Python desse ambiente virtual.

No Windows, normalmente:

```text
backend\.venv\Scripts\python.exe
```

No Linux/macOS:

```text
backend/.venv/bin/python
```

> **Importante:** este `uv sync` no host é principalmente para desenvolvimento local, autocomplete, análise estática, lint e execução de comandos fora do Docker. O backend que roda pela aplicação utiliza as dependências instaladas dentro do container.

Também é possível executar comandos Python diretamente dentro do container sem instalar as dependências Python no host:

```bash
docker compose exec backend uv run python --version
```

Por exemplo:

```bash
docker compose exec backend uv run alembic upgrade head
docker compose exec backend uv run python -m seeders.database_seeder
docker compose exec backend uv run pytest
```

### 3.2 Frontend

Entre na pasta `frontend`:

```bash
cd frontend
```

Instale as dependências:

```bash
npm install
```

Isso cria/sincroniza a pasta:

```text
frontend/node_modules
```

Além de permitir a execução local dos comandos do frontend, isso ajuda o editor a resolver corretamente dependências do Vue, Vuetify, Pinia, TypeScript, ESLint e demais pacotes.

Exemplos:

```bash
npm run type-check
npm run lint
npm run build
```

Se o frontend estiver sendo executado somente pelo Docker, o container também instala/utiliza suas próprias dependências. O `npm install` no host é recomendado para desenvolvimento e ferramentas do editor.

### 3.3 Resumo: host x Docker

```text
Host
├── backend/.venv
│   └── criado/sincronizado por: uv sync
│       └── usado pelo editor e comandos Python locais
│
└── frontend/node_modules
    └── criado/sincronizado por: npm install
        └── usado pelo editor e comandos npm locais

Docker
├── container backend
│   └── possui seu próprio ambiente Python e dependências
│
├── container frontend
│   └── possui suas próprias dependências Node
│
└── container postgres
    └── banco PostgreSQL
```

Portanto, um erro de importação mostrado pelo editor no host **não significa necessariamente que a dependência está ausente dentro do container**.

---

## 4. Comunicação entre os containers

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

## 5. Criar e iniciar os containers

Execute os comandos do Docker Compose na pasta onde está o arquivo `docker-compose.yml` — neste projeto, a pasta `backend`:

```bash
cd backend
docker compose up -d --build
```

Se você já estiver dentro de `backend`, basta executar:

```bash
docker compose up -d --build
```

O comando:

- cria a imagem do backend;
- cria a imagem do frontend;
- inicia a API;
- inicia o frontend;
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

### Logs do frontend

```bash
docker compose logs -f frontend
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

## 6. Executar migrations

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

## 7. Executar seeders

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

## 8. Acessar a aplicação

Com os containers ativos e o banco preparado:

### Frontend

```text
http://localhost:5173
```

### API

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

Não é necessário iniciar o Uvicorn ou o Vite manualmente no host quando os serviços estiverem sendo executados pelo Docker.

---

# Frontend

## Arquitetura

O frontend utiliza Vue.js com Options API e segue uma estrutura modular:

```text
Vue Component
     ↓
Pinia Store
     ↓
Service
     ↓
API Request
     ↓
FastAPI Backend
```

### Componentes

Responsáveis pela camada de apresentação:

- definição da interface;
- eventos do usuário;
- estado local;
- integração com stores do Pinia.

### Stores (Pinia)

Gerenciam o estado global da aplicação:

- autenticação (token, usuário);
- cache de dados;
- ações assíncronas;
- persistência no localStorage.

### Services

Encapsulam chamadas à API:

- comunicação HTTP;
- tratamento de erros;
- serialização de dados;
- gerenciamento de tokens.

### Router (Vue Router)

Gerencia a navegação:

- definição de rotas;
- proteção de rotas (autenticação);
- redirecionamentos;
- parâmetros de rota.

## Integração com a API

O frontend se comunica com a API via HTTP utilizando:

- `fetch` nativo do navegador;
- Bearer Token no header `Authorization`;
- tratamento de erros centralizado;
- armazenamento do token no localStorage.

### Fluxo de Autenticação

```text
Login
     ↓
POST /api/v1/auth/login
     ↓
Recebe JWT
     ↓
Armazena no localStorage
     ↓
Envia em todas as requisições
```

### Proteção de Rotas

O Vue Router utiliza guards para proteger rotas:

- Rotas com `requiresAuth`: exigem autenticação
- Rotas com `guestOnly`: apenas para usuários não autenticados
- Redirecionamento automático para login quando necessário

## Desenvolvimento

O frontend utiliza volume do Docker para refletir alterações locais no container durante o desenvolvimento.

Ao clonar o projeto em uma nova máquina, recomenda-se instalar também as dependências no host:

```bash
cd frontend
npm install
```

Isso disponibiliza `node_modules` para o editor e para comandos como:

```bash
npm run type-check
npm run lint
npm run build
```

Com o Vite em modo `--reload`, mudanças em arquivos podem ser detectadas sem reconstruir a imagem.

Uma nova build pode ser necessária quando houver mudanças em:

- `package.json`;
- `package-lock.json`;
- `Dockerfile`;
- dependências do sistema.

Nesse caso:

```bash
docker compose up -d --build
```

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

## CORS

O backend está configurado para aceitar requisições do frontend via CORS:

- Origens permitidas: `http://localhost:5173`, `http://127.0.0.1:5173`
- Credenciais permitidas
- Todos os métodos e headers permitidos

Isso permite que o frontend, rodando em uma porta diferente, possa se comunicar com a API sem restrições de navegador.

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

Ao clonar o projeto em uma nova máquina e utilizar Python/editor no host, sincronize primeiro as dependências:

```bash
cd backend
uv sync
```

Depois, configure o editor para utilizar o interpretador presente em `backend/.venv`.

Se preferir trabalhar exclusivamente pelo Docker, não é necessário executar o FastAPI manualmente no host. Com os containers ativos, comandos Python podem ser executados por:

```bash
docker compose exec backend uv run <comando>
```

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

## Opção recomendada: aplicação executada com Docker

Partindo da raiz do repositório:

```bash
# 1. Backend
cd backend

# 2. Criar os arquivos locais de configuração
cp docker-compose.yml.example docker-compose.yml
cp src/core/configs.py.example src/core/configs.py

# 3. Subir backend, frontend e PostgreSQL
docker compose up -d --build

# 4. Executar migrations
docker compose exec backend uv run alembic upgrade head

# 5. Executar seeders
docker compose exec backend uv run python -m seeders.database_seeder
```

Em outro terminal, configure o frontend:

```bash
cd frontend
cp .env.example .env
npm install
```

O `npm install` no host é recomendado para o editor e ferramentas locais. O frontend continuará sendo executado pelo container caso o serviço `frontend` esteja ativo no Docker Compose.

Para que o editor também reconheça imports Python como `fastapi` e `sqlalchemy`, execute opcionalmente no host:

```bash
cd backend
uv sync
```

e selecione o interpretador da `.venv` criada pelo `uv`.

### PowerShell

```powershell
# Backend
Set-Location backend

Copy-Item docker-compose.yml.example docker-compose.yml
Copy-Item src/core/configs.py.example src/core/configs.py

docker compose up -d --build

docker compose exec backend uv run alembic upgrade head
docker compose exec backend uv run python -m seeders.database_seeder

# Opcional: dependências Python também no host/editor
uv sync

# Frontend
Set-Location ..\frontend

Copy-Item .env.example .env
npm install
```

Depois acesse:

**Frontend:**

```text
http://localhost:5173
```

**API (Swagger):**

```text
http://localhost:8000/docs
```

> Se o sistema estiver rodando via Docker, **não é necessário executar `uvicorn` ou `npm run dev` manualmente no host**.

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

## Frontend

- [x] Estrutura do projeto
- [x] Configuração do Vite
- [x] Configuração do Vuetify
- [x] Configuração do Vue Router
- [x] Configuração do Pinia
- [x] Serviço de API
- [x] Serviço de autenticação
- [x] Store de autenticação
- [x] Página de login
- [x] Página inicial
- [x] Proteção de rotas
- [x] Integração com a API
- [x] Páginas de gestão de usuários
- [x] Páginas de gestão de fornecedores
- [x] Páginas de gestão de produtos

---

A documentação será atualizada conforme novas funcionalidades forem adicionadas.
