# Arquitetura do Frontend

Este documento descreve a organizacao do frontend do Desafio FullStack Norven, construido com Vue 3, TypeScript, Vite, Vue Router, Pinia e Vuetify.

## Visao geral

A aplicacao segue uma organizacao por responsabilidade:

```
Interacao do usuario
        |
        v
Views e componentes Vue
        |
        v
Services de dominio
        |
        v
apiRequest
        |
        v
API REST do backend

Estado transversal: Pinia (auth)
Navegacao: Vue Router
UI: Vuetify
```

## Estrutura

### `src/views/`

Contem as telas associadas as rotas da aplicacao:

- `LoginView.vue`: entrada no sistema.
- `InicioView.vue`: pagina inicial autenticada.
- `funcionarios/`: listagem, detalhe e formulario de funcionarios.
- `fornecedores/`: listagem, detalhe e formulario de fornecedores.
- `produtos/`: listagem, detalhe e formulario de produtos.
- `transacoes/`: historico de movimentacoes.

As views coordenam carregamento, estado local da tela, validacao de formulario e navegacao. Requisicoes HTTP devem ser delegadas aos services.

### `src/components/`

Contem componentes reutilizaveis de apresentacao e interacao. Os componentes de layout principais sao:

- `AppHeader.vue`: cabecalho e acoes globais.
- `AppSidebar.vue`: navegacao principal.
- `AppDataTable.vue`: tabela com carregamento, paginacao e menu de acoes.

### `src/services/`

Cada service encapsula os endpoints de um contexto do sistema, como produtos, fornecedores, funcionarios, lotes, estoque e transacoes. Os services tipam os payloads e respostas e utilizam `apiRequest` como ponto unico de comunicacao.

### `src/stores/`

O store `auth` do Pinia centraliza token, usuario autenticado, login, carregamento do usuario atual e logout. Estado especifico de uma tela permanece na propria view.

### `src/types/`

Define os contratos TypeScript usados por views, stores e services. Alteracoes na resposta da API devem ser refletidas nesses tipos antes de serem consumidas pela interface.

### `src/router/`

Define as rotas, os layouts e o guard global de autenticacao. As telas autenticadas sao filhas de `AppLayout`; a tela de login usa `AuthLayout`.

## Fluxo de uma operacao

1. A view coleta filtros ou dados do formulario.
2. A view chama o service do dominio.
3. O service monta query string ou payload JSON.
4. `apiRequest` inclui o token salvo e executa `fetch`.
5. O service devolve uma resposta tipada ou propaga `ApiError`.
6. A view atualiza sua lista, detalhe, mensagens ou navegacao.

## Convencoes

- Usar aliases `@/` para imports de `src`.
- Manter chamadas HTTP nos services, nao diretamente nos templates.
- Reutilizar `AppDataTable` para listagens paginadas.
- Usar os componentes Vuetify existentes para manter consistencia visual.
- Manter tipos de request e response proximos do dominio correspondente.
