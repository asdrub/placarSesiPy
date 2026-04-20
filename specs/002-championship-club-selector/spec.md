# Feature Specification: Seletor de Clubes 2026

**Feature Branch**: `[002-championship-club-selector]`  
**Created**: 2026-04-20  
**Status**: Draft  
**Input**: User description: "Vamos incluir no setup da partida a opcao de escolher-se os nomes e logos de todos os clubes de campeonato 2026 conforme a lista a seguir, substituindo os campos de texto para nome e URL do logo por opcoes predefinidas"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Escolher clubes no setup da partida (Priority: P1)

Como operador da mesa, eu quero selecionar os clubes mandante e visitante a partir de uma lista oficial do campeonato para iniciar a partida com nomes e logos corretos sem digitacao manual.

**Why this priority**: Esse e o fluxo principal da feature. Sem ele, o setup continua dependente de digitacao livre e nao entrega o ganho de padronizacao pedido.

**Independent Test**: Pode ser testado abrindo o setup de uma nova partida, escolhendo um clube para cada lado e confirmando que nome e logo exibidos passam a refletir automaticamente as selecoes.

**Acceptance Scenarios**:

1. **Given** que o operador abre o setup de uma nova partida, **When** seleciona `SESI / Araraquara` para um dos lados, **Then** o sistema associa automaticamente o nome oficial e o logo correspondente a esse lado da partida.
2. **Given** que o operador abre o setup de uma nova partida, **When** seleciona clubes distintos para mandante e visitante, **Then** a partida fica pronta para criacao sem exigir digitacao manual de nome ou URL de logo.
3. **Given** que o operador esta no setup da partida, **When** procura os campos livres de nome do time e URL de logo, **Then** esses campos nao devem mais aparecer no fluxo principal de configuracao.

---

### User Story 2 - Garantir padronizacao visual dos clubes (Priority: P2)

Como operador da mesa, eu quero que cada clube carregue sua identidade visual oficial ao ser escolhido para evitar erro operacional e manter a transmissao padronizada.

**Why this priority**: A padronizacao reduz erros de digitacao, inconsistencias visuais e retrabalho durante a preparacao da transmissao.

**Independent Test**: Pode ser testado selecionando cada clube disponivel e verificando que o nome oficial e o logo correspondente sao sempre os mesmos em todas as exibicoes da partida.

**Acceptance Scenarios**:

1. **Given** que o catalogo de clubes esta disponivel no setup, **When** o operador seleciona qualquer opcao da lista oficial, **Then** o sistema deve aplicar o par correto de nome e logo cadastrado para aquele clube.
2. **Given** que o operador altera a selecao de um dos lados da partida, **When** escolhe outro clube da lista oficial, **Then** o nome e o logo desse lado devem ser atualizados juntos para a nova identidade escolhida.
3. **Given** que o operador tenta escolher o mesmo clube para os dois lados da partida, **When** conclui a configuracao, **Then** o sistema deve impedir a criacao da partida com essa combinacao invalida.

---

### User Story 3 - Propagar os clubes selecionados para a exibicao do jogo (Priority: P3)

Como produtor de transmissao, eu quero ver na area de controle e no overlay publico os nomes e logos oficiais dos clubes escolhidos para que a apresentacao do jogo fique consistente em todos os pontos de exibicao.

**Why this priority**: A utilidade da selecao predefinida depende de os dados corretos aparecerem tambem na apresentacao publica, e nao apenas no setup interno.

**Independent Test**: Pode ser testado criando uma partida com dois clubes do catalogo e verificando que painel e overlay mostram a mesma identidade visual para cada lado.

**Acceptance Scenarios**:

1. **Given** que uma partida foi criada com clubes da lista oficial, **When** o painel principal de controle e aberto, **Then** os nomes e logos mostrados para mandante e visitante devem corresponder as selecoes feitas no setup.
2. **Given** que uma partida foi criada com clubes da lista oficial, **When** a URL publica do overlay e aberta, **Then** ela deve exibir os mesmos nomes e logos configurados no setup da partida.
3. **Given** que o operador ajusta a escolha de um clube antes do inicio da partida, **When** salva ou conclui a configuracao valida, **Then** todas as exibicoes da partida devem passar a usar a identidade mais recente selecionada.

### Edge Cases

- Se o operador abrir o setup de uma partida existente criada antes dessa feature, o sistema deve manter a partida legivel e nao exibir dados quebrados para nomes ou logos ja salvos.
- Se um dos logos oficiais estiver temporariamente indisponivel no momento de exibicao, a partida deve continuar identificando corretamente o clube pelo nome oficial.
- Se o operador ainda nao tiver escolhido os dois clubes, a criacao da partida deve permanecer bloqueada com orientacao clara sobre o que falta.
- Se a lista oficial de clubes estiver sendo exibida, ela deve apresentar exatamente as opcoes aprovadas para essa entrega, sem alternativas livres no fluxo principal.

## Constraints *(mandatory)*

- **CT-001**: A feature MUST manter o setup da partida tao simples quanto o fluxo atual, trocando digitacao livre por selecao direta sem adicionar etapas extras desnecessarias.
- **CT-002**: A feature MUST reaproveitar o fluxo existente de configuracao da partida em vez de criar um caminho paralelo para escolher clubes.
- **CT-003**: A feature MUST limitar o catalogo inicial aos clubes e identidades oficiais explicitamente aprovados para o campeonato 2026 nesta entrega.
- **CT-004**: A feature MUST validar as selecoes do operador para evitar combinacoes invalidas e nao expor erros internos quando algum dado visual nao puder ser carregado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST substituir os campos livres de nome do time e URL de logo no setup da partida por controles de selecao baseados em um catalogo oficial de clubes do campeonato 2026.
- **FR-002**: O sistema MUST disponibilizar no catalogo oficial exatamente os seguintes clubes para esta entrega: `SESI / Araraquara`, `ARAE/ SMEL Catanduva`, `Sao Jose Basketball/ Atleta Cidadao`, `FEAC Franca Basquete` e `A.D. Santo Andre`.
- **FR-003**: O sistema MUST associar a cada clube do catalogo um nome oficial de exibicao e um logo oficial predefinido.
- **FR-004**: O sistema MUST preencher automaticamente o nome exibido e o logo do lado correspondente assim que o operador selecionar um clube no setup da partida.
- **FR-005**: O sistema MUST permitir selecionar clubes distintos para mandante e visitante dentro do mesmo fluxo de configuracao da partida.
- **FR-006**: O sistema MUST impedir a criacao ou atualizacao da partida quando o mesmo clube estiver selecionado para os dois lados.
- **FR-007**: O sistema MUST impedir que o operador precise informar manualmente nome de clube ou URL de logo no fluxo principal dessa configuracao.
- **FR-008**: O sistema MUST manter os demais dados e controles do setup da partida funcionando sem exigir um fluxo alternativo para criar o jogo.
- **FR-009**: O sistema MUST preservar no estado da partida qual clube foi escolhido para cada lado e os dados de exibicao derivados dessa escolha.
- **FR-010**: O sistema MUST mostrar os nomes e logos oficiais selecionados no painel administrativo apos a criacao da partida.
- **FR-011**: O sistema MUST mostrar os mesmos nomes e logos oficiais selecionados na exibicao publica da partida.
- **FR-012**: O sistema MUST manter a lista oficial consistente em toda nova configuracao de partida criada com essa feature.
- **FR-013**: O sistema MUST continuar exibindo partidas antigas de forma legivel mesmo quando elas tiverem sido configuradas antes da adocao do catalogo oficial.
- **FR-014**: O sistema MUST usar os seguintes pares oficiais de clube e logo para esta entrega: `SESI / Araraquara` com `https://lbf.com.br/wp-content/uploads/2025/04/Novo-Logo-SESI-Araraquara.png`, `ARAE/ SMEL Catanduva` com `https://yt3.googleusercontent.com/cGTEpMCYExFEJsYRubQHaBcP2N7r3bxUnyCinuo2xsw-pjuW3T0SGjRhPbNbfdIuycQ9f1eo=s900-c-k-c0x00ffffff-no-rj`, `Sao Jose Basketball/ Atleta Cidadao` com `https://sistema.fpb.com.br/img/teams/207.jpg`, `FEAC Franca Basquete` com `https://sistema.fpb.com.br/img/teams/114.jpg` e `A.D. Santo Andre` com `https://sistema.fpb.com.br/img/teams/279.jpg`.

### Key Entities *(include if feature involves data)*

- **Catalogo de Clubes 2026**: Representa a lista fechada de clubes aprovados para selecao no setup, incluindo nome oficial de exibicao e logo oficial de cada clube.
- **Selecao de Clube da Partida**: Representa a escolha do clube atribuida a um dos lados da partida e os dados de exibicao derivados dessa escolha.
- **Partida**: Representa o jogo configurado no painel, incluindo mandante, visitante e demais informacoes operacionais ja existentes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um operador consegue configurar os dois clubes de uma nova partida em ate 30 segundos, sem digitar nomes ou URLs de logo.
- **SC-002**: Em 100% das validacoes manuais com os clubes aprovados, cada selecao exibe o nome oficial e o logo correspondente sem divergencia entre setup, painel e overlay.
- **SC-003**: Em 100% das tentativas de criar partida com o mesmo clube em ambos os lados, o sistema bloqueia a configuracao antes do inicio da operacao.
- **SC-004**: Em pelo menos 95% das criacoes de partida avaliadas, o operador conclui o setup visual na primeira tentativa sem precisar corrigir erro de nome ou logo do clube.

## Assumptions

- Esta entrega cobre exatamente os cinco clubes informados pelo solicitante como lista oficial inicial do campeonato 2026.
- Os nomes oficiais e os logos fornecidos para esses clubes permanecem validos para o periodo de uso desta feature.
- O fluxo de setup continua trabalhando com dois lados fixos da partida: mandante e visitante.
- Os demais controles do placar, autenticacao e overlay permanecem fora do escopo de alteracao funcional principal desta feature.
- Partidas configuradas antes dessa entrega podem continuar existindo com dados historicos ja salvos, mas novas configuracoes devem usar o catalogo oficial em vez de digitacao livre.
