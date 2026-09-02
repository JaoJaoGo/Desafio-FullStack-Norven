# Documentação do Banco de Dados

Este documento descreve a estrutura do banco de dados PostgreSQL, incluindo entidades, relacionamentos, decisões de modelagem, migrations e seeders.

## Índice

- [Visão Geral](#visão-geral)
- [Entidades e Relacionamentos](#entidades-e-relacionamentos)
- [Decisões de Modelagem](#decisões-de-modelagem)
- [Migrations](#migrations)
- [Seeders](#seeders)

---

## Visão Geral

### Tecnologias

- **Banco de Dados:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0 (Async)
- **Migrations:** Alembic
- **Driver:** asyncpg

### Configuração

**String de Conexão (Docker):**
```
postgresql+asyncpg://postgres:170602%40Jv@postgres:5432/norven
```

**Porta Exposta (Host):**
- `5434` (mapeada para `5432` no container)

### Estrutura de Tabelas

O banco de dados é organizado em 16 tabelas divididas em 4 grupos principais:

1. **Geografia:** `pais`, `estado`, `cidade`
2. **Pessoas e Contatos:** `contatos`, `enderecos`, `funcionarios`, `fornecedores`
3. **Produtos:** `categorias`, `unidades_medidas`, `informacoes_nutricionais`, `produtos`, `lotes`
4. **Estoque:** `entradas`, `estoques`, `saidas`

---

## Entidades e Relacionamentos

### Diagrama ER Simplificado

```
┌─────────────────────────────────────────────────────────────────┐
│                        GEOGRAFIA                                │
├─────────────────────────────────────────────────────────────────┤
│  pais (1) ────────< (N) estado (1) ────────< (N) cidade      │
│  (id, nome, sigla)  (id, nome, uf, pais_id)  (id, nome, uf)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (municipio_id)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PESSOAS E CONTATOS                           │
├─────────────────────────────────────────────────────────────────┤
│  contatos (1) ────────< (1) funcionarios (N) ────────> produtos│
│  (cod_pais, ddd, numero)  (nome, email, senha)                │
│                            │                                     │
│                            │ (endereco_id)                      │
│                            ▼                                     │
│  contatos (1) ────────< (N) fornecedores (N) ────────> entradas│
│                        (nome, cnpj)                             │
│                            │                                     │
│                            │ (endereco_id)                      │
│                            ▼                                     │
│                       enderecos                                  │
│              (logradouro, numero, municipio_id)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (categoria_id, unidade_medida_id)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PRODUTOS                                │
├─────────────────────────────────────────────────────────────────┤
│  categorias (1) ────────< (N) produtos (1) ────────< (N) lotes │
│  (nome)                   (nome, eh_perecivel)        (numero)   │
│                            │                                   │
│                            │ (unidade_medida_id)               │
│                            ▼                                   │
│  unidades_medidas (1) ───< (1) informacoes_nutricionais (1) ──<│
│  (nome, sigla)            (porcao, valor_energetico)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (lote_id)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          ESTOQUE                                │
├─────────────────────────────────────────────────────────────────┤
│  lotes (1) ────────< (N) entradas (1) ────────< (1) estoques  │
│                    (quantidade, preco_custo)    (quantidade)   │
│                    (fornecedor_id, usuario_id)    (corredor)    │
│                            │                                   │
│                            │ (estoque_id)                      │
│                            ▼                                   │
│  funcionarios (1) ────────< (N) saidas                          │
│                        (quantidade, tipo_saida, preco_venda)   │
└─────────────────────────────────────────────────────────────────┘
```

### Detalhes das Entidades

#### 1. Geografia

##### `pais`

**Descrição:** Tabela de países com códigos internacionais.

**Colunas:**
- `id` (BigInteger, PK): Identificador único
- `nome` (String(60), nullable): Nome do país
- `nome_pt` (String(60), nullable): Nome em português
- `sigla` (String(2), nullable): Sigla do país (ex: BR, US)
- `bacen` (Integer, nullable): Código BACEN
- `ddi` (Integer, nullable): Código DDI

**Relacionamentos:**
- `estados` (1:N): Um país tem muitos estados

**Decisões:**
- Uso de `BigInteger` para compatibilidade com dados externos (IBGE, BACEN)
- Todos os campos nullable para flexibilidade de dados incompletos

---

##### `estado`

**Descrição:** Estados/províncias federativas.

**Colunas:**
- `id` (BigInteger, PK): Identificador único
- `nome` (String(60), nullable): Nome do estado
- `uf` (String(2), nullable): Sigla da UF (ex: GO, SP)
- `ibge` (Integer, nullable): Código IBGE
- `pais` (BigInteger, FK): Referência ao país
- `ddd` (JSON, nullable): Lista de DDDs do estado

**Relacionamentos:**
- `pais` (N:1): Muitos estados pertencem a um país
- `cidades` (1:N): Um estado tem muitas cidades

**Índices:**
- `idx_estado_pais`: Otimiza consultas por país

**Decisões:**
- DDDs armazenados em JSON para flexibilidade (múltiplos DDDs por estado)
- Campo `uf` duplicado como FK para cidade para otimizar consultas

---

##### `cidade`

**Descrição:** Municípios brasileiros com coordenadas geográficas.

**Colunas:**
- `id` (BigInteger, PK): Identificador único
- `nome` (String(120), nullable): Nome da cidade
- `uf` (BigInteger, FK): Referência ao estado
- `ibge` (Integer, nullable): Código IBGE
- `lat_lon` (PostgreSQLPoint, nullable): Coordenadas geográficas (POINT)
- `cod_tom` (SmallInteger, nullable): Código de tipo de município

**Relacionamentos:**
- `estado` (N:1): Muitas cidades pertencem a um estado
- `enderecos` (1:N): Uma cidade tem muitos endereços

**Índices:**
- `idx_cidade_uf`: Otimiza consultas por UF
- `idx_cidade_nome_uf`: Otimiza buscas por nome e UF

**Decisões:**
- Tipo customizado `PostgreSQLPoint` para coordenadas
- `cod_tom` para classificação de municípios (capital, interior, etc.)

---

#### 2. Pessoas e Contatos

##### `contatos`

**Descrição:** Informações de contato telefônico.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `cod_pais` (String(30)): Código do país (ex: 55)
- `ddd` (String(3)): Código DDD
- `numero` (String(30)): Número do telefone

**Relacionamentos:**
- `usuario` (1:1): Um contato pertence a um usuário
- `fornecedores` (1:N): Um contato pode ser de múltiplos fornecedores

**Constraints:**
- `un_contato_telefone`: Unicidade de (cod_pais, ddd, numero)

**Decisões:**
- Unicidade composta para evitar duplicação de telefones
- Relacionamento 1:1 com usuário (uselist=False)

---

##### `enderecos`

**Descrição:** Endereços físicos.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `logradouro` (String(50)): Nome da rua/avenida
- `numero` (String(10), nullable): Número
- `complemento` (String(50), nullable): Complemento
- `cep` (String(11)): CEP
- `bairro` (String(30)): Bairro
- `municipio_id` (BigInteger, FK): Referência à cidade

**Relacionamentos:**
- `municipio` (N:1): Muitos endereços em uma cidade
- `usuarios` (1:N): Um endereço pode ter múltiplos usuários
- `fornecedores` (1:N): Um endereço pode ter múltiplos fornecedores

**Decisões:**
- CEP como String para preservar formatação
- Campo `numero` nullable para endereços sem número

---

##### `funcionarios` (usuarios)

**Descrição:** Usuários do sistema (funcionários).

**Colunas:**
- `id` (Integer, PK): Identificador único
- `nome` (String(50)): Nome completo
- `email` (String(50), unique): E-mail (login)
- `senha` (String(255)): Senha hasheada (bcrypt)
- `nivel_acesso` (Enum): ADMINISTRADOR ou OPERADOR
- `id_endereco` (Integer, FK): Referência ao endereço
- `id_contato` (Integer, FK, unique): Referência ao contato

**Relacionamentos:**
- `endereco` (N:1): Muitos usuários em um endereço
- `contato` (1:1): Um usuário tem um contato
- `produtos` (1:N): Um usuário pode cadastrar produtos
- `entradas` (1:N): Um usuário pode registrar entradas
- `saidas` (1:N): Um usuário pode registrar saídas

**Decisões:**
- Tabela nomeada como `funcionarios` mas representa usuários do sistema
- Senha hasheada com bcrypt
- Nível de acesso para controle de permissões

---

##### `fornecedores`

**Descrição:** Fornecedores de produtos.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `nome` (String(50)): Nome do fornecedor
- `cnpj` (CHAR(14), unique): CNPJ
- `id_endereco` (Integer, FK): Referência ao endereço
- `id_contato` (Integer, FK): Referência ao contato

**Relacionamentos:**
- `endereco` (N:1): Muitos fornecedores em um endereço
- `contato` (N:1): Muitos fornecedores com mesmo contato
- `entradas` (1:N): Um fornecedor tem muitas entradas

**Decisões:**
- CNPJ como CHAR(14) para preservar zeros à esquerda
- Unicidade de CNPJ

---

#### 3. Produtos

##### `categorias`

**Descrição:** Categorias de produtos.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `nome` (String(30), unique): Nome da categoria

**Relacionamentos:**
- `produtos` (1:N): Uma categoria tem muitos produtos

**Decisões:**
- Nome único para evitar duplicação

---

##### `unidades_medidas`

**Descrição:** Unidades de medida (kg, g, L, mL, un).

**Colunas:**
- `id` (Integer, PK): Identificador único
- `nome` (String(30), unique): Nome completo
- `sigla` (String(5), unique): Sigla (ex: kg, L)

**Relacionamentos:**
- `produtos` (1:N): Uma unidade tem muitos produtos
- `informacoes_nutricionais` (1:N): Uma unidade tem muitas informações nutricionais

**Decisões:**
- Nome e sigla únicos para padronização

---

##### `informacoes_nutricionais`

**Descrição:** Informações nutricionais de produtos.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `porcao_quantidade` (Numeric(10,2)): Quantidade da porção
- `valor_energetico_kcal` (Numeric(10,2), nullable): Valor energético
- `carboidratos_g` (Numeric(10,2), nullable): Carboidratos
- `proteinas_g` (Numeric(10,2), nullable): Proteínas
- `gorduras_totais_g` (Numeric(10,2), nullable): Gorduras totais
- `ingredientes` (Text, nullable): Lista de ingredientes
- `alergenicos` (Text, nullable): Lista de alergênicos
- `id_unidade_porcao` (Integer, FK): Unidade da porção

**Relacionamentos:**
- `unidade_porcao` (N:1): Muitas informações com uma unidade
- `produtos` (1:N): Uma informação nutricional pode estar em múltiplos produtos

**Constraints:**
- `ck_in_porcao_quantidade`: porcao_quantidade > 0
- `ck_in_valor_energetico`: valor_energetico_kcal >= 0
- `ck_in_carboidratos`: carboidratos_g >= 0
- `ck_in_proteinas`: proteinas_g >= 0
- `ck_in_gorduras_totais`: gorduras_totais_g >= 0

**Decisões:**
- Todos os valores nutricionais nullable para flexibilidade
- Ingredientes e alergênicos em Text para listas longas

---

##### `produtos`

**Descrição:** Produtos do estoque.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `cod_idt` (String(50), unique): Código identificador
- `nome` (String(50), unique): Nome do produto
- `descricao` (Text, nullable): Descrição
- `preco_venda_atual` (Numeric(10,2)): Preço de venda atual
- `eh_perecivel` (Boolean, default false): Produto perecível
- `data_cadastro` (DateTime, auto): Data de cadastro
- `id_funcionario` (Integer, FK): Usuário que cadastrou
- `id_categoria` (Integer, FK): Categoria do produto
- `id_unidade_medida` (Integer, FK): Unidade de medida
- `id_inf_nut` (Integer, FK, nullable): Informação nutricional

**Relacionamentos:**
- `usuario` (N:1): Muitos produtos por usuário
- `categoria` (N:1): Muitos produtos por categoria
- `unidade_medida` (N:1): Muitos produtos por unidade
- `informacao_nutricional` (N:1, nullable): Muitos produtos com mesma informação
- `lotes` (1:N): Um produto tem muitos lotes

**Constraints:**
- `ck_produto_preco_venda`: preco_venda_atual >= 0

**Índices:**
- `idx_produto_id_funcionario`: Otimiza consultas por usuário
- `idx_produto_id_categoria`: Otimiza consultas por categoria
- `idx_produto_id_unidade_medida`: Otimiza consultas por unidade

**Decisões:**
- `cod_idt` e `nome` únicos para evitar duplicação
- `eh_perecivel` para controle de validade
- Informação nutricional opcional (nem todos produtos têm)

---

##### `lotes`

**Descrição:** Lotes de produtos com controle de validade.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `numero` (String(30)): Número do lote
- `data_validade` (Date, nullable): Data de validade
- `id_produto` (Integer, FK): Produto do lote

**Relacionamentos:**
- `produto` (N:1): Muitos lotes por produto
- `entradas` (1:N): Um lote tem muitas entradas

**Constraints:**
- `un_lote_produto_numero`: Unicidade de (id_produto, numero)

**Índices:**
- `idx_lote_numero`: Otimiza buscas por número
- `idx_lote_data_validade`: Otimiza consultas de vencimento

**Decisões:**
- Unicidade composta para permitir mesmo número em produtos diferentes
- Data de validade nullable para produtos não perecíveis

---

#### 4. Estoque

##### `entradas`

**Descrição:** Registro de entrada de produtos no estoque.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `data_entrada` (DateTime, auto): Data da entrada
- `quantidade` (Numeric(12,3)): Quantidade recebida
- `preco_custo_unitario` (Numeric(10,2)): Preço de custo unitário
- `tipo_entrada` (String(30)): Tipo de entrada
- `observacao` (Text, nullable): Observações
- `id_fornecedor` (Integer, FK): Fornecedor
- `id_lote` (Integer, FK): Lote
- `id_funcionario` (Integer, FK): Usuário responsável

**Relacionamentos:**
- `fornecedor` (N:1): Muitas entradas por fornecedor
- `lote` (N:1): Muitas entradas por lote
- `usuario` (N:1): Muitas entradas por usuário
- `estoques` (1:N): Uma entrada cria um estoque

**Constraints:**
- `ck_entrada_quantidade`: quantidade > 0
- `ck_entrada_preco_custo`: preco_custo_unitario >= 0

**Índices:**
- `idx_entrada_id_lote`: Otimiza consultas por lote
- `idx_entrada_id_fornecedor`: Otimiza consultas por fornecedor
- `idx_entrada_data_entrada`: Otimiza consultas por data
- `idx_entrada_fornecedor_data`: Otimiza consultas por fornecedor e data
- `idx_entrada_id_funcionario`: Otimiza consultas por usuário
- `idx_entrada_tipo_data`: Otimiza consultas por tipo e data

**Decisões:**
- Quantidade com 3 casas decimais para precisão
- Índices compostos para consultas comuns

---

##### `estoques`

**Descrição:** Quantidade física em localização específica.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `quantidade_atual` (Numeric(12,3)): Quantidade disponível
- `corredor` (String(30)): Corredor do armazém
- `prateleira` (String(30)): Prateleira
- `secao` (String(30)): Seção
- `id_entrada` (Integer, FK): Entrada originária

**Relacionamentos:**
- `entrada` (N:1): Muitos estoques por entrada
- `saidas` (1:N): Um estoque tem muitas saídas

**Constraints:**
- `ck_estoque_quantidade`: quantidade_atual >= 0

**Índices:**
- `idx_estoque_id_entrada`: Otimiza consultas por entrada

**Decisões:**
- Localização física dividida em corredor, prateleira e seção
- Constraint para evitar estoque negativo

---

##### `saidas`

**Descrição:** Registro de saída de produtos do estoque.

**Colunas:**
- `id` (Integer, PK): Identificador único
- `data_saida` (DateTime, auto): Data da saída
- `quantidade` (Numeric(12,3)): Quantidade retirada
- `preco_venda_unitario` (Numeric(10,2), nullable): Preço de venda
- `id_estoque` (Integer, FK): Estoque de origem
- `id_funcionario` (Integer, FK): Usuário responsável
- `tipo_saida` (Enum): VENDA, PERDA, AVARIA, VENCIMENTO, RECALL

**Relacionamentos:**
- `estoque` (N:1): Muitas saídas por estoque
- `usuario` (N:1): Muitas saídas por usuário

**Constraints:**
- `ck_saida_quantidade`: quantidade > 0
- `ck_saida_preco`: Preço obrigatório apenas para VENDA

**Índices:**
- `idx_saida_id_estoque`: Otimiza consultas por estoque
- `idx_saida_data_saida`: Otimiza consultas por data
- `idx_saida_tipo_data`: Otimiza consultas por tipo e data
- `idx_saida_id_funcionario`: Otimiza consultas por usuário

**Decisões:**
- Enum para tipo de saída
- Constraint complexa para validar preço por tipo

---

## Decisões de Modelagem

### 1. Tipos de Dados

#### BigInteger vs Integer

**Uso de BigInteger:**
- Tabelas de geografia (`pais`, `estado`, `cidade`)
- Motivo: Compatibilidade com códigos externos (IBGE, BACEN)

**Uso de Integer:**
- Tabelas internas do sistema
- Motivo: Economia de espaço e performance

#### Numeric vs Float

**Uso de Numeric:**
- Todos os valores monetários e quantidades
- Motivo: Precisão exata em cálculos financeiros

**Precisão:**
- `Numeric(10, 2)`: Valores monetários (preço)
- `Numeric(12, 3)`: Quantidades (3 casas decimais para precisão)
- `Numeric(10, 2)`: Valores nutricionais

#### JSON

**Uso em `estado.ddd`:**
- Armazena lista de DDDs como JSON
- Motivo: Flexibilidade para múltiplos DDDs por estado

#### PostgreSQLPoint

**Uso em `cidade.lat_lon`:**
- Tipo customizado para coordenadas geográficas
- Motivo: Suporte nativo do PostgreSQL para operações espaciais

### 2. Nomenclatura

#### Tabelas

- **snake_case:** `funcionarios`, `unidades_medidas`, `informacoes_nutricionais`
- **Plural:** Convenção para tabelas
- **Exceções:** `pais`, `estado`, `cidade` (mantidos do dataset original)

#### Colunas

- **snake_case:** `id_endereco`, `id_funcionario`, `preco_venda_atual`
- **PK:** `id` (simples)
- **FK:** `id_tabela` ou `tabela_id` (consistente)

#### Relacionamentos

- **bidirecionais:** Sempre definidos em ambos os lados
- **back_populates:** Nome da relação oposta
- **uselist=False:** Para relacionamentos 1:1

### 3. Constraints

#### Unique Constraints

**Unicidade Simples:**
- `funcionarios.email`: Login único
- `fornecedores.cnpj`: CNPJ único
- `categorias.nome`: Categoria única
- `unidades_medidas.nome` e `sigla`: Unidade única

**Unicidade Composta:**
- `lotes (id_produto, numero)`: Mesmo número em produtos diferentes
- `contatos (cod_pais, ddd, numero)`: Telefone único

#### Check Constraints

**Validações de Negócio:**
- Quantidades > 0 (entradas, saídas, porções)
- Preços >= 0 (produtos, entradas)
- Estoque >= 0 (estoques)
- Preço obrigatório apenas para VENDA (saídas)
- Valores nutricionais >= 0

### 4. Índices

#### Estratégia de Indexação

**Índices Simples:**
- Chaves estrangeiras frequentemente usadas em joins
- Campos únicos (já indexados automaticamente)
- Campos de busca (nome, numero, data)

**Índices Compostos:**
- Consultas frequentes com múltiplos filtros
- Ex: `idx_entrada_fornecedor_data` (fornecedor + data)
- Ex: `idx_saida_tipo_data` (tipo + data)

**Índices Especiais:**
- `idx_lote_data_validade`: Para consultas de vencimento
- `idx_cidade_nome_uf`: Para busca de cidades

### 5. Relacionamentos

#### 1:1 (One-to-One)

**Exemplo:** `funcionarios` ↔ `contatos`

```python
contato: Mapped[Optional["ContatoModel"]] = relationship(
    "ContatoModel", 
    back_populates="usuario", 
    uselist=False
)
```

**Decisão:** `uselist=False` para indicar cardinalidade 1:1

#### 1:N (One-to-Many)

**Exemplo:** `categorias` ↔ `produtos`

```python
produtos: Mapped[List["ProdutoModel"]] = relationship(
    "ProdutoModel", 
    back_populates="categoria"
)
```

**Decisão:** Relação padrão, mais comum

#### N:1 (Many-to-One)

**Exemplo:** `produtos` ↔ `categorias`

```python
categoria: Mapped["CategoriaModel"] = relationship(
    "CategoriaModel", 
    back_populates="produtos"
)
```

**Decisão:** Inverso de 1:N, sempre definido para consistência

### 6. Valores Padrão

#### Server Defaults

**Timestamps:**
```python
data_entrada: Mapped[datetime] = mapped_column(
    DateTime, 
    nullable=False, 
    server_default=text("CURRENT_TIMESTAMP")
)
```

**Booleanos:**
```python
eh_perecivel: Mapped[bool] = mapped_column(
    Boolean, 
    nullable=False, 
    server_default=text("false")
)
```

**Decisão:** Server defaults para garantir consistência mesmo sem aplicação

### 7. Nullable vs Not Null

**NotNull Obrigatório:**
- Chaves primárias
- Chaves estrangeiras
- Campos de negócio críticos (nome, email, quantidade)

**Nullable Permitido:**
- Campos opcionais (complemento, observacao)
- Campos que podem não se aplicar (data_validade para não perecíveis)
- Campos de dados externos incompletos (geografia)

### 8. Enumerações

**Tipos de Saída:**
```python
class TipoSaidaEnum(str, Enum):
    VENDA = "VENDA"
    PERDA = "PERDA"
    AVARIA = "AVARIA"
    VENCIMENTO = "VENCIMENTO"
    RECALL = "RECALL"
```

**Nível de Acesso:**
```python
class NivelAcessoEnum(str, Enum):
    ADMINISTRADOR = "administrador"
    OPERADOR = "operador"
```

**Decisão:** Enums Python com `native_enum=False` para flexibilidade

---

## Migrations

### Configuração do Alembic

**Localização:** `migrations/`

**Arquivo de Configuração:** `migrations/env.py`

**Configurações Principais:**

```python
# Importa todos os models para registro no metadata
import models.__all_models

# Metadata do SQLAlchemy
target_metadata = settings.DBBaseModel.metadata

# Suporte a migrations assíncronas
async def run_async_migrations() -> None:
    connectable = create_async_engine(
        settings.DB_URL,
        poolclass=pool.NullPool,
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
```

**Decisões:**
- Migrations assíncronas para compatibilidade com SQLAlchemy async
- `compare_type=True` para detectar mudanças de tipo
- Centralização de models em `__all_models.py`

### Comandos de Migration

**Criar nova migration:**
```bash
uv run alembic revision --autogenerate -m "descricao"
```

**Aplicar migrations:**
```bash
uv run alembic upgrade head
```

**Reverter última migration:**
```bash
uv run alembic downgrade -1
```

**Histórico de migrations:**
```bash
uv run alembic history
```

### Estrutura de Versions

**Localização:** `migrations/versions/`

**Padrão de Nomenclatura:**
```
{revision}_{descricao}.py
```

**Exemplo:**
```
001_initial_schema.py
002_add_produto_perecivel.py
003_add_saida_tipo_enum.py
```

### Boas Práticas

1. **Sempre usar `--autogenerate`:** Evita erros manuais
2. **Revisar migrations geradas:** Verificar se refletem a intenção
3. **Testar migrations em ambiente de desenvolvimento:** Antes de produção
4. **Nunca editar migrations aplicadas:** Cria nova migration para alterações
5. **Manter migrations reversíveis:** Implementar `downgrade()` quando necessário

---

## Seeders

### Estrutura de Seeders

**Localização:** `seeders/`

**Arquivos:**
- `database_seeder.py`: Orquestrador principal
- `geography_seeder.py`: Dados geográficos (países, estados, cidades)
- `admin_seeder.py`: Usuário administrador padrão
- `data/`: Arquivos SQL com dados brutos

### Geography Seeder

**Função:** Popular tabelas de geografia com dados do IBGE

**Fonte de Dados:** `seeders/data/paises.sql`, `estado.sql`, `cidade.sql`

**Processo:**

1. **Leitura de Arquivos COPY:**
   - Parser customizado para extrair dados de arquivos PostgreSQL COPY
   - Conversão de valores `\N` para `None`

2. **Inserção com UPSERT:**
   ```sql
   INSERT INTO tabela (...)
   VALUES (...)
   ON CONFLICT (id)
   DO UPDATE SET ...
   ```

3. **Reset de Sequences:**
   - Atualiza sequences após inserção para evitar conflitos

**Decisões:**
- UPSERT para permitir reexecução segura
- Parser customizado para compatibilidade com dumps PostgreSQL
- Reset de sequences para manter consistência

### Admin Seeder

**Função:** Criar usuário administrador padrão

**Configurações:**
- **Email:** `admin@norven.com.br`
- **Senha:** Definida em `settings.PRIMARY_ADMIN_PASSWORD`
- **Nível:** ADMINISTRADOR
- **Localização:** Goiânia/GO (requer geography seeder executado antes)

**Processo:**

1. **Verifica se admin já existe:**
   - Evita duplicação em reexecuções

2. **Busca cidade de Goiânia:**
   - Requer geography seeder executado antes
   - Join com estado para garantir Goiânia/GO

3. **Cria endereço e contato:**
   - Endereço de teste
   - Contato com DDD 62

4. **Cria usuário:**
   - Senha hasheada com bcrypt
   - Nível de acesso ADMINISTRADOR

**Decisões:**
- Verificação de existência para idempotência
- Dependência explícita de geography seeder
- Senha configurável via environment variable

### Database Seeder

**Função:** Orquestrador principal de todos os seeders

**Processo:**

```python
async with Session() as session:
    try:
        async with session.begin():
            await seed_geography(session)
            await seed_admin(session)
    except Exception:
        await session.rollback()
        raise
```

**Decisões:**
- Transação única para consistência
- Rollback em caso de erro
- Ordem explícita (geography antes de admin)

### Execução de Seeders

**Via Docker:**
```bash
docker compose exec backend uv run python -m seeders.database_seeder
```

**Via Python (local):**
```bash
uv run python -m seeders.database_seeder
```

### Boas Práticas

1. **Idempotência:** Seeders devem poder ser reexecutados sem erro
2. **Transações:** Usar transações para consistência
3. **Verificação:** Verificar se dados já existem antes de inserir
4. **Ordem:** Respeitar dependências entre seeders
5. **Configuração:** Dados sensíveis via environment variables

---

## Manutenção do Banco de Dados

### Backups

**Dump do Banco:**
```bash
docker compose exec postgres pg_dump -U postgres norven > backup.sql
```

**Restore do Banco:**
```bash
docker compose exec -T postgres psql -U postgres norven < backup.sql
```

### Monitoramento

**Consultas Lentas:**
```sql
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Tamanho de Tabelas:**
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Limpeza

**Vacuum (reclaim space):**
```sql
VACUUM ANALYZE;
```

**Reindex (rebuild indexes):**
```sql
REINDEX DATABASE norven;
```

---

## Considerações de Performance

### 1. Índices

**Índices Criados:**
- 20+ índices estratégicos
- Índices compostos para consultas comuns
- Índices em chaves estrangeiras

**Impacto:**
- Melhora performance de leitura
- Aumenta tempo de escrita (trade-off)
- Consome espaço em disco

### 2. Eager Loading

**Uso de `selectinload`:**
- Evita problema N+1
- Carrega relacionamentos em uma query
- Usado em consultas detalhadas

### 3. Paginação

**Todas as listagens:**
- Suportam paginação
- `offset` e `limit` em queries
- Evita sobrecarga de memória

### 4. Lock Pessimista

**Uso de `FOR UPDATE`:**
- Operações críticas de escrita
- Evita race conditions
- Usado apenas quando necessário

---

## Segurança

### 1. Senhas

**Hash com bcrypt:**
- Nunca armazenadas em texto plano
- `get_password_hash()` para criar
- Verificação via `verify_password()`

### 2. SQL Injection

**Proteção via SQLAlchemy:**
- Queries parametrizadas automaticamente
- Nunca concatenar strings em queries
- Uso de `text()` apenas quando necessário

### 3. Acesso

**Autenticação:**
- Todas as operações exigem JWT
- Usuário registrado em auditoria

**Autorização:**
- Nível de acesso (ADMINISTRADOR/OPERADOR)
- Implementado via middleware

---

## Troubleshooting

### Problemas Comuns

**Migration falha:**
- Verificar conflito de nomes
- Revisar código da migration
- Usar `alembic downgrade` se necessário

**Seeder falha:**
- Verificar ordem de execução
- Verificar dependências (geography antes de admin)
- Verificar dados de entrada

**Erro de constraint:**
- Verificar unicidade de dados
- Verificar check constraints
- Revisar regras de negócio

**Performance lenta:**
- Verificar índices existentes
- Usar `EXPLAIN ANALYZE` em queries
- Considerar eager loading
