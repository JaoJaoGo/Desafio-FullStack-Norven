# Integracao com a API

O frontend se comunica com a API REST por meio de `src/services/api.ts`. Os services de dominio nao devem duplicar a configuracao de autenticacao ou o tratamento basico de erros.

## URL base

A URL e definida por `VITE_API_BASE_URL`. Quando a variavel nao existe, o cliente usa:

```text
http://localhost:8000/api/v1
```

Exemplo de configuracao local:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Cliente HTTP

`apiRequest<T>(endpoint, options)`:

1. Cria os headers a partir das opcoes recebidas.
2. Le o token de `localStorage`.
3. Adiciona `Authorization: Bearer <token>` quando houver token.
4. Executa `fetch` contra a URL base.
5. Retorna `undefined` para respostas `204`.
6. Converte respostas bem-sucedidas em JSON.
7. Para respostas de erro, tenta ler `detail` e lanca `ApiError` com status e mensagem.

## Formatos usados

### JSON

Operacoes de criacao e atualizacao enviam JSON e devem definir:

```http
Content-Type: application/json
```

```ts
body: JSON.stringify(payload)
```

### Login

O endpoint de login segue o contrato OAuth2 e recebe formulario codificado:

```http
Content-Type: application/x-www-form-urlencoded
```

O campo `username` recebe o e-mail informado pelo usuario.

### Consultas paginadas

Listagens montam filtros com `URLSearchParams`. Os parametros usados pelo frontend incluem, conforme o dominio:

- `page`;
- `per_page`;
- filtros de texto;
- filtros de status;
- intervalos numericos.

Os services devem omitir filtros vazios e manter a codificacao feita por `URLSearchParams`.

## Tratamento nas views

As views devem:

- controlar um estado de carregamento durante a requisicao;
- exibir uma mensagem compreensivel para `ApiError`;
- tratar `404` conforme o contexto, geralmente retornando para a listagem;
- atualizar a lista ou detalhe depois de uma operacao bem-sucedida;
- evitar requisicoes duplicadas quando a tela ja estiver carregando.

Erros de validacao de dominio continuam sendo definidos pelo backend e chegam no campo `detail`.

## Conta do usuario autenticado

O menu do `AppHeader` disponibiliza a acao **Editar conta**, que navega para `minha-conta/editar`. A tela reutiliza o formulario de funcionarios em um modo especifico de conta e chama `funcionarioService.updateCurrent` para enviar:

```http
PATCH /api/v1/usuarios/me
```

Nesse modo, o frontend envia somente nome, senha, contato e endereco. Depois de uma atualizacao bem-sucedida, o store de autenticacao recarrega o usuario atual e a aplicacao retorna para a pagina inicial. A edicao administrativa de funcionarios usa o endpoint separado `/usuarios/{id}`.

## Adicao de um novo dominio

1. Criar ou atualizar os tipos em `src/types/`.
2. Criar um service em `src/services/` usando `apiRequest`.
3. Implementar a view e seus estados de carregamento/erro.
4. Registrar a rota em `src/router/index.ts`.
5. Adicionar a entrada de navegacao em `AppSidebar.vue` quando a funcionalidade for acessivel pelo menu.
