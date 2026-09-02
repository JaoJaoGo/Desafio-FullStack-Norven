# Documentação de Autenticação

Este documento descreve o sistema de autenticação do backend, incluindo OAuth2, JWT, bcrypt, fluxo de login e gerenciamento de usuários autenticados.

## Índice

- [Visão Geral](#visão-geral)
- [Tecnologias](#tecnologias)
- [Configurações](#configurações)
- [Fluxo de Login](#fluxo-de-login)
- [Estrutura do JWT](#estrutura-do-jwt)
- [Segurança de Senhas](#segurança-de-senhas)
- [Dependência de Autenticação](#dependência-de-autenticação)
- [Proteção de Rotas](#proteção-de-rotas)
- [Boas Práticas](#boas-práticas)

---

## Visão Geral

O sistema de autenticação utiliza uma combinação de:

- **OAuth2:** Padrão de autorização para fluxo de login
- **JWT (JSON Web Tokens):** Tokens stateless para autenticação
- **Bcrypt:** Hash de senhas para segurança

**Características:**
- Stateless (não armazena sessões no servidor)
- Tokens com expiração configurável
- Senhas hasheadas com bcrypt
- Integração nativa com FastAPI

---

## Tecnologias

### 1. OAuth2

**Implementação:** FastAPI `OAuth2PasswordBearer`

**Propósito:**
- Define o fluxo de autenticação padrão
- Especifica o endpoint de token (`/api/v1/auth/login`)
- Extrai o token do header `Authorization: Bearer <token>`

**Configuração:**

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)
```

**Endpoint de Token:**
- URL: `/api/v1/auth/login`
- Método: POST
- Content-Type: `application/x-www-form-urlencoded`

---

### 2. JWT (JSON Web Tokens)

**Implementação:** `python-jose` com algoritmo HS256

**Propósito:**
- Geração de tokens de acesso
- Codificação de informações do usuário no token
- Validação de expiração

**Configuração:**

```python
from jose import jwt

jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
```

**Características:**
- Assimétrico: Usa chave secreta para assinar
- Stateless: Informações codificadas no próprio token
- Expirável: Tempo de vida configurável

---

### 3. Bcrypt

**Implementação:** `bcrypt` library

**Propósito:**
- Hash de senhas com salt automático
- Verificação segura de senhas
- Proteção contra rainbow tables

**Configuração:**

```python
import bcrypt

# Hash
salt = bcrypt.gensalt()
hash_bytes = bcrypt.hashpw(password_bytes, salt)

# Verificação
bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
```

**Características:**
- Salt automático (cada hash é único)
- Slow hashing (proteção contra brute force)
- Adaptável (fator de custo configurável)

---

## Configurações

### Variáveis de Ambiente

**Localização:** `.env` ou `settings.py`

**Configurações Atuais:**

```python
class Settings(BaseSettings):
    # JWT
    JWT_SECRET: str = "BzyIwri23qkrmV4BU2QS7LfeUe55QwutuakEAB-K9gQ"
    ALGORITHM: str = "HS256"
    
    # Expiração do token (7 dias)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # Senha do administrador
    PRIMARY_ADMIN_PASSWORD: str
```

### JWT_SECRET

**Propósito:** Chave secreta para assinar tokens JWT

**Segurança:**
- Deve ser mantida em segredo
- Deve ser gerada aleatoriamente em produção
- Não deve ser commitada no repositório

**Geração de Chave Segura:**

```python
import secrets
token = secrets.token_urlsafe(32)
```

### ACCESS_TOKEN_EXPIRE_MINUTES

**Valor Atual:** 10080 minutos (7 dias)

**Configuração:**
```python
60 * 24 * 7  # 60 minutos * 24 horas * 7 dias
```

**Considerações:**
- 7 dias é um período relativamente longo
- Pode ser reduzido para maior segurança
- Requer implementação de refresh token para períodos curtos

### ALGORITHM

**Valor:** `HS256` (HMAC SHA-256)

**Propósito:** Algoritmo de assinatura do JWT

**Alternativas:**
- `HS256`: Simétrico (mesma chave para assinar e verificar)
- `RS256`: Assimétrico (chave pública/privada)

**Decisão:** HS256 é suficiente para a maioria dos casos

---

## Fluxo de Login

### Diagrama de Sequência

```
Cliente                    FastAPI                  Banco de Dados
   │                          │                          │
   │ POST /auth/login         │                          │
   │ (email, password)        │                          │
   ├─────────────────────────>│                          │
   │                          │                          │
   │                          │ SELECT usuario           │
   │                          │ WHERE email = ?          │
   │                          ├─────────────────────────>│
   │                          │                          │
   │                          │ usuario (hash senha)    │
   │                          │<─────────────────────────┤
   │                          │                          │
   │                          │ bcrypt.checkpw()         │
   │                          │ (verifica senha)         │
   │                          │                          │
   │                          │ create_access_token()    │
   │                          │ (gera JWT)               │
   │                          │                          │
   │ {access_token,           │                          │
   │  token_type: "bearer"}   │                          │
   │<─────────────────────────┤                          │
   │                          │                          │
```

### Passo a Passo

#### 1. Requisição de Login

**Endpoint:** `POST /api/v1/auth/login`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Body (form-data):**
```
username: usuario@exemplo.com
password: senha123
```

**Código:**

```python
@router.post("/login", response_model=TokenResponseSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_session)
):
    usuario = await authenticate(
        email=form_data.username, 
        password=form_data.password, 
        db=db
    )
    
    if usuario is None:
        raise HTTPException(
            status_code=401, 
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(sub=str(usuario.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

#### 2. Autenticação

**Função:** `authenticate(email, password, db)`

**Processo:**

```python
async def authenticate(email: EmailStr, password: str, db: AsyncSession):
    # Busca usuário por e-mail
    query = select(UsuarioModel).filter(UsuarioModel.email == email)
    result = await session.execute(query)
    usuario = result.scalars().unique().one_or_none()
    
    # Usuário não encontrado
    if not usuario:
        return None
    
    # Verifica senha
    if not verify_password(password, usuario.password):
        return None
    
    return usuario
```

**Validações:**
- Usuário deve existir no banco
- Senha deve corresponder ao hash armazenado

#### 3. Geração do Token

**Função:** `create_access_token(sub)`

**Processo:**

```python
def create_access_token(sub: str) -> str:
    return _create_token(
        tipo_token="access_token",
        tempo_vida=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=sub  # ID do usuário
    )

def _create_token(tipo_token: str, tempo_vida: timedelta, sub: str):
    payload = {}
    
    # Fuso horário de São Paulo
    sp = timezone('America/Sao_Paulo')
    expira = datetime.now(sp) + tempo_vida
    
    payload['type'] = tipo_token
    payload['exp'] = expira
    payload['iat'] = datetime.now(tz=sp)
    payload['sub'] = str(sub)
    
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
```

**Payload do JWT:**
```json
{
  "type": "access_token",
  "exp": "2026-09-09T08:31:00-03:00",
  "iat": "2026-09-02T08:31:00-03:00",
  "sub": "1"
}
```

#### 4. Resposta

**Status:** 200 OK

**Body:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Estrutura do JWT

### Payload (Claims)

**Claims Padrão:**

| Claim | Descrição | Exemplo |
|-------|-----------|---------|
| `sub` | Subject (ID do usuário) | `"1"` |
| `exp` | Expiration (data de expiração) | `"2026-09-09T08:31:00-03:00"` |
| `iat` | Issued At (data de emissão) | `"2026-09-02T08:31:00-03:00"` |

**Claims Customizados:**

| Claim | Descrição | Exemplo |
|-------|-----------|---------|
| `type` | Tipo do token | `"access_token"` |

### Decodificação do Token

**Exemplo de Decodificação:**

```python
from jose import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
payload = jwt.decode(
    token,
    settings.JWT_SECRET,
    algorithms=[settings.ALGORITHM],
    options={"verify_aud": False}
)

# Resultado:
# {
#   "type": "access_token",
#   "exp": 1725863460,
#   "iat": 1725258660,
#   "sub": "1"
# }
```

### Validação do Token

**Verificações Automáticas:**
- Assinatura válida (chave secreta correta)
- Token não expirado (`exp` > data atual)
- Formato correto

**Verificação Manual:**

```python
try:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
except jwt.ExpiredSignatureError:
    raise HTTPException(401, "Token expirado")
except jwt.JWTError:
    raise HTTPException(401, "Token inválido")
```

---

## Segurança de Senhas

### Hash com Bcrypt

**Função:** `get_password_hash(password)`

**Processo:**

```python
def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()  # Salt aleatório
    hash_bytes = bcrypt.hashpw(password_bytes, salt)
    return hash_bytes.decode('utf-8')
```

**Características:**
- Salt gerado automaticamente (cada hash é único)
- Fator de custo padrão (12 rounds)
- Saída em string UTF-8

**Exemplo:**

```python
senha = "senha123"
hash_senha = get_password_hash(senha)
# Resultado: "$2b$12$N9qo8uLOickgx2ZMRZoMy..."
```

### Verificação de Senha

**Função:** `verify_password(password, hashed_password)`

**Processo:**

```python
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )
```

**Características:**
- Compara senha em texto plano com hash
- Extrai salt do hash automaticamente
- Retorna booleano

**Exemplo:**

```python
senha = "senha123"
hash_senha = "$2b$12$N9qo8uLOickgx2ZMRZoMy..."

valido = verify_password(senha, hash_senha)
# Resultado: True

invalido = verify_password("senha_errada", hash_senha)
# Resultado: False
```

### Por Que Bcrypt?

**Vantagens:**
1. **Salt Automático:** Cada hash é único, mesmo para mesma senha
2. **Slow Hashing:** Proteção contra brute force
3. **Adaptável:** Fator de custo pode aumentar com hardware mais potente
4. **Battle-Tested:** Amplamente usado e testado

**Comparação com Outros Métodos:**

| Método | Salt | Slow Hashing | Segurança |
|--------|------|--------------|-----------|
| MD5 | Não | Não | Baixa |
| SHA-256 | Manual | Não | Média |
| Bcrypt | Automático | Sim | Alta |
| Argon2 | Automático | Sim | Muito Alta |

---

## Dependência de Autenticação

### get_current_user

**Função:** `get_current_user(db, token)`

**Propósito:**
- Extrair e validar o token JWT
- Buscar o usuário no banco
- Retornar o usuário autenticado

**Implementação:**

```python
async def get_current_user(
    db: Session = Depends(get_session), 
    token: str = Depends(oauth2_scheme)
) -> UsuarioModel:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Não foi possível autenticar a credencial",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        # Decodifica token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )
        
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Busca usuário no banco
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == int(token_data.username))
        result = await session.execute(query)
        user: UsuarioModel = result.scalars().unique().one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user
```

**Fluxo:**
1. Extrai token do header `Authorization: Bearer <token>`
2. Decodifica e valida o token
3. Extrai `sub` (ID do usuário) do payload
4. Busca usuário no banco de dados
5. Retorna o usuário ou lança exceção

### Uso em Endpoints

**Exemplo:**

```python
from fastapi import Depends
from core.deps import get_current_user
from models.usuario_model import UsuarioModel

@router.get("/me", response_model=UsuarioResponseSchema)
async def get_me(current_user: UsuarioModel = Depends(get_current_user)):
    return current_user

@router.get("/usuarios", dependencies=[Depends(get_current_user)])
async def list_usuarios():
    # Endpoint protegido, mas não precisa do usuário
    ...
```

**Diferenças:**
- `Depends(get_current_user)`: Injeta o usuário no parâmetro
- `dependencies=[Depends(get_current_user)]`: Apenas valida autenticação

---

## Proteção de Rotas

### Rotas Públicas

**Exemplo:** Criação de usuário

```python
@router.post("/", response_model=UsuarioResponseSchema)
async def create_usuario(data: UsuarioCreateSchema, db: AsyncSession = Depends(get_session)):
    return await UsuarioController.create(data, db)
```

**Características:**
- Não exige autenticação
- Acessível a qualquer pessoa
- Usado para cadastro, login, etc.

### Rotas Protegidas

**Exemplo:** Listagem de usuários

```python
@router.get("/", response_model=UsuarioListResponseSchema, dependencies=[Depends(get_current_user)])
async def list_usuarios(
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    ...
```

**Características:**
- Exige token JWT válido
- Apenas usuários autenticados
- Usado para operações sensíveis

### Rotas com Usuário Injetado

**Exemplo:** Perfil do usuário

```python
@router.get("/me", response_model=UsuarioResponseSchema)
async def get_me(current_user: UsuarioModel = Depends(get_current_user)):
    return current_user
```

**Características:**
- Exige autenticação
- Injeta o usuário autenticado
- Usado para operações específicas do usuário

### Erros de Autenticação

**Cenários:**

1. **Token Ausente:**
   - Header `Authorization` não enviado
   - Status: 401 Unauthorized
   - Detalhe: "Não foi possível autenticar a credencial"

2. **Token Inválido:**
   - Token malformado ou assinatura incorreta
   - Status: 401 Unauthorized
   - Detalhe: "Não foi possível autenticar a credencial"

3. **Token Expirado:**
   - Token com `exp` no passado
   - Status: 401 Unauthorized
   - Detalhe: "Não foi possível autenticar a credencial"

4. **Usuário Não Encontrado:**
   - Token válido mas usuário não existe
   - Status: 401 Unauthorized
   - Detalhe: "Não foi possível autenticar a credencial"

---

## Boas Práticas

### 1. Segurança do JWT_SECRET

**Recomendações:**
- Gerar chave aleatória em produção
- Nunca commitar no repositório
- Usar variáveis de ambiente
- Rotacionar chaves periodicamente

**Geração:**

```python
import secrets
jwt_secret = secrets.token_urlsafe(32)
```

### 2. Tempo de Expiração

**Considerações:**
- **Curto (15-30 minutos):** Maior segurança, requer refresh token
- **Médio (1-24 horas):** Equilíbrio entre segurança e UX
- **Longo (7 dias):** Menor segurança, melhor UX

**Atual:** 7 dias (considerado longo)

**Recomendação:** Implementar refresh token para reduzir tempo de expiração

### 3. Armazenamento de Tokens

**Cliente:**
- Armazenar em `localStorage` ou `sessionStorage`
- Enviar no header `Authorization: Bearer <token>`
- Limpar ao fazer logout

**Servidor:**
- Não armazenar tokens (stateless)
- Validar em cada requisição
- Implementar blacklist se necessário

### 4. Revogação de Tokens

**Desafio:** Tokens stateless não podem ser revogados facilmente

**Soluções:**
1. **Blacklist:** Armazenar tokens revogados em Redis
2. **Short Expiration:** Tempo curto + refresh token
3. **Versioning:** Versão do usuário no token, incrementar ao revogar

### 5. Proteção HTTPS

**Obrigatório:**
- Sempre usar HTTPS em produção
- Nunca enviar tokens em HTTP
- Configurar HSTS

### 6. Rate Limiting

**Recomendação:**
- Limitar tentativas de login
- Bloquear após X tentativas falhas
- Implementar CAPTCHA se necessário

### 7. Logs de Autenticação

**Registrar:**
- Tentativas de login (sucesso/falha)
- IPs de origem
- Timestamps
- Usuários envolvidos

**Propósito:**
- Detecção de atividades suspeitas
- Auditoria de segurança
- Forense em caso de incidente

### 8. Senhas Fortes

**Requisitos:**
- Mínimo 8 caracteres
- Letras maiúsculas e minúsculas
- Números
- Caracteres especiais

**Validação (Pydantic):**

```python
from pydantic import field_validator

class UsuarioCreateSchema(BaseModel):
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')
        return v
```

---

## Exemplos de Uso

### Login via cURL

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@norven.com.br&password=senha123"
```

**Resposta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Requisição Autenticada via cURL

```bash
curl -X GET "http://localhost:8000/api/v1/usuarios" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Login via JavaScript (Fetch)

```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'admin@norven.com.br',
    password: 'senha123'
  })
});

const data = await response.json();
const token = data.access_token;

// Armazenar token
localStorage.setItem('access_token', token);
```

### Requisição Autenticada via JavaScript (Fetch)

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/v1/usuarios', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
```

---

## Troubleshooting

### Problema: Token Inválido

**Causas Possíveis:**
- Token malformado
- Assinatura incorreta (JWT_SECRET diferente)
- Token expirado

**Solução:**
- Verificar se token está completo
- Verificar JWT_SECRET no servidor
- Gerar novo token (fazer login novamente)

### Problema: Usuário Não Encontrado

**Causas Possíveis:**
- Usuário deletado após geração do token
- ID do usuário alterado no payload

**Solução:**
- Verificar se usuário existe no banco
- Fazer login novamente para gerar novo token

### Problema: Senha Inválida

**Causas Possíveis:**
- Senha incorreta
- Hash de senha corrompido
- Encoding incorreto

**Solução:**
- Verificar senha digitada
- Resetar senha do usuário
- Verificar encoding UTF-8

### Problema: Token Expirado

**Causas:**
- Tempo de expiração atingido

**Solução:**
- Fazer login novamente
- Aumentar `ACCESS_TOKEN_EXPIRE_MINUTES`
- Implementar refresh token

---

## Melhorias Futuras

### 1. Refresh Token

**Implementar:**
- Token de curta duração (15-30 minutos)
- Refresh token de longa duração (7-30 dias)
- Endpoint para renovar access token

**Benefícios:**
- Maior segurança
- Menor necessidade de login frequente

### 2. Multi-Factor Authentication (MFA)

**Implementar:**
- TOTP (Time-based One-Time Password)
- SMS verification
- Email verification

**Benefícios:**
- Segurança adicional
- Proteção contra roubo de credenciais

### 3. OAuth2 Social

**Implementar:**
- Login com Google
- Login com GitHub
- Login com Microsoft

**Benefícios:**
- Melhor UX
- Menos senhas para gerenciar

### 4. Role-Based Access Control (RBAC)

**Implementar:**
- Permissões granulares por role
- Herança de permissões
- Middleware de autorização

**Benefícios:**
- Controle de acesso mais fino
- Escalabilidade de permissões

### 5. Auditoria de Autenticação

**Implementar:**
- Log de todos os eventos de autenticação
- Detecção de atividades suspeitas
- Alertas de segurança

**Benefícios:**
- Compliance
- Segurança aprimorada
- Forense
