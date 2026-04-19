# Feature Specification: Console Manual de Placar

**Feature Branch**: `[001-manual-score-console]`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "Aplicativo de placar para basquete com painel manual de controle e interface publica de apresentacao em tempo real"

## Clarifications

### Session 2026-04-19

- Q: O placar deve suportar marcacao dos periodos do jogo? → A: Sim, o sistema deve permitir marcar e exibir os 4 periodos regulamentares do basquete.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Operar o placar ao vivo (Priority: P1)

Como operador da mesa, eu quero atualizar pontos, faltas, periodo atual e tempo de jogo em uma interface simples para manter o placar oficial sincronizado durante a partida.

**Why this priority**: Sem esse fluxo, o produto nao entrega valor principal, porque a transmissao depende de um estado de placar correto e atualizado ao vivo.

**Independent Test**: Pode ser testado de forma independente ao abrir uma partida no painel de controle, alterar pontos, faltas, periodo e cronometro, e verificar que o estado exibido no painel muda imediatamente sem acao adicional.

**Acceptance Scenarios**:

1. **Given** que uma partida esta aberta no painel de controle, **When** o operador pressiona um botao de `+1`, `+2` ou `+3` para um dos times, **Then** o placar desse time e atualizado imediatamente.
2. **Given** que uma partida esta aberta no painel de controle, **When** o operador altera manualmente o valor do placar ou das faltas de um time, **Then** o novo valor passa a valer sem exigir botao de envio.
3. **Given** que o cronometro da partida esta parado em 10:00, **When** o operador inicia a contagem, **Then** o tempo passa a ser decrementado automaticamente ate que o operador pause o cronometro ou o periodo chegue a 00:00.
4. **Given** que o cronometro esta em andamento, **When** o operador pausa e depois retoma a contagem, **Then** o tempo permanece congelado durante a pausa e volta a ser decrementado a partir do valor anterior.
5. **Given** que a partida esta em um periodo regulamentar, **When** o operador marca o periodo atual entre primeiro, segundo, terceiro ou quarto, **Then** o painel e a exibicao publica passam a mostrar imediatamente o periodo selecionado.
6. **Given** que um periodo ja foi iniciado, **When** o operador tenta ativar novamente o botao desse mesmo periodo ou pular para um periodo posterior sem que o cronometro atual tenha chegado a `00:00`, **Then** a interface deve impedir a acao e liberar apenas o proximo periodo sequencial apos o encerramento do periodo corrente.
7. **Given** que o operador precisa corrigir o tempo restante do periodo atual, **When** informa manualmente um novo valor valido para o cronometro, **Then** o sistema ajusta o periodo corrente sem trocar de quarto e preserva a possibilidade de continuar a contagem regressiva a partir desse novo valor.
8. **Given** que a partida entra em operacao fora do estado `draft`, **When** o painel de controle e exibido, **Then** a area lateral de configuracao da partida deve ser recolhida automaticamente para priorizar os controles do jogo.
9. **Given** que a area lateral de configuracao foi recolhida, **When** o operador aciona o botao hamburguer no topo da pagina, **Then** a configuracao completa da partida deve ser exibida novamente sem ser ocultada automaticamente na sequencia.

---

### User Story 2 - Configurar a partida e controlar acesso (Priority: P2)

Como operador da mesa, eu quero preparar os dados basicos da partida e acessar o painel por senha unica para iniciar a operacao com rapidez e sem expor o controle ao publico.

**Why this priority**: A operacao depende de contexto correto da partida e de um bloqueio minimo de acesso ao painel administrativo.

**Independent Test**: Pode ser testado de forma independente ao entrar no painel com a senha configurada, informar dados dos times e confirmar que o placar fica pronto para uso.

**Acceptance Scenarios**:

1. **Given** que o operador acessa o painel de controle, **When** informa a senha configurada corretamente, **Then** o painel e liberado para edicao.
2. **Given** que o operador esta no painel autenticado, **When** informa nome e identificacao visual de cada time, **Then** esses dados ficam associados a partida em edicao.
3. **Given** que uma partida ainda nao foi configurada, **When** o operador cria uma nova partida, **Then** o sistema gera uma URL publica unica para a apresentacao desse jogo.
4. **Given** que a partida ja foi criada, **When** o operador precisa ajustar logos ou metadados basicos, **Then** essas alteracoes devem permanecer concentradas no painel lateral de configuracao, sem duplicacao desses campos no painel principal de controle do jogo.
5. **Given** que o operador prefere outro contraste visual, **When** aciona o switch de tema no topo do painel, **Then** o painel completo deve alternar entre modo claro e modo escuro preservando a preferencia entre recargas da pagina.

---

### User Story 3 - Exibir o placar na transmissao (Priority: P3)

Como produtor de transmissao, eu quero abrir uma URL publica do jogo e receber as alteracoes do placar em tempo quase imediato para usar essa tela como camada de exibicao no software de streaming.

**Why this priority**: A interface publica completa a entrega do produto ao tornar o estado operado na mesa reutilizavel na transmissao sem passos manuais extras.

**Independent Test**: Pode ser testado de forma independente ao abrir a URL publica de uma partida em um navegador separado e confirmar que a exibicao acompanha as alteracoes feitas no painel de controle sem autenticacao.

**Acceptance Scenarios**:

1. **Given** que existe uma partida configurada, **When** a URL publica correspondente e aberta, **Then** o placar e mostrado em modo somente leitura sem exigir autenticacao.
2. **Given** que a interface publica da partida esta aberta, **When** o operador altera pontos, faltas, nomes, logos ou cronometro no painel de controle, **Then** a interface publica reflete o novo estado automaticamente.
3. **Given** que a interface publica da partida esta aberta, **When** o operador muda o periodo atual do jogo no painel de controle, **Then** a exibicao publica mostra o periodo atualizado sem exigir recarga manual.

### Edge Cases

- O sistema deve impedir que pontos, faltas ou tempo assumam valores negativos apos erro operacional ou correcao manual.
- O sistema deve impedir a selecao de um periodo fora dos 4 periodos regulamentares suportados por esta entrega.
- Se a interface publica for aberta antes da configuracao completa da partida, ela deve mostrar um estado inicial claro em vez de dados quebrados ou parciais.
- Se o painel de controle for recarregado durante uma partida em andamento, o estado atual do jogo deve reaparecer sem reiniciar o placar.
- Se o operador reabrir a area lateral pelo botao hamburguer durante uma partida em andamento, ela deve permanecer visivel ate nova acao explicita do operador.
- Se duas alteracoes forem feitas em sequencia muito rapida, a interface publica deve refletir a ordem mais recente sem exibir um estado inconsistente prolongado.
- Se a senha informada estiver incorreta, o painel deve negar acesso sem revelar detalhes desnecessarios sobre a configuracao interna.

## Constraints *(mandatory)*

- **CT-001**: A feature MUST manter a operacao do placar no menor fluxo possivel, priorizando uma tela de controle simples e uma tela publica de exibicao.
- **CT-002**: A feature MUST reaproveitar o modelo atual de app enxuto e evitar fluxos duplicados para atualizacao de placar, faltas e cronometro.
- **CT-003**: A feature MUST limitar dependencias operacionais ao necessario para suportar atualizacao quase em tempo real e acesso publico por URL unica de jogo.
- **CT-004**: A feature MUST aplicar seguranca minima ao painel de controle, protegendo o acesso por senha unica, validando entradas operacionais e evitando exposicao desnecessaria de erros ou segredos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST permitir criar e identificar uma partida de basquete para operacao manual do placar.
- **FR-002**: O sistema MUST exigir uma senha unica preconfigurada para liberar acesso ao painel de controle.
- **FR-003**: O sistema MUST permitir informar e atualizar o nome exibido de cada time da partida.
- **FR-004**: O sistema MUST permitir associar uma identificacao visual a cada time para uso na exibicao publica.
- **FR-005**: O sistema MUST permitir adicionar 1, 2 ou 3 pontos a qualquer time por meio de controles dedicados e visiveis.
- **FR-006**: O sistema MUST permitir corrigir manualmente o placar de qualquer time para um valor arbitrario valido.
- **FR-007**: O sistema MUST permitir registrar e corrigir faltas por time.
- **FR-008**: O sistema MUST aplicar alteracoes de placar, faltas, nomes, identificacao visual e cronometro assim que o operador concluir cada edicao, sem exigir envio explicito por botao de confirmacao.
- **FR-009**: O sistema MUST permitir marcar o periodo atual da partida entre os 4 periodos regulamentares do jogo de basquete.
- **FR-010**: O sistema MUST disponibilizar um cronometro regressivo de 10 minutos por periodo que possa ser iniciado, pausado e retomado pelo operador.
- **FR-011**: O sistema MUST decrementar automaticamente o cronometro enquanto ele estiver em execucao, parar em 00:00 e preservar o tempo restante ao pausar.
- **FR-018**: O sistema MUST reiniciar o cronometro do periodo para 10:00 quando o operador trocar o periodo atual entre os 4 periodos regulamentares da FIBA.
- **FR-019**: O sistema MUST permitir avancar o periodo apenas de forma sequencial, liberando o proximo quarto somente quando o cronometro do periodo atual tiver chegado a `00:00`.
- **FR-020**: O sistema MUST impedir no painel a reativacao do botao do periodo atual e o salto para periodos futuros fora da sequencia permitida.
- **FR-021**: O sistema MUST oferecer um ajuste manual do cronometro do periodo corrente sem trocar o periodo ativo.
- **FR-012**: O sistema MUST gerar uma URL publica unica por partida para a interface de apresentacao.
- **FR-013**: O sistema MUST disponibilizar a interface publica da partida sem autenticacao e em modo somente leitura.
- **FR-014**: O sistema MUST refletir automaticamente na interface publica toda alteracao valida feita no painel de controle para a mesma partida, incluindo o periodo atual.
- **FR-015**: O sistema MUST preservar o estado atual da partida para que uma recarga de pagina nao zere dados ja informados.
- **FR-016**: O sistema MUST validar entradas operacionais para impedir valores invalidos, especialmente numeros negativos, periodos fora da faixa suportada e dados obrigatorios ausentes.
- **FR-017**: O sistema MUST informar falhas de acesso ou atualizacao de forma clara ao operador, sem expor detalhes internos desnecessarios.
- **FR-022**: O sistema MUST recolher automaticamente o painel lateral de configuracao quando a partida entrar em operacao, priorizando a area do painel principal de controle.
- **FR-023**: O sistema MUST permitir reabrir e ocultar manualmente o painel lateral de configuracao por um botao hamburguer no topo da pagina sem reocultacao automatica imediata.
- **FR-024**: O sistema MUST manter a edicao de logos dos times apenas no painel de configuracao da partida, sem expor esses campos no painel principal de controle do jogo.
- **FR-025**: O sistema MUST oferecer um switch de tema claro/escuro para todo o painel administrativo e preservar a preferencia visual do operador entre recargas.

### Key Entities *(include if feature involves data)*

- **Partida**: Representa um jogo especifico com identificador unico, URL publica de exibicao, estado atual, periodo atual e metadados basicos de apresentacao.
- **Time**: Representa um dos lados da partida com nome exibido, identificacao visual, pontuacao atual e total de faltas.
- **Estado do Placar**: Representa o conjunto de valores operacionais da partida em um instante, incluindo pontuacoes, faltas, periodo atual, cronometro e momento da ultima atualizacao.
- **Sessao de Controle**: Representa o acesso autorizado ao painel administrativo por meio da senha unica preconfigurada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um operador consegue configurar uma nova partida, incluindo times e identificacao visual, em ate 2 minutos.
- **SC-002**: Pelo menos 95% das alteracoes feitas no painel de controle aparecem na interface publica correspondente em ate 2 segundos.
- **SC-003**: Em teste operacional guiado, o operador consegue registrar ou corrigir pontos, faltas, periodo atual e tempo de jogo em uma unica interacao, sem depender de submit manual, em pelo menos 90% das tentativas.
- **SC-004**: A URL publica de uma partida pode ser aberta por um produtor de transmissao e exibir o estado atual do jogo em ate 5 segundos em pelo menos 95% dos acessos validos.

## Assumptions

- Cada partida tera um operador principal por vez no painel de controle.
- As faltas serao controladas no nivel do time, nao por atleta individual, nesta primeira versao.
- A primeira versao suporta explicitamente os 4 periodos regulamentares do jogo e nao cobre regras adicionais de prorrogacao.
- O cronometro principal da partida seguira a regra FIBA de 10 minutos por periodo em contagem regressiva.
- A interface publica sera usada apenas para exibicao do placar e nao permitira edicao.
- Os dados de identificacao visual dos times serao fornecidos pelo operador em um formato pronto para exibicao pela aplicacao.
- Esta feature parte da estrutura atual do projeto e nao inclui mudanca de plataforma como objetivo desta entrega.