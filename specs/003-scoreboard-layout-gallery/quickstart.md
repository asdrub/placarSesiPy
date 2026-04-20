# Quickstart: Galeria de Layouts de Placar

## Objetivo

Validar localmente que o painel administrativo passa a exigir a escolha de um layout antes do setup basico e que a escolha permanece associada a partida durante a operacao.

## Pre-requisitos

1. Ambiente virtual configurado.
2. Dependencias instaladas em `.python_packages/lib/site-packages`.
3. `ADMIN_PASSWORD` configurada em `local.settings.json`.
4. Azurite em execucao se o storage local estiver configurado com `UseDevelopmentStorage=true`.

## Execucao local

1. Ative o ambiente virtual.
2. Inicie a Function App:
   ```bash
   PYTHONPATH="$PWD/.python_packages/lib/site-packages:$PYTHONPATH" func start
   ```
3. Abra o painel em `http://localhost:7071/api/control`.

## Fluxo de validacao principal

1. Faça login com a senha administrativa configurada.
2. Confirme que a primeira etapa apos login e uma galeria de layouts e que os formularios basicos ainda nao estao liberados.
3. Tente prosseguir sem escolher um layout e verifique que o painel bloqueia o avanço com orientacao clara.
4. Escolha um layout valido e confirme que o painel avanca para o setup atual da partida.
5. Escolha mandante e visitante, crie a partida e confirme que o layout selecionado permanece identificado no painel.
6. Abra o overlay publico da partida e verifique que ele usa o layout correspondente a selecao feita.
7. Coloque a partida em operacao normal e confirme que o comportamento de ocultar/reabrir o sidebar continua igual ao fluxo atual.

## Validacoes complementares

1. Recarregue a pagina antes de criar a partida e verifique o comportamento esperado da escolha de layout.
2. Carregue uma partida antiga sem `layoutId` e confirme que painel e overlay permanecem legiveis com fallback para o layout padrao.
3. Tente alterar o layout apos a partida sair de `draft` e confirme que a alteracao e bloqueada.

## Resultado esperado

- O operador sempre escolhe um layout antes do setup.
- O setup basico mantem a mesma operacao atual apos a escolha.
- O layout fica persistido no estado da partida.
- O sidebar continua recolhendo e reabrindo como antes.
