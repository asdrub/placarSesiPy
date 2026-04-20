# Implementation Plan: Galeria de Layouts de Placar

**Branch**: `[003-add-layout-gallery]` | **Date**: 2026-04-20 | **Spec**: [specs/003-scoreboard-layout-gallery/spec.md](specs/003-scoreboard-layout-gallery/spec.md)
**Input**: Feature specification from `/specs/003-scoreboard-layout-gallery/spec.md`

## Summary

Adicionar uma etapa de galeria de layouts logo apos o login no console manual, antes do setup basico ja existente, reaproveitando o sidebar atual e persistindo um `layoutId` no estado da partida. O desenho evita novo endpoint de catalogo e mantem Python e HTML/JS embutido: uma lista estatica de layouts e injetada no painel, a escolha fica visivel ao operador, e o overlay passa a selecionar sua apresentacao a partir do layout persistido sem alterar o fluxo atual de clubes, placar, cronometro e recolhimento da barra lateral.

## Technical Context

**Language/Version**: Python 3.11 no backend; HTML/CSS/JavaScript vanilla no cliente  
**Primary Dependencies**: `azure-functions`, `azure-storage-blob`, `requests`, biblioteca padrao Python  
**Storage**: Blob JSON por partida na storage account da Function App, com compatibilidade de leitura para partidas antigas sem `layoutId`  
**Testing**: `pytest` para validacao de estado e contratos; validacao manual local com Azure Functions Core Tools e navegador  
**Target Platform**: Azure Functions v4 em Linux, com execucao local via Functions Core Tools e Azurite  
**Project Type**: Aplicacao web serverless pequena com HTML servido pela propria Function App e endpoints HTTP JSON  
**Runtime Decision**: Manter Python; a feature e incremental no fluxo existente e nao ha evidencia de ganho geral com migracao parcial para JavaScript  
**Performance Goals**: exibir a galeria em ate 2 segundos apos login bem-sucedido; permitir chegar da escolha de layout ao setup em ate 15 segundos; refletir o layout selecionado no overlay em ate 2 segundos em pelo menos 95% das leituras  
**Constraints**: sem novas dependencias de runtime; sem endpoint separado para catalogo de layouts; setup basico deve permanecer igual apos a escolha; mudanca de layout so e permitida enquanto a partida estiver em `draft`; comportamento de ocultacao do sidebar deve permanecer intacto  
**Scale/Scope**: conjunto pequeno e fechado de layouts oficiais, 1 operador principal por partida, baixo volume operacional e codigo concentrado em poucos arquivos root-centric

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Smallest viable change identified; any new abstraction, dependency, or service has explicit justification. PASS: a feature pode ser entregue com catalogo estatico de layouts, uma nova etapa visual no sidebar atual e um campo adicional no estado da partida, sem novo servico nem dependencia.
- Reuse inventory completed for affected code paths, helpers, and platform capabilities. PASS: serao reaproveitados `admin_html()`, `setConfigOpen()`, `renderGame()`, `overlay_html()`, `BlobGameStore`, `build_initial_game()`, `apply_game_update()` e o fluxo atual de autenticacao e criacao de partida.
- Runtime decision documented; Python remains default unless JavaScript has evidence-backed gains. PASS: Python mantido; a logica nova permanece coerente com a renderizacao embutida ja existente.
- Resource impact recorded for external calls, dependency weight, latency, and memory expectations. PASS: a galeria usa dados estaticos locais, nao adiciona chamadas externas e acrescenta apenas custo desprezivel de memoria e payload ao estado da partida.
- Minimum security controls identified for secrets, input validation, and error handling. PASS: senha administrativa continua fora do codigo, `layoutId` passa a ser validado contra um conjunto permitido, e erros continuam sem exposicao de detalhes internos.

## Project Structure

### Documentation (this feature)

```text
specs/003-scoreboard-layout-gallery/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── scoreboard-layout-api.yaml
└── tasks.md
```

### Source Code (repository root)

```text
.
├── function_app.py
├── scoreboard_state.py
├── club_catalog.py
├── README.md
├── requirements.txt
├── host.json
├── local.settings.example.json
├── local.settings.json
└── specs/
    ├── 001-manual-score-console/
    ├── 002-championship-club-selector/
    └── 003-scoreboard-layout-gallery/
```

**Structure Decision**: Manter o projeto unico no root. `function_app.py` continua como ponto principal da UI administrativa e do overlay, enquanto `scoreboard_state.py` continua responsavel por validacao, serializacao e persistencia do estado. A feature admite apenas uma extracao pequena de catalogo de layouts para helper dedicado se a duplicacao entre painel e overlay realmente justificar; fora isso, a mudanca permanece contida na estrutura atual.

## Post-Design Constitution Check

- Smallest viable change re-checked. PASS: o design final usa galeria embutida no sidebar atual e um `layoutId` no estado da partida; nenhuma arquitetura paralela foi introduzida.
- Reuse re-checked. PASS: a nova etapa se encaixa entre `loginPanel` e `gamePanel`, e o overlay continua consumindo `/api/games/{gameId}` com extensao de payload, sem novo contrato de leitura separado.
- Runtime decision re-checked. PASS: nao surgiu qualquer pressao tecnica para migracao de runtime.
- Resource impact re-checked. PASS: layouts estaticos mantem custo de memoria e latencia praticamente inalterados e nao aumentam chamadas HTTP.
- Security re-checked. PASS: o plano limita `layoutId` a valores conhecidos, mantem autenticacao atual e restringe troca de layout ao estado `draft` para reduzir risco operacional.

## Complexity Tracking

Nenhuma violacao da constituicao precisa de justificativa adicional nesta fase.
