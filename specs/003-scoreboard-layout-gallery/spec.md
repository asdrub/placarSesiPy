# Feature Specification: Galeria de Layouts de Placar

**Feature Branch**: `[003-add-layout-gallery]`  
**Created**: 2026-04-20  
**Status**: Draft  
**Input**: User description: "Instroduzir nova funcionalidade. Devemos, ainda no setup da partida oferecer um menu adicional de opções de layouts para os placares além do atual. Logo após o login, devemos apresentar uma galeria de opções antes do início das configurações básicas hoje existentes. Após escolhido o layout do placar os form do painel de setup fixa-se neste modelo atual. Todas demais funcionalidades de ocultação do sidebar de setup continuam como antes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Escolher layout antes do setup (Priority: P1)

Como operador da mesa, eu quero escolher visualmente um layout de placar logo após o login para iniciar a configuração da partida já no modelo de apresentação desejado.

**Why this priority**: Essa é a nova entrada principal da feature. Sem essa escolha inicial, o sistema continua preso ao layout atual e não entrega a capacidade pedida.

**Independent Test**: Pode ser testado fazendo login no painel, verificando a exibição de uma galeria de layouts antes dos formulários de setup e escolhendo um dos layouts disponíveis para seguir com a configuração.

**Acceptance Scenarios**:

1. **Given** que o operador concluiu o login com sucesso, **When** acessa o fluxo de criação de partida, **Then** o sistema deve apresentar uma galeria de layouts de placar antes dos formulários básicos de setup.
2. **Given** que a galeria de layouts está visível, **When** o operador escolhe um layout disponível, **Then** o sistema deve registrar essa escolha e avançar para o setup normal da partida.
3. **Given** que o operador ainda não escolheu um layout, **When** tenta seguir para a configuração básica, **Then** o sistema não deve liberar o setup até que uma opção válida seja selecionada.

---

### User Story 2 - Manter o setup atual após a escolha (Priority: P2)

Como operador da mesa, eu quero que os formulários básicos continuem com o modelo atual depois da seleção do layout para não reaprender o fluxo operacional já usado hoje.

**Why this priority**: O pedido explicita que a novidade deve acontecer antes do setup, sem alterar a forma como o painel atual é operado depois da escolha do layout.

**Independent Test**: Pode ser testado selecionando qualquer layout e verificando que o painel exibe os mesmos formulários básicos já existentes, com a mesma sequência operacional.

**Acceptance Scenarios**:

1. **Given** que o operador selecionou um layout na galeria, **When** o painel avança para o setup, **Then** os formulários básicos devem manter a estrutura e comportamento atuais.
2. **Given** que o operador concluiu a escolha de layout, **When** cria ou carrega uma partida, **Then** o restante do fluxo operacional deve continuar igual ao já existente no painel.
3. **Given** que um layout foi escolhido, **When** o operador interage com os controles básicos do setup, **Then** a nova funcionalidade não deve introduzir etapas extras obrigatórias além da seleção inicial do layout.

---

### User Story 3 - Preservar a experiência lateral do painel (Priority: P3)

Como operador da mesa, eu quero continuar usando a ocultação do sidebar de setup como hoje para não perder a ergonomia atual do painel durante a operação da partida.

**Why this priority**: O usuário pediu explicitamente que a funcionalidade existente de ocultação do sidebar continue intacta, então isso precisa ser preservado como parte da experiência.

**Independent Test**: Pode ser testado escolhendo um layout, entrando no setup e validando que o comportamento de esconder e reabrir o sidebar continua igual ao fluxo atual.

**Acceptance Scenarios**:

1. **Given** que o operador já escolheu um layout e está no setup da partida, **When** usa o comando de ocultar o sidebar, **Then** o painel deve continuar recolhendo a lateral como acontece hoje.
2. **Given** que o sidebar foi ocultado após a escolha do layout, **When** o operador solicita sua reabertura, **Then** o painel deve restaurar a lateral sem perder a seleção do layout já feita.
3. **Given** que o operador navega entre galeria, setup e operação da partida, **When** usa os controles laterais existentes, **Then** o comportamento de recolhimento e expansão deve permanecer consistente em todo o fluxo.

### Edge Cases

- Se o operador fizer login e sair do fluxo sem escolher um layout, o sistema deve manter a criação de partida bloqueada e orientar claramente que a seleção é obrigatória.
- Se houver apenas um layout disponível na galeria, o sistema ainda deve apresentar a etapa de escolha de forma clara, sem pular automaticamente para o setup.
- Se o operador já tiver escolhido um layout e recarregar a página antes de iniciar a partida, o sistema deve deixar claro se a escolha ainda está ativa ou se precisa ser refeita antes do setup.
- Se a galeria estiver visível em telas menores, a seleção do layout deve continuar compreensível sem esconder ou quebrar os controles essenciais do fluxo.

## Constraints *(mandatory)*

- **CT-001**: A feature MUST manter a solução pequena e direta, adicionando a galeria de layouts sem criar um segundo fluxo completo de configuração de partida.
- **CT-002**: A feature MUST reaproveitar o setup atual como etapa seguinte à escolha do layout, em vez de duplicar os formulários básicos.
- **CT-003**: A feature MUST explicitar qualquer impacto visual ou operacional somente na etapa inicial do setup, preservando o restante do painel e a lógica de sidebar existentes.
- **CT-004**: A feature MUST manter as mesmas expectativas mínimas de segurança já existentes para login, entradas do setup e exposição de erros ao operador.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST oferecer, logo após o login bem-sucedido, uma galeria de layouts de placar antes da exibição dos formulários básicos atuais de setup da partida.
- **FR-002**: O sistema MUST apresentar na galeria apenas opções de layout válidas e claramente distinguíveis entre si.
- **FR-003**: O sistema MUST exigir que o operador selecione um layout antes de prosseguir para os formulários básicos de setup.
- **FR-004**: O sistema MUST registrar qual layout foi escolhido para a partida em configuração.
- **FR-005**: O sistema MUST encaminhar o operador para o setup básico atual imediatamente após a escolha de um layout válido.
- **FR-006**: O sistema MUST manter os formulários básicos com o mesmo modelo operacional atual depois que o layout for escolhido.
- **FR-007**: O sistema MUST preservar os comportamentos existentes de ocultação e reabertura do sidebar de setup após a introdução da galeria de layouts.
- **FR-008**: O sistema MUST manter a escolha de layout associada à partida em uso durante o restante do fluxo de configuração e operação.
- **FR-009**: O sistema MUST deixar visível para o operador qual layout está selecionado enquanto a partida estiver sendo configurada ou operada.
- **FR-010**: O sistema MUST permitir iniciar novas partidas escolhendo novamente um layout a partir da galeria antes do setup.
- **FR-011**: O sistema MUST manter a nova etapa compatível com o fluxo atual de login e com o carregamento de partida já existente no painel.
- **FR-012**: O sistema MUST evitar regressões no comportamento atual do painel para usuários que já conhecem o setup existente.

### Key Entities *(include if feature involves data)*

- **Opcao de Layout de Placar**: Representa uma alternativa visual de apresentação disponível para seleção na galeria inicial, com identificação estável, nome de exibição e prévia visual.
- **Seleção de Layout da Partida**: Representa a escolha do layout associada ao fluxo de configuração de uma partida específica e reaproveitada durante a operação.
- **Partida em Configuração**: Representa o contexto da partida após o login, incluindo a etapa inicial de escolha de layout e o setup básico já existente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das validações manuais do fluxo novo, a galeria de layouts aparece imediatamente após o login e antes do setup básico da partida.
- **SC-002**: Em pelo menos 95% das tentativas observadas, o operador consegue escolher um layout e chegar ao setup atual em até 15 segundos.
- **SC-003**: Em 100% dos testes de regressão do painel, a ocultação e reabertura do sidebar continuam funcionando como antes após a seleção do layout.
- **SC-004**: Em 100% das novas partidas criadas com a feature, o layout selecionado permanece identificável ao operador durante a configuração e a operação da partida.

## Assumptions

- A entrega inicial pode trabalhar com um conjunto fechado de layouts de placar definidos pelo produto para o painel atual.
- A escolha do layout acontece no fluxo do console manual já existente, sem criar uma área separada de autenticação ou administração.
- O layout selecionado influencia a apresentação da partida, mas não exige mudança estrutural nos formulários básicos atuais nesta primeira entrega.
- O comportamento existente de recolher e expandir o sidebar é considerado parte obrigatória da experiência atual e deve ser preservado.
- A feature se aplica a novas configurações de partida iniciadas após o login; ajustes mais profundos em overlays já em produção podem ser planejados depois, se necessário.
