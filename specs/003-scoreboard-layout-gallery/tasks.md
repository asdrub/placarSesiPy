# Tasks: Galeria de Layouts de Placar

**Input**: Design documents from `/specs/003-scoreboard-layout-gallery/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluir testes para contrato, persistencia de `layoutId`, fallback legada e fluxo critico do painel porque a feature altera selecao de estado, contrato HTTP e comportamento visual do overlay.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar a base comum da feature sem alterar o fluxo principal ainda.

- [X] T001 Revisar e confirmar os pontos de reuso da feature em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py e /Users/eduardoribeiro/projetos-code/placarSesiPy/scoreboard_state.py
- [X] T002 [P] Criar o catalogo estatico de layouts oficiais em /Users/eduardoribeiro/projetos-code/placarSesiPy/scoreboard_layout_catalog.py
- [X] T003 [P] Atualizar o contexto de execucao e validacao da feature em /Users/eduardoribeiro/projetos-code/placarSesiPy/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Criar a infraestrutura minima que bloqueia todas as historias.

**⚠️ CRITICAL**: Nenhuma user story deve comecar antes desta fase.

- [X] T004 Integrar o catalogo de layouts e validacao de `layoutId` ao modelo de estado em /Users/eduardoribeiro/projetos-code/placarSesiPy/scoreboard_state.py
- [X] T005 Estender a criacao, serializacao e leitura de partidas com fallback legada de `layoutId` em /Users/eduardoribeiro/projetos-code/placarSesiPy/scoreboard_state.py
- [X] T006 Atualizar as rotas `POST /api/games` e `PATCH /api/games/{gameId}` para aceitar `layoutId` conforme contrato em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py
- [X] T007 [P] Cobrir a validacao base de `layoutId`, fallback legada e bloqueio fora de `draft` em /Users/eduardoribeiro/projetos-code/placarSesiPy/tests/unit/test_scoreboard_layout_state.py
- [X] T008 [P] Atualizar o contrato HTTP com `layoutId` definitivo e restricoes de alteracao em /Users/eduardoribeiro/projetos-code/placarSesiPy/specs/003-scoreboard-layout-gallery/contracts/scoreboard-layout-api.yaml

**Checkpoint**: Estado, contrato e persistencia de layout prontos para suportar as historias.

---

## Phase 3: User Story 1 - Escolher layout antes do setup (Priority: P1) 🎯 MVP

**Goal**: Exibir uma galeria de layouts logo apos o login e bloquear o setup ate que um layout valido seja escolhido.

**Independent Test**: Fazer login em `/api/control`, verificar a galeria antes do setup, tentar prosseguir sem layout e depois escolher um layout valido para liberar o setup.

### Tests for User Story 1

- [X] T009 [P] [US1] Criar teste de contrato para `POST /api/games` exigindo `layoutId` em /Users/eduardoribeiro/projetos-code/placarSesiPy/tests/contract/test_layout_game_creation.py
- [X] T010 [P] [US1] Criar teste de integracao do fluxo login -> galeria -> setup em /Users/eduardoribeiro/projetos-code/placarSesiPy/tests/integration/test_control_layout_gallery.py

### Implementation for User Story 1

- [X] T011 [US1] Adicionar a secao `galleryPanel` com cards, estilos e bloqueio inicial do setup em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py
- [X] T012 [US1] Implementar o estado cliente da galeria, selecao obrigatoria e transicao `loginPanel -> galleryPanel -> gamePanel` em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py
- [X] T013 [US1] Enviar `layoutId` no fluxo de criacao de partida e exibir feedback de selecao invalida em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py
- [ ] T014 [US1] Registrar logs essenciais e tratamento minimo de erro para selecao e criacao com layout em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py

**Checkpoint**: O operador escolhe um layout antes do setup e consegue criar uma partida com `layoutId` persistido.

---

## Phase 4: User Story 2 - Manter o setup atual apos a escolha (Priority: P2)

**Goal**: Preservar o modelo atual do setup basico depois da escolha do layout, mantendo a identidade visual selecionada associada a partida.

**Independent Test**: Escolher qualquer layout e confirmar que os formularios basicos continuam com a mesma estrutura e operacao atual, sem fluxo alternativo.

### Tests for User Story 2

- [X] T015 [P] [US2] Criar teste unitario de persistencia e recarga de `layoutId` em /Users/eduardoribeiro/projetos-code/placarSesiPy/tests/unit/test_layout_persistence.py
- [X] T016 [P] [US2] Criar teste de integracao para manter o setup atual apos a escolha do layout em /Users/eduardoribeiro/projetos-code/placarSesiPy/tests/integration/test_control_setup_after_layout.py

### Implementation for User Story 2

- [X] T017 [US2] Persistir `layoutId` e metadados de selecao no ciclo de vida da partida em /Users/eduardoribeiro/projetos-code/placarSesiPy/scoreboard_state.py
- [X] T018 [US2] Exibir o layout selecionado no painel e reaproveitar os formularios atuais sem duplicacao em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py
- [X] T019 [US2] Implementar restauracao da escolha ao carregar partida existente e fallback para partidas sem `layoutId` em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py
- [X] T020 [US2] Permitir troca de layout apenas enquanto a partida estiver em `draft` via `PATCH /api/games/{gameId}` em /Users/eduardoribeiro/projetos-code/placarSesiPy/scoreboard_state.py

**Checkpoint**: O setup continua igual ao atual apos a escolha e a selecao de layout permanece associada a partida durante a configuracao.

---

## Phase 5: User Story 3 - Preservar a experiencia lateral do painel (Priority: P3)

**Goal**: Manter o comportamento atual do sidebar e propagar o layout selecionado para o overlay sem regressao visual ou operacional.

**Independent Test**: Criar uma partida com layout escolhido, abrir o overlay correspondente e validar que o sidebar do painel continua recolhendo e reabrindo como antes.

### Tests for User Story 3

- [X] T021 [P] [US3] Criar teste de integracao para recolhimento e reabertura do sidebar apos escolha de layout em /Users/eduardoribeiro/projetos-code/placarSesiPy/tests/integration/test_sidebar_layout_flow.py
- [X] T022 [P] [US3] Criar teste de integracao para fallback legado e renderizacao do overlay por `layoutId` em /Users/eduardoribeiro/projetos-code/placarSesiPy/tests/integration/test_overlay_layout_rendering.py

### Implementation for User Story 3

- [X] T023 [US3] Adaptar `overlay_html()` para selecionar variacoes visuais a partir de `layoutId` com fallback para o layout padrao em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py
- [X] T024 [US3] Preservar a logica existente de `setConfigOpen()` e do auto-collapse do sidebar durante galeria, setup e operacao em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py
- [X] T025 [US3] Garantir que carregar partidas antigas sem `layoutId` nao quebre painel nem overlay em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py

**Checkpoint**: O overlay respeita o layout selecionado e o sidebar continua funcionando como antes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Ajustes finais, documentacao e validacao cruzada.

- [X] T026 [P] Atualizar a documentacao operacional da feature em /Users/eduardoribeiro/projetos-code/placarSesiPy/README.md
- [ ] T027 Revisar validacao de entradas, mensagens de erro e logs essenciais de layout em /Users/eduardoribeiro/projetos-code/placarSesiPy/function_app.py e /Users/eduardoribeiro/projetos-code/placarSesiPy/scoreboard_state.py
- [ ] T028 Executar e ajustar o roteiro de validacao manual em /Users/eduardoribeiro/projetos-code/placarSesiPy/specs/003-scoreboard-layout-gallery/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pode iniciar imediatamente.
- **Foundational (Phase 2)**: Depende da Setup e bloqueia todas as user stories.
- **User Stories (Phase 3+)**: Dependem da conclusao da fase Foundational.
- **Polish (Phase 6)**: Depende das user stories que entrarem na entrega.

### User Story Dependencies

- **User Story 1 (P1)**: Comeca assim que a Foundational estiver concluida; e o MVP da feature.
- **User Story 2 (P2)**: Depende da persistencia e criacao com `layoutId` da Foundational e integra o fluxo entregue em US1.
- **User Story 3 (P3)**: Depende da existencia de `layoutId` carregavel e visivel no painel; valida overlay e sidebar apos US1 e US2.

### Within Each User Story

- Testes primeiro, garantindo falha inicial antes da implementacao.
- Estado persistido antes de wiring visual quando a historia depende de backend.
- Alteracoes de UI antes da integracao final do fluxo.
- Checkpoint de historia antes de avancar para a proxima prioridade.

### Parallel Opportunities

- `T002` e `T003` podem rodar em paralelo.
- `T007` e `T008` podem rodar em paralelo apos `T004`-`T006` estarem definidos.
- `T009` e `T010` podem rodar em paralelo.
- `T015` e `T016` podem rodar em paralelo.
- `T021` e `T022` podem rodar em paralelo.

---

## Parallel Example: User Story 1

```bash
# Tests da US1 em paralelo:
Task: "Criar teste de contrato para POST /api/games exigindo layoutId em tests/contract/test_layout_game_creation.py"
Task: "Criar teste de integracao do fluxo login -> galeria -> setup em tests/integration/test_control_layout_gallery.py"

# Implementacao paralela inicial da US1:
Task: "Adicionar a secao galleryPanel com cards, estilos e bloqueio inicial do setup em function_app.py"
Task: "Implementar o estado cliente da galeria, selecao obrigatoria e transicao loginPanel -> galleryPanel -> gamePanel em function_app.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup.
2. Completar Phase 2: Foundational.
3. Completar Phase 3: User Story 1.
4. Validar o fluxo login -> galeria -> setup -> criacao de partida.
5. Demonstrar a feature minima com `layoutId` persistido.

### Incremental Delivery

1. Setup + Foundational deixam catalogo, persistencia e contrato prontos.
2. US1 entrega a nova entrada da feature e ja permite demo do MVP.
3. US2 consolida persistencia, restauracao e preservacao do setup atual.
4. US3 fecha overlay, sidebar e compatibilidade legada.
5. Phase 6 fecha documentacao e validacao final.

### Parallel Team Strategy

1. Uma pessoa fecha `scoreboard_state.py` e contrato na Foundational.
2. Outra pessoa prepara os testes de integracao do painel.
3. Depois da Foundational:
   - Dev A: US1 no painel admin.
   - Dev B: US2 em persistencia e restauracao.
   - Dev C: US3 em overlay e sidebar.

---

## Notes

- `[P]` indica tarefas em arquivos independentes ou com baixo acoplamento imediato.
- `[US1]`, `[US2]` e `[US3]` mantem rastreabilidade direta com a spec.
- As tarefas privilegiam a menor mudanca possivel no fluxo existente.
- Partidas antigas sem `layoutId` devem continuar legiveis em todo o plano.
