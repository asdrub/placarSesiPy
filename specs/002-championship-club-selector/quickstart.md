# Quickstart: Seletor de Clubes 2026

## Objective

Validar localmente que o setup da partida substitui os campos livres de nome e URL de logo por uma selecao fechada dos clubes oficiais de 2026, preservando a criacao da partida, o painel de controle e o overlay publico.

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
3. Iniciar a criacao de uma nova partida.
4. Confirmar que o setup exibe controles de selecao de clube para mandante e visitante, e nao campos livres de nome ou URL de logo.
5. Confirmar que a lista disponivel contem exatamente estas opcoes:
   - `SESI / Araraquara`
   - `ARAE/ SMEL Catanduva`
   - `Sao Jose Basketball/ Atleta Cidadao`
   - `FEAC Franca Basquete`
   - `A.D. Santo Andre`
6. Selecionar dois clubes distintos e confirmar que a criacao da partida retorna `gameId` e URL publica do overlay.
7. Abrir a URL publica do overlay em outra aba ou navegador.
8. Confirmar que painel principal e overlay exibem os nomes e logos oficiais correspondentes aos clubes escolhidos.
9. Tentar selecionar o mesmo clube para os dois lados e confirmar que a criacao ou atualizacao e bloqueada com orientacao clara.
10. Trocar um dos clubes antes do inicio da partida e confirmar que nome e logo daquele lado mudam juntos para a nova identidade oficial.
11. Recarregar painel e overlay e confirmar que o `clubId` resolvido continua refletido como nome e logo corretos no estado restaurado.
12. Carregar uma partida antiga sem `clubId`, se disponivel, e confirmar que ela continua legivel sem quebra de exibicao.

## Suggested Automated Coverage

- Testes unitarios para validacao do catalogo oficial e unicidade de `clubId`.
- Testes unitarios para criacao de jogo com resolucao de `clubId` para `name` e `logoUrl`.
- Testes unitarios para bloqueio de selecao duplicada do mesmo clube em `home` e `away`.
- Testes de integracao para `POST /api/games` e `PATCH /api/games/{gameId}` usando selecao por clube.
- Teste de compatibilidade para leitura de snapshot legado sem `clubId`.

## Exit Criteria

- O setup da partida nao exibe mais campos livres de nome e URL de logo no fluxo principal.
- A lista de clubes disponivel corresponde exatamente ao catalogo oficial aprovado para 2026.
- A criacao de partida aceita apenas dois clubes distintos e propaga nome e logo corretos para painel e overlay.
- Partidas antigas permanecem legiveis apos a mudanca de modelo.
