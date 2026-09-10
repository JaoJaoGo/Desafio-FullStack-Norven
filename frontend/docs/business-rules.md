# Regras de Interface

Este documento registra comportamentos implementados no frontend. As regras de dominio e de persistencia continuam pertencendo ao backend.

## Navegacao

- A area autenticada usa `AppLayout`.
- A navegacao principal esta no `AppSidebar`.
- As entradas atuais sao Inicio, Funcionarios, Fornecedores, Produtos e Historico.
- Rotas desconhecidas redirecionam para `/`.
- Acoes de voltar, editar e criar devem usar os nomes de rota registrados no Vue Router.

## Conta do usuario autenticado

- O menu do cabecalho oferece a acao `Editar conta`.
- A acao abre a rota `account-edit` (`/minha-conta/editar`).
- O formulario permite atualizar nome, senha, contato e endereco da propria conta.
- E-mail e nivel de acesso nao sao editaveis nesse modo.
- Apos o salvamento, o usuario autenticado e recarregado no store e a aplicacao retorna para `inicio`.
- A edicao de outro funcionario continua usando a rota administrativa `funcionario-edit`.

## Listagens

As listagens usam carregamento assincrono e paginacao. O componente `AppDataTable`:

- mostra indicador enquanto `loading` esta ativo;
- calcula o total de paginas a partir de `totalItems` e `perPage`;
- exibe o intervalo de itens atual;
- permite tamanhos de pagina 10, 20, 50 e 100;
- suporta acoes por registro;
- fecha o menu de contexto ao clicar fora, redimensionar ou rolar a pagina;
- exibe `Nenhum registro encontrado.` quando nao ha itens, salvo texto personalizado.

Ao alterar filtros, a view deve voltar para a primeira pagina antes de buscar os resultados.

## Formularios

Formularios de criacao e edicao devem:

- diferenciar modo de criacao de modo de edicao pela rota;
- carregar dados relacionados por meio dos services apropriados;
- bloquear ou indicar envio em andamento;
- impedir envio quando os dados locais forem invalidos;
- exibir o erro retornado pela API sem esconder a causa;
- atualizar a tela ou navegar para o detalhe/listagem apos sucesso.

A validacao da interface melhora a experiencia, mas nao substitui as validacoes do backend.

## Produtos e estoque

A interface permite consultar produtos com filtros e exibir o status retornado pela API. A obrigatoriedade de lote, validade, quantidade e demais invariantes de estoque deve ser determinada pelo backend; o frontend apenas coleta, envia e apresenta esses dados.

## Transacoes

A tela de transacoes representa o historico de movimentacoes. Ela e somente uma camada de consulta: a consistencia de entradas, saidas, quantidades e auditoria e responsabilidade do backend.

## Estados de tela

Toda tela que carrega dados deve considerar pelo menos:

- carregamento inicial;
- carregamento de uma nova busca;
- resultado vazio;
- erro de comunicacao ou validacao;
- sucesso apos criacao, edicao ou exclusao, quando aplicavel.

Mensagens devem ser acionaveis e nao devem expor detalhes internos da API.
