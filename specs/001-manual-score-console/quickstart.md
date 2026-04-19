# Quickstart: Console Manual de Placar

## Objective

Validar localmente o fluxo principal da feature: autenticar no painel, criar uma partida, operar pontos/faltas/periodo/cronometro e confirmar que o overlay publico acompanha o estado em ate 2 segundos.

## Prerequisites

- Python 3.11 ativo no ambiente local.
- Azure Functions Core Tools instalado.
- Dependencias instaladas a partir de `requirements.txt`.
- Configuracao local da senha administrativa e da persistencia de blobs no `local.settings.json`.

## Local Setup

1. Criar e ativar o ambiente virtual.
2. Instalar dependencias com `pip install -r requirements.txt`.
3. Instalar as dependencias tambem em `.python_packages/lib/site-packages` para o Core Tools local:
   - `python -m pip install --target=.python_packages/lib/site-packages -r requirements.txt`
4. Copiar `local.settings.example.json` para `local.settings.json`.
5. Configurar as chaves locais necessarias:
   - `ADMIN_PASSWORD`
   - `AzureWebJobsStorage`
   - `SCOREBOARD_STATE_CONTAINER` com valor padrao, por exemplo `games`
6. Iniciar o Azurite se estiver usando `UseDevelopmentStorage=true`.
7. Iniciar a Function App com `PYTHONPATH="$PWD/.python_packages/lib/site-packages:$PYTHONPATH" func start`.

## Manual Validation Flow

1. Abrir o painel administrativo em `http://localhost:7071/api/control`.
2. Informar a senha unica configurada.
3. Criar uma partida com nome e logo dos dois times.
4. Confirmar que a resposta de criacao retorna `gameId` e URL publica do overlay.
5. Abrir a URL publica do overlay em outra aba ou navegador.
6. No painel, executar as operacoes abaixo e confirmar reflexo no overlay em ate 2 segundos:
   - iniciar a partida e confirmar que o painel lateral de configuracao e recolhido automaticamente
   - usar o botao hamburguer para reabrir a configuracao da partida e confirmar que ela permanece visivel ate nova acao manual
   - confirmar que os campos de logo aparecem apenas na configuracao da partida, nao no painel principal de controle
   - adicionar 1, 2 e 3 pontos para cada time
   - editar manualmente score e faltas
   - alternar entre os periodos 1, 2, 3 e 4
   - iniciar, pausar e retomar o cronometro regressivo a partir de `10:00`
   - confirmar que a troca de periodo reinicia o cronometro para `10:00`
   - confirmar que o cronometro para automaticamente em `00:00`
   - confirmar que o proximo periodo so e liberado depois que o periodo atual zera
   - ajustar manualmente o cronometro do periodo corrente e confirmar que a contagem pode continuar no mesmo quarto
   - alternar o switch de modo escuro no topo e confirmar que o tema escolhido persiste apos recarregar a pagina
7. Recarregar painel e overlay e confirmar que o estado do jogo permanece consistente.

## Suggested Automated Coverage

- Testes unitarios para validacao de score, faltas, periodo e cronometro.
- Testes unitarios para serializacao/deserializacao do snapshot de jogo.
- Teste de integracao para criar partida, atualizar estado e consultar o JSON publico.

## Exit Criteria

- Painel autenticado acessivel localmente.
- Overlay publico funcional por URL unica de jogo.
- Persistencia de estado validada apos recarga de pagina.
- Atualizacoes refletidas no overlay dentro do alvo de 2 segundos.