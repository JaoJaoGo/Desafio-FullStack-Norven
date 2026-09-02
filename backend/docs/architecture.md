# Arquitetura do Backend

Este documento descreve a arquitetura do backend do projeto Desafio FullStack Norven, detalhando a estrutura de camadas, responsabilidades e decisões arquiteturais.

## Visão Geral

O backend segue uma arquitetura em camadas com separação clara de responsabilidades:

```
HTTP Request
     ↓
Endpoint (API Layer)
     ↓
Controller (Coordination Layer)
     ↓
Service (Business Logic Layer)
     ↓
Repository (Data Access Layer)
     ↓
Model (ORM Layer)
     ↓
PostgreSQL
```

## Camadas da Arquitetura

### 1. Endpoints (API Layer)

**Localização:** `src/api/v1/endpoints/`

**Responsabilidades:**
- Definir rotas HTTP (GET, POST, PATCH, DELETE)
- Validar dados de entrada usando Pydantic schemas
- Gerenciar dependências do FastAPI (sessão de banco, autenticação)
- Definir códigos de status HTTP
- Especificar schemas de resposta (response_model)
- Documentação automática via OpenAPI/Swagger

**Exemplo:**

```python
@router.post("/", response_model=UsuarioResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_usuario(data: UsuarioCreateSchema, db: AsyncSession = Depends(get_session)):
    return await UsuarioController.create(data, db)
```

**Princípios:**
- Endpoints públicos não exigem autenticação
- Endpoints protegidos usam `Depends(get_current_user)`
- Validação de dados é delegada ao Pydantic
- Não contêm lógica de negócio

---

### 2. Controllers (Coordination Layer)

**Localização:** `src/controllers/`

**Responsabilidades:**
- Receber requisições dos endpoints
- Delegar operações para os services
- Coordenar o fluxo de dados
- Ser um ponto de orquestração simples

**Exemplo:**

```python
class UsuarioController:
    @staticmethod
    async def create(data: UsuarioCreateSchema, db: AsyncSession) -> UsuarioModel:
        return await UsuarioService.create_usuario(db, data)
```

**Princípios:**
- Métodos estáticos (sem estado)
- Não contêm lógica de negócio
- Não acessam diretamente o banco de dados
- Não lançam exceções HTTP (delegam para services)

---

### 3. Services (Business Logic Layer)

**Localização:** `src/services/`

**Responsabilidades:**
- Implementar regras de negócio
- Coordenar múltiplos repositories
- Validar regras específicas do domínio
- Gerenciar transações (commit/rollback)
- Tratar exceções e converter para HTTP exceptions
- Orquestrar operações complexas

**Exemplo:**

```python
class UsuarioService:
    @staticmethod
    async def create_usuario(db: AsyncSession, data: UsuarioCreateSchema) -> UsuarioModel:
        try:
            # Validação de negócio
            usuario_existente = await UsuarioRepository.find_by_email(db, str(data.email))
            if usuario_existente:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já existe")
            
            # Criação de entidades relacionadas
            endereco = await EnderecoRepository.create(db, data.endereco)
            contato = await ContatoRepository.create(db, data.contato)
            
            # Hash de senha
            hashed_password = get_password_hash(data.password)
            
            # Criação do usuário
            usuario = await UsuarioRepository.create(...)
            
            await db.commit()
            await db.refresh(usuario)
            return usuario
        except HTTPException:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()
            raise HTTPException(...)
```

**Princípios:**
- Gerenciamento de transações explícito
- Rollback em caso de erro
- Validações de integridade de dados
- Coordenação entre repositories
- Tratamento de exceções específicas

---

### 4. Repositories (Data Access Layer)

**Localização:** `src/repositories/`

**Responsabilidades:**
- Executar queries SQL via SQLAlchemy
- Abstrair detalhes de acesso ao banco
- Implementar eager loading de relacionamentos
- Gerenciar locking pessimista (FOR UPDATE)
- Paginação e filtros
- Operações CRUD básicas

**Exemplo:**

```python
class UsuarioRepository:
    @staticmethod
    async def find_by_id(db: AsyncSession, usuario_id: int, with_relations: bool = False):
        query = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
        
        if with_relations:
            query = query.options(
                selectinload(UsuarioModel.endereco),
                selectinload(UsuarioModel.contato)
            )
        
        result = await db.execute(query)
        return result.scalars().unique().one_or_none()
```

**Princípios:**
- Métodos estáticos
- Não contêm lógica de negócio
- Retornam instâncias de Model ou dados brutos
- Usam `flush()` para persistir sem commit
- Usam `selectinload` para eager loading

---

### 5. Models (ORM Layer)

**Localização:** `src/models/`

**Responsabilidades:**
- Representar tabelas do banco de dados
- Definir relacionamentos entre entidades
- Especificar tipos de dados e constraints
- Mapear colunas para atributos Python
- Centralizar metadata do SQLAlchemy

**Exemplo:**

```python
class UsuarioModel(settings.DBBaseModel):
    __tablename__ = "funcionarios"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    endereco: Mapped["EnderecoModel"] = relationship("EnderecoModel", back_populates="usuarios")
    contato: Mapped["ContatoModel"] = relationship("ContatoModel", back_populates="usuario", uselist=False)
```

**Princípios:**
- Herdam de `settings.DBBaseModel`
- Usam `Mapped` para type hints modernos
- Definem `__tablename__` explicitamente
- Configuram relacionamentos bidirecionais
- Centralizados em `__all_models.py` para Alembic

---

## Decisões Arquiteturais

### 1. Async/Await com SQLAlchemy

**Decisão:** Uso de SQLAlchemy assíncrono com `asyncpg` como driver.

**Justificativa:**
- Melhor performance em operações I/O bound
- Escalabilidade superior em cenários concorrentes
- Non-blocking I/O permite atender mais requisições simultaneamente

**Implementação:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine: AsyncEngine = create_async_engine(settings.DB_URL)
Session: AsyncSession = sessionmaker(class_=AsyncSession, bind=engine)
```

---

### 2. Session Management com Dependency Injection

**Decisão:** Sessões de banco injetadas via FastAPI Depends.

**Justificativa:**
- Gerenciamento automático do ciclo de vida da sessão
- Garante fechamento correto da sessão
- Facilita testes com mock de dependências

**Implementação:**
```python
async def get_session() -> Generator:
    session: AsyncSession = Session()
    try:
        yield session
    finally:
        await session.close()

@router.post("/")
async def create_usuario(data: UsuarioCreateSchema, db: AsyncSession = Depends(get_session)):
    ...
```

---

### 3. Eager Loading com selectinload

**Decisão:** Uso de `selectinload` para carregar relacionamentos antecipadamente.

**Justificativa:**
- Evita problema N+1 queries
- Melhora performance em listagens
- Carrega dados relacionados em uma única query

**Implementação:**
```python
query = query.options(
    selectinload(UsuarioModel.endereco),
    selectinload(UsuarioModel.contato)
)
```

---

### 4. Locking Pessimista com FOR UPDATE

**Decisão:** Uso de `with_for_update()` em operações críticas de estoque.

**Justificativa:**
- Previne race conditions em operações de saída de estoque
- Garante consistência de dados em cenários concorrentes
- Essencial para evitar estoque negativo

**Implementação:**
```python
async def lock_by_id(db: AsyncSession, estoque_id: int) -> Optional[EstoqueModel]:
    result = await db.execute(
        select(EstoqueModel)
        .where(EstoqueModel.id == estoque_id)
        .with_for_update()
    )
    return result.scalars().unique().one_or_none()
```

**Quando usar:**
- Operações de saída de estoque (decremento de quantidade)
- Operações que requerem consistência estrita
- Cenários onde múltiplas transações podem modificar o mesmo registro

---

### 5. Flush vs Commit

**Decisão:** Uso de `flush()` para persistir sem commit e `commit()` para finalizar transação.

**Justificativa:**
- `flush()` envia SQL ao banco mas não finaliza transação
- Permite obter IDs gerados antes do commit
- Permite rollback parcial em operações complexas
- `commit()` finaliza a transação e persiste permanentemente

**Implementação:**
```python
# Service layer
endereco = await EnderecoRepository.create(db, data)  # Usa flush interno
contato = await ContatoRepository.create(db, data)   # Usa flush interno
usuario = await UsuarioRepository.create(db, ...)    # Usa flush interno

await db.commit()  # Commit final de toda a transação
```

---

### 6. Centralização de Models

**Decisão:** Todos os models importados em `__all_models.py`.

**Justificativa:**
- Facilita importação no Alembic
- Garante que todos os models sejam registrados no metadata
- Centraliza definições para migrations

**Implementação:**
```python
# models/__all_models.py
from .pais_model import PaisModel
from .estado_model import EstadoModel
from .cidade_model import CidadeModel
# ... todos os models

# migrations/env.py
import models.__all_models
target_metadata = settings.DBBaseModel.metadata
```

---

### 7. Autenticação JWT com Dependency Injection

**Decisão:** Autenticação via JWT com dependência `get_current_user`.

**Justificativa:**
- Stateless authentication
- Padrão OAuth2 Bearer Token
- Integração nativa com FastAPI
- Separação clara entre autenticação e autorização

**Implementação:**
```python
async def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
    user_id = payload.get("sub")
    user = await UsuarioRepository.find_by_id(db, user_id)
    return user

@router.get("/", dependencies=[Depends(get_current_user)])
async def list_usuarios():
    ...
```

---

## Padrões de Código

### Validação em Múltiplas Camadas

1. **Endpoint:** Validação de estrutura de dados (Pydantic)
2. **Service:** Validação de regras de negócio
3. **Repository:** Validação de integridade de banco
4. **Database:** Constraints SQL (unique, foreign key, check)

### Tratamento de Exceções

```python
try:
    # Operação
    await db.commit()
except HTTPException:
    await db.rollback()
    raise  # Re-lança HTTP exception
except IntegrityError:
    await db.rollback()
    raise HTTPException(status_code=409, detail="Violação de integridade")
except Exception:
    await db.rollback()
    raise  # Re-lança exceção genérica
```

### Paginação Padrão

```python
async def list(db: AsyncSession, page: int, per_page: int):
    count_query = select(func.count(Model.id))
    total = (await db.execute(count_query)).scalar_one()
    
    offset = (page - 1) * per_page
    query = select(Model).offset(offset).limit(per_page)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return items, total
```

---

## Convenções de Nomenclatura

- **Tabelas:** snake_case (ex: `funcionarios`, `enderecos`)
- **Colunas:** snake_case (ex: `nome`, `endereco_id`)
- **Models:** PascalCase com sufixo `Model` (ex: `UsuarioModel`)
- **Repositories:** PascalCase com sufixo `Repository` (ex: `UsuarioRepository`)
- **Services:** PascalCase com sufixo `Service` (ex: `UsuarioService`)
- **Controllers:** PascalCase com sufixo `Controller` (ex: `UsuarioController`)
- **Schemas:** PascalCase com sufixo `Schema` (ex: `UsuarioSchema`)
- **Endpoints:** snake_case (ex: `create_usuario`, `list_usuarios`)

---

## Fluxo Completo de uma Requisição

Exemplo de criação de usuário:

```
1. Cliente faz POST /usuarios com JSON
   ↓
2. Endpoint valida JSON com UsuarioCreateSchema
   ↓
3. Endpoint injeta db via Depends(get_session)
   ↓
4. Controller.create() é chamado
   ↓
5. Service.create_usuario() é chamado
   ↓
6. Service valida se e-mail já existe
   ↓
7. Service cria endereço via EnderecoRepository.create()
   ↓
8. Service cria contato via ContatoRepository.create()
   ↓
9. Service faz hash da senha
   ↓
10. Service cria usuário via UsuarioRepository.create()
    ↓
11. Service faz db.commit()
    ↓
12. Service retorna usuário
    ↓
13. Controller retorna usuário
    ↓
14. Endpoint serializa com UsuarioResponseSchema
    ↓
15. Cliente recebe JSON com usuário criado
```

---

## Considerações de Performance

### Índices de Banco

Índices são definidos nos models para otimizar queries:

```python
__table_args__ = (
    Index("idx_usuario_email", "email"),
    Index("idx_estoque_produto", "produto_id"),
)
```

### Eager Loading Estratégico

Carregar relacionamentos apenas quando necessário:

```python
# Sem relacionamentos (mais rápido)
await UsuarioRepository.find_by_id(db, id)

# Com relacionamentos (evita N+1)
await UsuarioRepository.find_by_id(db, id, with_relations=True)
```

### Queries Otimizadas

Usar `select()` com colunas específicas para listagens:

```python
query = select(
    EstoqueModel.id.label("id"),
    ProdutoModel.nome.label("produto_nome"),
).join(ProdutoModel, ...)
```

---

## Segurança

### Hash de Senhas

Senhas são hasheadas com bcrypt antes de persistir:

```python
hashed_password = get_password_hash(data.password)
```

### Autenticação JWT

Tokens JWT são usados para autenticação stateless:

```python
token = create_access_token(sub=str(user.id))
```

### Proteção de Rotas

Rotas sensíveis exigem autenticação:

```python
@router.get("/", dependencies=[Depends(get_current_user)])
```

---

## Testabilidade

A arquitetura facilita testes através de:

- **Dependency Injection:** Mock de sessões e serviços
- **Camadas separadas:** Testes unitários por camada
- **Métodos estáticos:** Fácil instanciação para testes
- **Transações controladas:** Rollback após testes