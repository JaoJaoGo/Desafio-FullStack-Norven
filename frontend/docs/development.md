# Desenvolvimento do Frontend

## Requisitos

- Node.js `^22.18.0` ou `>=24.12.0`.
- npm.
- Backend disponivel em uma URL compativel com `VITE_API_BASE_URL`.

## Configuracao inicial

Na pasta `frontend`:

```sh
npm install
```

Copie `.env.example` para `.env` e ajuste a URL da API:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Variaveis com prefixo `VITE_` sao expostas ao bundle do navegador. Nunca coloque segredos do backend nesse arquivo.

## Comandos

### Desenvolvimento

```sh
npm run dev
```

Inicia o servidor Vite com recarregamento automatico.

### Type-check e build

```sh
npm run type-check
npm run build
```

`build` executa o type-check e gera o bundle de producao.

### Lint

```sh
npm run lint
npm run lint:fix
```

Use `lint:fix` apenas quando aceitar as correcoes automaticas propostas pelo ESLint.

### Preview

```sh
npm run preview
```

Serve localmente o bundle ja gerado.

## Checklist de alteracao

1. Atualizar tipos quando o contrato da API mudar.
2. Manter requisicoes no service correspondente.
3. Registrar novas rotas e itens de navegacao.
4. Cobrir estados de carregamento, vazio, sucesso e erro.
5. Executar `npm run type-check`, `npm run lint` e `npm run build`.
6. Atualizar esta documentacao quando uma convencao ou fluxo mudar.
