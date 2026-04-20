# Implementation Plan: Seletor de Clubes 2026

**Branch**: `[002-championship-club-selector]` | **Date**: 2026-04-20 | **Spec**: [specs/002-championship-club-selector/spec.md](specs/002-championship-club-selector/spec.md)
**Input**: Feature specification from `/specs/002-championship-club-selector/spec.md`

## Summary

Substituir o preenchimento livre de nome e URL de logo dos times no setup da partida por uma selecao fechada dos clubes oficiais de 2026, mantendo o backend em Python e reaproveitando o fluxo atual de criacao de jogo, persistencia em blob JSON e renderizacao do painel e do overlay. O desenho proposto adiciona um catalogo estatico de clubes, persiste `clubId` junto do estado ja existente de `name` e `logoUrl`, e ajusta contrato e UI sem introduzir novos servicos ou dependencias de runtime.

## Technical Context

**Language/Version**: Python 3.11 no backend; HTML/CSS/JavaScript vanilla no cliente  
**Primary Dependencies**: `azure-functions`, `azure-storage-blob`, `requests`, biblioteca padrao Python  
**Storage**: Blob JSON por jogo na storage account da Function App, com compatibilidade para snapshots legados  
**Testing**: `pytest` para catalogo, validacao de selecao e serializacao de estado; validacao manual local com Azure Functions Core Tools  
**Target Platform**: Azure Functions v4 em Linux, com execucao local via Functions Core Tools e Azurite  
**Project Type**: Aplicacao web serverless pequena com HTML servido pela propria Function App e endpoints HTTP JSON  
**Runtime Decision**: Manter Python; nao ha ganho comprovado em migrar para JavaScript para um catalogo estatico e ajustes pequenos no fluxo existente  
**Performance Goals**: manter criacao e atualizacao de partida em ate 250 ms p95 sob carga baixa; refletir clubes selecionados no overlay em ate 2 segundos em pelo menos 95% das vezes; manter setup visual completo em ate 30 segundos  
**Constraints**: sem novas dependencias de runtime; sem endpoint externo para catalogo; sem campos livres de nome/logo no fluxo principal; compatibilidade de leitura para jogos antigos; validacao obrigatoria para impedir selecao duplicada do mesmo clube  
**Scale/Scope**: lista fechada com 5 clubes oficiais, 1 operador principal por partida, baixo volume operacional e uma base de codigo root-centric com poucos arquivos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Smallest viable change identified; any new abstraction, dependency, or service has explicit justification. PASS: o desenho usa apenas um catalogo estatico e campos adicionais opcionais no estado atual; nenhum servico ou dependencia novos foram introduzidos.
- Reuse inventory completed for affected code paths, helpers, and platform capabilities. PASS: serao reaproveitados `build_initial_game`, `apply_game_update`, `BlobGameStore`, as rotas `/api/games`, a tela `admin_html()` e a renderizacao do overlay que ja consome `name` e `logoUrl`.
- Runtime decision documented; Python remains default unless JavaScript has evidence-backed gains. PASS: Python mantido, sem evidencia de ganho global para esta feature.
- Resource impact recorded for external calls, dependency weight, latency, and memory expectations. PASS: o catalogo e local ao processo, reduz chamadas externas e preserva o mesmo perfil leve de memoria e latencia do fluxo atual.
- Minimum security controls identified for secrets, input validation, and error handling. PASS: senha administrativa continua fora do codigo, entradas passam a validar `clubId` permitido e duplicidade entre lados, e respostas seguem sem expor detalhes internos.

## Project Structure

### Documentation (this feature)

```text
specs/002-championship-club-selector/
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
|-- scoreboard_state.py
|-- requirements.txt
|-- host.json
|-- README.md
|-- specs/
|   |-- 001-manual-score-console/
|   `-- 002-championship-club-selector/
|-- local.settings.example.json
`-- local.settings.json
```

**Structure Decision**: Manter um unico projeto Azure Functions no root do repositorio. `function_app.py` continua como ponto de entrada de HTML e HTTP, enquanto `scoreboard_state.py` permanece como local principal de validacao, montagem e persistencia do estado. A feature admite, no maximo, uma extracao pequena de catalogo para um helper dedicado se isso reduzir duplicacao entre backend e UI; fora isso, o trabalho permanece concentrado na estrutura atual. Se a implementacao adicionar cobertura automatizada, os testes poderao entrar em um novo `tests/` no root sem alterar a estrutura principal do app.

## Post-Design Constitution Check

- Smallest viable change re-checked. PASS: o design final usa catalogo fixo em codigo e evita endpoint adicional de catalogo, CMS ou configuracao remota.
- Reuse re-checked. PASS: overlay continua inalterado no contrato visual principal porque segue lendo `homeTeam.name`, `homeTeam.logoUrl`, `awayTeam.name` e `awayTeam.logoUrl`; a mudanca fica concentrada na configuracao e validacao.
- Runtime decision re-checked. PASS: nenhum artefato de design criou pressao para migracao parcial ou total de runtime.
- Resource impact re-checked. PASS: o catalogo adiciona custo desprezivel de memoria e elimina digitacao livre sem aumentar o numero de chamadas HTTP do overlay.
- Security re-checked. PASS: contratos e modelo passam a limitar entradas a IDs conhecidos e mantem compatibilidade sem expor segredos ou detalhes de storage.

## Complexity Tracking

Nenhuma violacao da constituicao precisa de justificativa adicional nesta fase.
