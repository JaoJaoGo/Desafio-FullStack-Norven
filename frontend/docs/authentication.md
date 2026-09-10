# Autenticacao no Frontend

Este documento descreve como o frontend realiza login, conserva a sessao e restringe a navegacao.

## Componentes envolvidos

- `src/views/LoginView.vue`: coleta e envia as credenciais.
- `src/services/authService.ts`: chama `/auth/login` e `/auth/me`.
- `src/stores/auth.ts`: mantem token e usuario no Pinia.
- `src/services/api.ts`: injeta o header Bearer e remove token apos resposta `401`.
- `src/router/index.ts`: aplica os guards `requiresAuth` e `guestOnly`.

## Fluxo de login

1. O usuario informa e-mail e senha na tela de login.
2. `authService.login` envia `application/x-www-form-urlencoded` para `POST /auth/login`.
3. O store salva `access_token` no estado e em `localStorage`, usando a chave `norven_access_token`.
4. O store chama `GET /auth/me` para carregar o usuario autenticado.
5. Em caso de sucesso, a aplicacao navega para a area protegida.
6. Se `/auth/me` falhar, o store executa logout e remove o token.

## Persistencia da sessao

O token e recuperado do `localStorage` quando o store e criado. O usuario autenticado nao e persistido: ele e carregado novamente por `/auth/me` quando necessario.

O logout limpa:

- `auth.token`;
- `auth.user`;
- `localStorage[norven_access_token]`.

## Protecao de rotas

Rotas filhas de `AppLayout` usam `meta.requiresAuth`. Quando o usuario nao esta autenticado, o guard redireciona para `login` e preserva a URL original em `query.redirect`.

A rota de login usa `meta.guestOnly`. Usuarios autenticados sao redirecionados para `inicio`.

Antes de concluir a navegacao, o guard chama `ensureCurrentUser`. Uma falha nessa verificacao invalida a sessao local e redireciona para o login.

## Expiracao ou token invalido

Quando qualquer requisicao retorna `401`, `apiRequest` remove o token do `localStorage` e lanca `ApiError`. A proxima verificacao de rota exigira novo login.

O frontend nao implementa refresh token. A renovacao ou alteracao da politica de expiracao deve ser tratada em conjunto com o contrato do backend.

## Seguranca

- Nao registrar tokens ou senhas em logs.
- Manter `VITE_API_BASE_URL` configurada para o ambiente correto.
- A protecao definitiva deve permanecer no backend; guards do frontend controlam apenas navegacao e experiencia de uso.
