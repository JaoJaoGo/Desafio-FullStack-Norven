# Regras de Negócio

Este documento descreve as regras de negócio do sistema de controle de estoque, incluindo perecibilidade, lotes, entradas, estoques, saídas, auditoria e histórico.

## Índice

- [Perecibilidade](#perecibilidade)
- [Lotes](#lotes)
- [Entradas](#entradas)
- [Estoques](#estoques)
- [Saídas](#saídas)
- [Auditoria e Histórico](#auditoria-e-histórico)

---

## Perecibilidade

### Definição

Um produto é considerado perecível quando possui data de validade limitada e requer controle rigoroso de vencimento.

### Regras

#### 1. Classificação de Perecibilidade

- **Produto Perecível:** `eh_perecivel = true`
  - Requer data de validade obrigatória
  - Exemplos: alimentos, medicamentos, produtos químicos
  
- **Produto Não Perecível:** `eh_perecivel = false`
  - Data de validade opcional
  - Exemplos: utensílios, embalagens, materiais de limpeza

#### 2. Validação de Data de Validade

Ao criar um lote para um produto perecível:

```python
if produto.eh_perecivel and data.data_validade is None:
    raise HTTPException(
        status_code=422,
        detail="Data de validade é obrigatória para produtos perecíveis."
    )
```

#### 3. Unicidade de Lote por Produto

O número do lote deve ser único para cada produto:

```python
# Constraint no banco
UniqueConstraint("id_produto", "numero", name="un_lote_produto_numero")
```

#### 4. Índices de Validade

Para otimizar consultas de produtos próximos ao vencimento:

```python
Index("idx_lote_data_validade", "data_validade")
```

### Status de Produto

O sistema define status baseados em estoque e validade:

- **SEM_ESTOQUE:** Produto sem quantidade em estoque
- **VENCIDO:** Produto com lotes vencidos
- **PROXIMO_VENCIMENTO:** Produto com lotes próximos ao vencimento
- **ESTOQUE_BAIXO:** Produto com quantidade abaixo do mínimo
- **OK:** Produto em condições normais

---

## Lotes

### Definição

Lote é um agrupamento de produtos com características comuns, como número de controle e data de validade.

### Regras

#### 1. Criação de Lote

**Validações:**
- Produto deve existir
- Se produto é perecível, data de validade é obrigatória
- Número do lote deve ser único por produto

**Exemplo:**

```python
async def validate_create(db: AsyncSession, data: LoteCreateSchema):
    produto = await ProdutoRepository.find_by_id(db, data.produto_id)
    
    if produto is None:
        raise HTTPException(404, "Produto não encontrado.")
    
    if produto.eh_perecivel and data.data_validade is None:
        raise HTTPException(422, "Data de validade é obrigatória para produtos perecíveis.")
    
    lote_existente = await LoteRepository.find_by_product_and_number(
        db, data.produto_id, data.numero
    )
    
    if lote_existente is not None:
        raise HTTPException(409, "Já existe um lote com este número para este produto.")
```

#### 2. Atualização de Lote

**Validações:**
- Lote deve existir
- Se número for alterado, deve ser único por produto

**Exemplo:**

```python
if data.numero is not None and data.numero != lote.numero:
    existente = await LoteRepository.find_by_product_and_number(
        db, lote.produto_id, data.numero
    )
    
    if existente is not None and existente.id != lote.id:
        raise HTTPException(409, "Já existe um lote com este número para este produto.")
```

#### 3. Relacionamento com Entradas

Um lote pode ter múltiplas entradas, mas cada entrada pertence a um único lote:

```python
entradas: Mapped[List["EntradaModel"]] = relationship(
    "EntradaModel", 
    back_populates="lote"
)
```

#### 4. Resolução de Lote em Entradas

Ao criar uma entrada, o lote pode ser:
- **Existente:** Referenciado por `lote_id`
- **Novo:** Criado via `novo_lote` com validação automática

**Exemplo:**

```python
async def _resolve_lote(db: AsyncSession, produto, lote_id, novo_lote):
    if lote_id is not None:
        lote = await LoteRepository.find_by_id(db, lote_id)
        
        if lote is None:
            raise HTTPException(404, "Lote não encontrado.")
        
        if lote.produto_id != produto.id:
            raise HTTPException(409, "Lote não pertence ao produto.")
        
        return lote
    
    # Cria novo lote
    lote_data = LoteCreateSchema(
        produto_id=produto.id,
        numero=novo_lote.numero,
        data_validade=novo_lote.data_validade
    )
    
    return await LoteService.create(db=db, data=lote_data, commit=False)
```

---

## Entradas

### Definição

Entrada representa o registro de produtos recebidos no estoque, associados a um fornecedor e um lote específico.

### Regras

#### 1. Criação de Entrada

**Validações:**
- Produto deve existir
- Fornecedor deve existir
- Lote deve existir ou ser criado
- Quantidade deve ser maior que zero
- Preço de custo unitário deve ser não negativo

**Exemplo:**

```python
async def create(db: AsyncSession, *, produto_id: int, data, current_user: UsuarioModel):
    produto = await ProdutoRepository.find_by_id(db, produto_id)
    
    if produto is None:
        raise HTTPException(404, "Produto não encontrado.")
    
    fornecedor = await FornecedorRepository.find_by_id(db, data.fornecedor_id)
    
    if fornecedor is None:
        raise HTTPException(404, "Fornecedor não encontrado.")
    
    lote = await EntradaService._resolve_lote(db, produto, data.lote_id, data.novo_lote)
    
    entrada = await EntradaRepository.create(db, **values)
    
    # Cria estoque automaticamente
    await EstoqueRepository.create(
        db,
        entrada_id=entrada.id,
        quantidade=data.quantidade,
        corredor=data.localizacao.corredor,
        prateleira=data.localizacao.prateleira,
        secao=data.localizacao.secao
    )
    
    await db.commit()
```

#### 2. Atualização de Entrada

**Validações:**
- Entrada deve existir
- Estoque associado deve existir (lock pessimista)
- Nova quantidade não pode ser inferior ao total já retirado
- Data de entrada não pode ser posterior a uma saída já registrada
- Fornecedor deve existir se alterado

**Exemplo:**

```python
async def update(db: AsyncSession, entrada_id: int, data: EntradaUpdateSchema):
    entrada = await EntradaRepository.find_by_id(db, entrada_id)
    
    if entrada is None:
        raise HTTPException(404, "Entrada não encontrada.")
    
    # Lock pessimista no estoque
    estoque = await EstoqueRepository.lock_by_entry(db, entrada.id)
    
    if estoque is None:
        raise HTTPException(409, "A entrada não possui estoque associado.")
    
    # Validação de quantidade
    if data.quantidade is not None:
        consumido = entrada.quantidade - estoque.quantidade_atual
        
        if data.quantidade < consumido:
            raise HTTPException(
                400,
                "A quantidade da entrada é inferior ao total já retirado do estoque."
            )
        
        estoque.quantidade_atual = data.quantidade - consumido
    
    # Validação de data
    if data.data_entrada is not None:
        primeira_data = await EntradaRepository.get_first_exit_date(db, entrada.id)
        
        if primeira_data is not None and data.data_entrada > primeira_data:
            raise HTTPException(
                400,
                "A data de entrada não pode ser posterior a uma saída já registrada."
            )
```

#### 3. Constraints de Banco

```python
CheckConstraint("quantidade > 0", name="ck_entrada_quantidade")
CheckConstraint("preco_custo_unitario >= 0", name="ck_entrada_preco_custo")
```

#### 4. Índices de Performance

```python
Index("idx_entrada_id_lote", "id_lote")
Index("idx_entrada_id_fornecedor", "id_fornecedor")
Index("idx_entrada_data_entrada", "data_entrada")
Index("idx_entrada_fornecedor_data", "id_fornecedor", "data_entrada")
Index("idx_entrada_id_funcionario", "id_funcionario")
Index("idx_entrada_tipo_data", "tipo_entrada", "data_entrada")
```

#### 5. Auditoria

Toda entrada registra:
- Data de entrada (automática ou manual)
- Usuário responsável (`usuario_id`)
- Tipo de entrada
- Observações

---

## Estoques

### Definição

Estoque representa a quantidade física de produtos armazenados em uma localização específica (corredor, prateleira, seção), associada a uma entrada.

### Regras

#### 1. Criação de Estoque

**Automaticamente criado com entrada:**
- Quantidade inicial = quantidade da entrada
- Localização definida na entrada
- Associado à entrada via `entrada_id`

**Exemplo:**

```python
estoque = await EstoqueRepository.create(
    db,
    entrada_id=entrada.id,
    quantidade=data.quantidade,
    corredor=data.localizacao.corredor,
    prateleira=data.localizacao.prateleira,
    secao=data.localizacao.secao
)
```

#### 2. Atualização de Quantidade

**Regras:**
- Quantidade nunca pode ser negativa (constraint de banco)
- Atualizações são feitas via saídas (decremento) ou atualização de entrada
- Lock pessimista (`FOR UPDATE`) em operações críticas

**Exemplo de Lock:**

```python
async def lock_by_id(db: AsyncSession, estoque_id: int):
    result = await db.execute(
        select(EstoqueModel)
        .where(EstoqueModel.id == estoque_id)
        .with_for_update()  # FOR UPDATE
    )
    return result.scalars().unique().one_or_none()
```

#### 3. Constraints de Banco

```python
CheckConstraint("quantidade_atual >= 0", name="ck_estoque_quantidade")
```

#### 4. Localização

Cada estoque possui localização física:
- **Corredor:** Identificação do corredor no armazém
- **Prateleira:** Identificação da prateleira
- **Seção:** Identificação da seção

#### 5. Consulta de Contexto

Para obter informações completas do estoque (produto, lote, preço):

```python
async def get_context(db: AsyncSession, estoque_id: int):
    query = select(
        EstoqueModel.id.label("estoque_id"),
        EntradaModel.id.label("entrada_id"),
        EntradaModel.data_entrada.label("data_entrada"),
        LoteModel.id.label("lote_id"),
        LoteModel.numero.label("lote_numero"),
        ProdutoModel.id.label("produto_id"),
        ProdutoModel.nome.label("produto_nome"),
        ProdutoModel.preco_venda_atual.label("preco_venda_atual")
    ).join(EntradaModel, EntradaModel.id == EstoqueModel.entrada_id)
     .join(LoteModel, LoteModel.id == EntradaModel.lote_id)
     .join(ProdutoModel, ProdutoModel.id == LoteModel.produto_id)
     .where(EstoqueModel.id == estoque_id)
    
    result = await db.execute(query)
    return result.mappings().one_or_none()
```

#### 6. Listagem com Filtros

**Filtros disponíveis:**
- Busca por texto (nome produto, número lote, localização)
- Filtro por produto
- Filtro por lote
- Apenas com saldo (`somente_com_saldo`)

**Exemplo:**

```python
if somente_com_saldo:
    conditions.append(EstoqueModel.quantidade_atual > 0)
```

---

## Saídas

### Definição

Saída representa a retirada de produtos do estoque, podendo ser venda, perda, avaria, vencimento ou recall.

### Regras

#### 1. Tipos de Saída

```python
class TipoSaidaEnum(str, Enum):
    VENDA = "VENDA"        # Venda comercial
    PERDA = "PERDA"        # Perda não identificada
    AVARIA = "AVARIA"      # Produto danificado
    VENCIMENTO = "VENCIMENTO"  # Produto vencido
    RECALL = "RECALL"      # Recall do fabricante
```

#### 2. Criação de Saída

**Validações:**
- Estoque deve existir (lock pessimista)
- Estoque deve pertencer ao produto informado
- Quantidade não pode exceder estoque disponível
- Data de saída não pode ser anterior à data de entrada
- Preço de venda obrigatório apenas para tipo VENDA
- Preço de venda usa preço atual do produto se não informado

**Exemplo:**

```python
async def create(db: AsyncSession, *, produto_id: int, data, current_user: UsuarioModel):
    # Lock pessimista
    estoque = await EstoqueRepository.lock_by_id(db, data.estoque_id)
    
    if estoque is None:
        raise HTTPException(404, "Estoque não encontrado.")
    
    contexto = await EstoqueRepository.get_context(db, estoque.id)
    
    if contexto["produto_id"] != produto_id:
        raise HTTPException(409, "O estoque selecionado não pertence ao produto.")
    
    # Validação de quantidade
    if data.quantidade > estoque.quantidade_atual:
        raise HTTPException(
            409,
            f"Estoque insuficiente. Disponível: {estoque.quantidade_atual}."
        )
    
    # Validação de data
    if data.data_saida is not None and data.data_saida < contexto["data_entrada"]:
        raise HTTPException(422, "A saída não pode ocorrer antes da entrada.")
    
    # Validação de preço
    if data.tipo_saida == TipoSaidaEnum.VENDA:
        preco = data.preco_venda_unitario
        
        if preco is None:
            preco = contexto["preco_venda_atual"]
    else:
        if data.preco_venda_unitario is not None:
            raise HTTPException(422, "Somente saídas do tipo VENDA podem possuir preço.")
        
        preco = None
    
    # Decrementa estoque
    estoque.quantidade_atual -= data.quantidade
    
    saida = await SaidaRepository.create(db, **values)
    
    await db.commit()
```

#### 3. Atualização de Saída

**Validações:**
- Saída deve existir
- Estoque associado deve existir (lock pessimista)
- Aumento de quantidade deve ter estoque disponível
- Diminuição de quantidade restaura estoque
- Data não pode ser anterior à entrada
- Preço obrigatório apenas para VENDA

**Exemplo:**

```python
async def update(db: AsyncSession, saida_id: int, data: SaidaUpdateSchema):
    saida = await SaidaRepository.find_by_id(db, saida_id)
    
    # Lock pessimista
    estoque = await EstoqueRepository.lock_by_id(db, saida.estoque_id)
    
    nova_quantidade = (data.quantidade if data.quantidade is not None else saida.quantidade)
    diferenca = (nova_quantidade - saida.quantidade)
    
    # Aumento de quantidade
    if diferenca > 0:
        if diferenca > estoque.quantidade_atual:
            raise HTTPException(409, "Estoque insuficiente para aumentar a saída.")
        
        estoque.quantidade_atual -= diferenca
    
    # Diminuição de quantidade
    elif diferenca < 0:
        estoque.quantidade_atual += abs(diferenca)
    
    # Validação de tipo e preço
    tipo_final = (data.tipo_saida if data.tipo_saida is not None else saida.tipo_saida)
    
    if tipo_final == TipoSaidaEnum.VENDA:
        # Lógica de preço para venda
        ...
    else:
        if data.preco_venda_unitario is not None:
            raise HTTPException(422, "Somente saídas do tipo VENDA podem possuir preço.")
        
        preco_final = None
```

#### 4. Constraints de Banco

```python
CheckConstraint("quantidade > 0", name="ck_saida_quantidade")

CheckConstraint(
    "(tipo_saida = 'VENDA' AND preco_venda_unitario IS NOT NULL) OR "
    "(tipo_saida <> 'VENDA' AND preco_venda_unitario IS NULL)",
    name="ck_saida_preco"
)
```

#### 5. Índices de Performance

```python
Index("idx_saida_id_estoque", "id_estoque")
Index("idx_saida_data_saida", "data_saida")
Index("idx_saida_tipo_data", "tipo_saida", "data_saida")
Index("idx_saida_id_funcionario", "id_funcionario")
```

#### 6. Auditoria

Toda saída registra:
- Data de saída (automática ou manual)
- Usuário responsável (`usuario_id`)
- Tipo de saída
- Preço de venda (se aplicável)
- Quantidade

---

## Auditoria e Histórico

### Definição

Auditoria é o registro de todas as operações realizadas no sistema, permitindo rastreamento completo de movimentações.

### Regras

#### 1. Rastreamento de Usuário

Toda operação de entrada e saída registra o usuário responsável:

```python
values = {
    ...
    "usuario_id": current_user.id,
}
```

#### 2. Timestamps Automáticos

**Entradas:**
- `data_entrada`: Padrão `CURRENT_TIMESTAMP` se não informado

**Saídas:**
- `data_saida`: Padrão `func.current_timestamp()` se não informado

**Produtos:**
- `data_cadastro`: Padrão `func.current_timestamp()`

#### 3. Histórico de Movimentações

O sistema permite consultar o histórico através de:

**Entradas por período:**
```python
Index("idx_entrada_data_entrada", "data_entrada")
Index("idx_entrada_fornecedor_data", "id_fornecedor", "data_entrada")
```

**Saídas por período:**
```python
Index("idx_saida_data_saida", "data_saida")
Index("idx_saida_tipo_data", "tipo_saida", "data_saida")
```

**Por usuário:**
```python
Index("idx_entrada_id_funcionario", "id_funcionario")
Index("idx_saida_id_funcionario", "id_funcionario")
```

#### 4. Integridade Temporal

**Regra de consistência:**
- Saída não pode ocorrer antes da entrada associada
- Atualização de entrada não pode ter data posterior a saída já registrada

**Exemplo:**

```python
# Na criação de saída
if data.data_saida is not None and data.data_saida < contexto["data_entrada"]:
    raise HTTPException(422, "A saída não pode ocorrer antes da entrada.")

# Na atualização de entrada
if data.data_entrada is not None:
    primeira_data = await EntradaRepository.get_first_exit_date(db, entrada.id)
    
    if primeira_data is not None and data.data_entrada > primeira_data:
        raise HTTPException(400, "A data de entrada não pode ser posterior a uma saída já registrada.")
```

#### 5. Lock Pessimista para Consistência

Operações críticas usam `FOR UPDATE` para evitar race conditions:

```python
# Em saídas
estoque = await EstoqueRepository.lock_by_id(db, data.estoque_id)

# Em atualizações de entrada
estoque = await EstoqueRepository.lock_by_entry(db, entrada.id)

# Em atualizações de saída
estoque = await EstoqueRepository.lock_by_id(db, saida.estoque_id)
```

#### 6. Transações Atômicas

Todas as operações usam transações com rollback em caso de erro:

```python
try:
    # Operações
    await db.commit()
except HTTPException:
    await db.rollback()
    raise
except IntegrityError:
    await db.rollback()
    raise HTTPException(409, "Violação de integridade.")
except Exception:
    await db.rollback()
    raise
```

#### 7. Observações

**Entradas:**
- Campo `observacao` permite registrar informações adicionais
- Útil para notas sobre condições de recebimento, problemas, etc.

**Saídas:**
- Tipo de saída já indica motivo (PERDA, AVARIA, VENCIMENTO, RECALL)
- Observações podem ser adicionadas via extensão futura

---

## Fluxos de Negócio

### Fluxo 1: Entrada de Produtos

```
1. Usuário cria entrada para um produto
   ↓
2. Sistema valida produto e fornecedor
   ↓
3. Sistema resolve lote (existente ou novo)
   ↓
4. Se produto perecível, valida data de validade
   ↓
5. Sistema cria entrada
   ↓
6. Sistema cria estoque automaticamente
   ↓
7. Sistema registra usuário responsável
   ↓
8. Sistema commita transação
```

### Fluxo 2: Saída de Produtos

```
1. Seleciona estoque para saída
   ↓
2. Sistema locka estoque (FOR UPDATE)
   ↓
3. Sistema valida estoque pertence ao produto
   ↓
4. Sistema valida quantidade disponível
   ↓
5. Sistema valida data não é anterior à entrada
   ↓
6. Sistema define preço (VENDA usa preço atual)
   ↓
7. Sistema decrementa quantidade do estoque
   ↓
8. Sistema cria saída
   ↓
9. Sistema registra usuário responsável
   ↓
10. Sistema commita transação
```

### Fluxo 3: Atualização de Entrada

```
1. Sistema busca entrada
   ↓
2. Sistema locka estoque associado (FOR UPDATE)
   ↓
3. Se quantidade alterada, calcula consumido
   ↓
4. Valida nova quantidade >= consumido
   ↓
5. Atualiza estoque se necessário
   ↓
6. Valida data não posterior a saídas existentes
   ↓
7. Sistema commita transação
```

---

## Validações Cruzadas

### 1. Produto ↔ Lote

- Lote deve pertencer ao produto
- Número de lote único por produto
- Perecibilidade obriga data de validade

### 2. Entrada ↔ Estoque

- Cada entrada cria exatamente um estoque
- Atualização de entrada afeta estoque
- Lock pessimista em atualizações

### 3. Estoque ↔ Saída

- Saída decrementa estoque
- Validação de quantidade disponível
- Lock pessimista em operações

### 4. Lote ↔ Produto ↔ Estoque

- Estoque → Entrada → Lote → Produto
- Contexto completo obtido via joins
- Validação de pertencimento em todas as operações

---

## Considerações de Performance

### 1. Índices Estratégicos

Índices criados para otimizar consultas comuns:
- Busca por data de entrada/saída
- Busca por fornecedor
- Busca por usuário
- Busca por tipo de movimentação
- Busca por validade de lote

### 2. Eager Loading

Consultas detalhadas usam joins para evitar N+1:

```python
query = select(...).join(EntradaModel, ...).join(LoteModel, ...).join(ProdutoModel, ...)
```

### 3. Lock Pessimista

Usado apenas em operações críticas de escrita para evitar bloqueios desnecessários em leituras.

### 4. Paginação

Todas as listagens suportam paginação para evitar sobrecarga de memória.

---

## Segurança

### 1. Autenticação

Todas as operações exigem autenticação via JWT.

### 2. Autorização

Usuário é registrado em todas as operações para auditoria.

### 3. Validação de Dados

Validações em múltiplas camadas:
- Pydantic schemas (estrutura)
- Services (regras de negócio)
- Database constraints (integridade)

---

## Tratamento de Erros

### Códigos de Status

- **400:** Bad Request - Validação de dados
- **404:** Not Found - Recurso não encontrado
- **409:** Conflict - Violação de unicidade ou integridade
- **422:** Unprocessable Entity - Regra de negócio violada

### Rollback Automático

Todas as exceções causam rollback da transação para manter consistência.
