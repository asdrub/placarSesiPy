# Tasks: Console Manual de Placar

**Input**: Design documents from `/specs/001-manual-score-console/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/scoreboard-api.yaml`, `quickstart.md`

**Tests**: Testes automatizados nao foram explicitamente solicitados nesta feature. A validacao obrigatoria desta entrega segue o fluxo manual descrito em `specs/001-manual-score-console/quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar dependencias e configuracoes locais minimas para a implementacao.

- [X] T001 Adicionar a dependencia de persistencia em blob mantendo o budget enxuto em `requirements.txt`
- [X] T002 [P] Criar exemplo de configuracao local para `ADMIN_PASSWORD`, `AzureWebJobsStorage` e `SCOREBOARD_STATE_CONTAINER` em `local.settings.example.json`
- [X] T003 [P] Atualizar o contexto de execucao local da feature com as variaveis obrigatorias em `specs/001-manual-score-console/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Criar o nucleo de estado, persistencia e infraestrutura HTTP compartilhada.

**CRITICAL**: Nenhuma historia de usuario deve comecar antes desta fase estar completa.

- [X] T004 Validar o conjunto final de dependencias e restricoes operacionais em `specs/001-manual-score-console/plan.md`
- [X] T005 Criar os modelos de estado, validacoes basicas e serializacao de snapshots em `scoreboard_state.py`
- [X] T006 Implementar a camada de persistencia em blob para carregar, salvar e remover partidas em `scoreboard_state.py`
- [X] T007 [P] Configurar leitura centralizada de senha administrativa e container de estado em `function_app.py`
- [X] T008 [P] Implementar utilitarios compartilhados de parsing JSON, respostas HTTP e logs essenciais em `function_app.py`
- [X] T009 Integrar o `function_app.py` ao `scoreboard_state.py` para obter acesso ao armazenamento e ao ciclo de vida de partidas

**Checkpoint**: Fundacao pronta. As historias de usuario podem seguir em paralelo.

---

## Phase 3: User Story 1 - Operar o placar ao vivo (Priority: P1) 🎯 MVP

**Goal**: Permitir que o operador atualize placar, faltas, periodo e cronometro sem submit manual.

**Independent Test**: Abrir uma partida no painel, alterar pontos, faltas, periodo e cronometro, e verificar atualizacao imediata do estado do jogo.

- [X] T010 [US1] Implementar as transicoes de score, faltas, periodo e cronometro em `scoreboard_state.py`
- [X] T011 [US1] Implementar os handlers de leitura e atualizacao do estado da partida em `function_app.py`
- [X] T012 [P] [US1] Construir o HTML do painel de operacao com controles de pontos, faltas, periodo e cronometro em `function_app.py`
- [X] T013 [US1] Adicionar autosave sem submit e polling curto do painel em `function_app.py`
- [X] T014 [US1] Reforcar validacoes de valores nao negativos, periodo de 1 a 4 e pausa/retomada do cronometro em `scoreboard_state.py`
- [X] T015 [US1] Registrar logs essenciais para mutacoes de placar ao vivo em `function_app.py`

**Checkpoint**: A operacao manual do placar deve estar funcional e validavel por si so.

---

## Phase 4: User Story 2 - Configurar a partida e controlar acesso (Priority: P2)

**Goal**: Permitir autenticacao simples e configuracao dos dados da partida com URL unica por jogo.

**Independent Test**: Informar a senha correta, criar uma partida, preencher nomes e logos dos times e obter a URL publica do overlay.

- [X] T016 [US2] Implementar a validacao da senha unica e o endpoint de sessao administrativa em `function_app.py`
- [X] T017 [P] [US2] Implementar a geracao de `gameId`, URL publica e estado inicial da partida em `scoreboard_state.py`
- [X] T018 [US2] Implementar os handlers de criacao e encerramento de partidas em `function_app.py`
- [X] T019 [US2] Estender o fluxo do painel para autenticacao, configuracao de times e exibicao da URL publica em `function_app.py`
- [X] T020 [US2] Alinhar a configuracao administrativa local com o fluxo de acesso do painel em `local.settings.example.json`

**Checkpoint**: O operador deve conseguir autenticar, configurar a partida e obter uma URL publica unica sem depender do overlay pronto.

---

## Phase 5: User Story 3 - Exibir o placar na transmissao (Priority: P3)

**Goal**: Exibir em URL publica um overlay somente leitura que acompanhe o estado operado na mesa.

**Independent Test**: Abrir a URL publica do jogo em outro navegador e confirmar a renderizacao e atualizacao automatica do placar, faltas, periodo e cronometro.

- [X] T021 [P] [US3] Implementar a projecao publica do estado da partida para consumo do overlay em `scoreboard_state.py`
- [X] T022 [US3] Implementar a rota HTML publica do overlay por `gameId` em `function_app.py`
- [X] T023 [US3] Implementar a renderizacao do overlay com score, nomes, logos, periodo e cronometro em `function_app.py`
- [X] T024 [US3] Adicionar polling curto e tratamento de estado vazio ou jogo inexistente no overlay em `function_app.py`

**Checkpoint**: O overlay publico deve funcionar por URL unica e refletir automaticamente o estado da partida.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Fechar documentacao, seguranca minima e validacao manual final.

- [X] T025 [P] Documentar endpoints, variaveis de ambiente e fluxo manual do placar em `README.md`
- [X] T026 Verificar peso final de dependencias e remover qualquer adicao desnecessaria em `requirements.txt`
- [X] T027 Revisar tratamento de segredos, erros publicos e logs administrativos em `function_app.py`
- [X] T028 Validar o fluxo completo da feature e ajustar instrucoes finais em `specs/001-manual-score-console/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: pode iniciar imediatamente.
- **Phase 2: Foundational**: depende da conclusao do Setup e bloqueia todas as historias.
- **Phase 3: US1**: depende da conclusao completa da Foundational.
- **Phase 4: US2**: depende da conclusao completa da Foundational.
- **Phase 5: US3**: depende da conclusao completa da Foundational.
- **Phase 6: Polish**: depende das historias que forem incluidas na entrega.

### User Story Dependencies

- **US1 (P1)**: depende apenas da fundacao e entrega o MVP operacional.
- **US2 (P2)**: depende apenas da fundacao; pode ser validada independentemente ao criar e configurar partidas.
- **US3 (P3)**: depende apenas da fundacao; pode ser validada com uma partida previamente existente.

### Recommended Execution Order

- Completar `T001-T003`.
- Completar `T004-T009`.
- Entregar MVP com `T010-T015` e validar antes de seguir.
- Adicionar configuracao e acesso com `T016-T020`.
- Adicionar overlay publico com `T021-T024`.
- Finalizar com `T025-T028`.

---

## Parallel Opportunities

- **Setup**: `T002` e `T003` podem ocorrer em paralelo apos `T001`.
- **Foundational**: `T007` e `T008` podem ocorrer em paralelo apos `T005-T006` definirem o contrato interno compartilhado.
- **US1**: `T012` pode ser trabalhada em paralelo com `T010` enquanto o contrato de atualizacao for mantido.
- **US2**: `T017` pode ocorrer em paralelo com `T016`.
- **US3**: `T021` pode ocorrer em paralelo com `T022`.
- **Polish**: `T025` pode ocorrer em paralelo com `T026`.

---

## Parallel Example: User Story 1

```bash
# Depois da fundacao, estes itens podem avancar em paralelo:
Task: "Implementar as transicoes de score, faltas, periodo e cronometro em scoreboard_state.py"
Task: "Construir o HTML do painel de operacao com controles de pontos, faltas, periodo e cronometro em function_app.py"
```

## Parallel Example: User Story 2

```bash
# Depois da fundacao, estes itens podem avancar em paralelo:
Task: "Implementar a validacao da senha unica e o endpoint de sessao administrativa em function_app.py"
Task: "Implementar a geracao de gameId, URL publica e estado inicial da partida em scoreboard_state.py"
```

## Parallel Example: User Story 3

```bash
# Depois da fundacao, estes itens podem avancar em paralelo:
Task: "Implementar a projecao publica do estado da partida para consumo do overlay em scoreboard_state.py"
Task: "Implementar a rota HTML publica do overlay por gameId em function_app.py"
```

---

## Implementation Strategy

### MVP First

1. Completar Setup e Foundational.
2. Completar US1.
3. Validar manualmente o fluxo do painel de operacao antes de expandir a feature.

### Incremental Delivery

1. MVP operacional com US1.
2. Acrescentar autenticacao simples e criacao/configuracao de partidas com US2.
3. Acrescentar overlay publico em tempo quase real com US3.
4. Fechar documentacao, seguranca minima e validacao final em Polish.

### Notes

- Tasks marcadas com `[P]` usam arquivos diferentes e podem ser executadas em paralelo.
- Cada historia permanece validavel de forma independente apos a fundacao.
- O plano prioriza menor mudanca viavel sobre refatores estruturais amplos.