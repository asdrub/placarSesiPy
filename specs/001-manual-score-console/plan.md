# Implementation Plan: Console Manual de Placar

**Branch**: `[001-manual-score-console]` | **Date**: 2026-04-19 | **Spec**: [specs/001-manual-score-console/spec.md](specs/001-manual-score-console/spec.md)
**Input**: Feature specification from `/specs/001-manual-score-console/spec.md`

## Summary

Adicionar ao app atual em Azure Functions um fluxo manual de operacao de partidas com duas interfaces HTML servidas pela propria Function App: um painel protegido por senha unica para criar e atualizar o estado da partida e um overlay publico por jogo para exibicao em transmissao. A implementacao mantera o backend em Python, reutilizara o padrao atual de rotas HTTP + HTML da Function App, persistira o estado por jogo em JSON no storage ja associado a aplicacao e usara polling curto para refletir alteracoes no overlay sem introduzir SignalR ou outro servico pesado.

## Technical Context

**Language/Version**: Python 3.11 no backend; HTML/CSS/JavaScript vanilla no cliente  
**Primary Dependencies**: `azure-functions`, `requests` existente, biblioteca padrao Python, `azure-storage-blob` para persistencia de estado em blob JSON usando a storage account da Function App  
**Storage**: Blob JSON por jogo em container dedicado na storage account da Function App, com cache em memoria apenas como acelerador local nao autoritativo  
**Testing**: `pytest` para helpers puros e validacoes de estado; validacao manual local com Azure Functions Core Tools para fluxos HTML e HTTP  
**Target Platform**: Azure Functions v4 em Linux, com execucao local via Functions Core Tools  
**Project Type**: Aplicacao web serverless de pagina dupla com API HTTP leve  
**Runtime Decision**: Manter Python; nao ha evidencia de ganho global ao migrar para JavaScript diante do backend existente, das dependencias minimas atuais e da necessidade de menor mudanca viavel  
**Performance Goals**: refletir atualizacoes validas do painel no overlay em ate 2 segundos em pelo menos 95% das vezes; carregar painel e overlay em ate 5 segundos; responder operacoes de estado em ate 250 ms p95 sob carga baixa  
**Constraints**: sem SignalR, sem banco dedicado, sem framework frontend; no maximo uma nova dependencia de runtime; seguranca minima via senha unica fora do codigo fonte; sem suporte a prorrogacao nesta versao; entradas devem impedir valores negativos e periodos fora de 1-4  
**Scale/Scope**: MVP para operacao de baixa escala, com 1 operador principal por partida, 1 partida ativa por URL e volume baixo de espectadores simultaneos por jogo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Smallest viable change identified; any new abstraction, dependency, or service has explicit justification. PASS: a unica nova dependencia proposta e `azure-storage-blob`, justificada por persistencia real usando a storage account ja exigida pela Function App.
- Reuse inventory completed for affected code paths, helpers, and platform capabilities. PASS: serao reaproveitados o app Azure Functions atual, o padrao de rotas HTML/JSON, o `host.json`, a estrutura de deploy existente e a storage account obrigatoria da plataforma.
- Runtime decision documented; Python remains default unless JavaScript has evidence-backed gains. PASS: Python mantido como runtime principal.
- Resource impact recorded for external calls, dependency weight, latency, and memory expectations. PASS: polling curto substitui infraestrutura de tempo real; blobs JSON pequenos por jogo mantem memoria e custo baixos.
- Minimum security controls identified for secrets, input validation, and error handling. PASS: senha via configuracao, validacao de payload, respostas sem detalhes internos e separacao de rotas publicas e administrativas.

## Project Structure

### Documentation (this feature)

```text
specs/001-manual-score-console/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- scoreboard-api.yaml
`-- tasks.md
```

### Source Code (repository root)

```text
.
|-- function_app.py
|-- host.json
|-- requirements.txt
|-- README.md
|-- specs/
|   `-- 001-manual-score-console/
`-- tests/
    |-- unit/
    `-- integration/
```

**Structure Decision**: Manter um unico projeto Azure Functions no root do repositorio. `function_app.py` continuara como ponto de entrada HTTP, enquanto a logica nova deve permanecer em pouquissimos modulos auxiliares apenas se isso reduzir o tamanho e a opacidade do arquivo atual. A estrutura alvo para implementacao e manter rotas HTTP no app existente e introduzir, se necessario, um helper pequeno para validacao/persistencia do estado do jogo e testes focados nesses helpers.

## Complexity Tracking

Nenhuma violacao da constituicao precisa de justificativa adicional nesta fase.
