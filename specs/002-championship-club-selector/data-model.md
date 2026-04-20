# Data Model: Seletor de Clubes 2026

## Entity: ChampionshipClub

**Purpose**: Representa um clube oficial disponivel para selecao no setup da partida.

**Fields**:
- `clubId`: identificador estavel e unico do clube, usado em validacao e persistencia.
- `displayName`: nome oficial de exibicao usado no painel e no overlay.
- `logoUrl`: URL oficial do logo usada na apresentacao do jogo.
- `season`: marcador do catalogo ativo, fixado em `2026` nesta entrega.

**Validation Rules**:
- `clubId` deve ser unico dentro do catalogo.
- `displayName` deve ser nao vazio.
- `logoUrl` deve ser nao vazia para todas as entradas aprovadas nesta entrega.
- O catalogo ativo deve conter exatamente os 5 clubes definidos na spec.

**Relationships**:
- Um `ChampionshipClub` pode ser associado ao lado mandante ou visitante de uma `Game`.

## Entity: TeamSelection

**Purpose**: Representa o lado da partida configurado a partir de um clube oficial e os dados derivados usados na exibicao.

**Fields**:
- `side`: enum `home | away`.
- `clubId`: referencia ao `ChampionshipClub` escolhido para o lado.
- `name`: nome oficial resolvido a partir do catalogo e persistido no estado do jogo.
- `logoUrl`: logo oficial resolvido a partir do catalogo e persistido no estado do jogo.
- `score`: inteiro `>= 0`.
- `fouls`: inteiro `>= 0`.

**Validation Rules**:
- `clubId` deve existir no catalogo oficial quando presente.
- `home.clubId` e `away.clubId` nao podem ser iguais na mesma partida.
- `name` e `logoUrl` de jogos novos devem refletir exatamente o clube selecionado.
- `score` nao pode ser negativo.
- `fouls` nao pode ser negativo.

**Relationships**:
- Uma `Game` possui exatamente duas `TeamSelection`, uma para `home` e outra para `away`.

## Entity: Game

**Purpose**: Representa a partida operada no painel e exibida no overlay.

**Fields**:
- `gameId`: identificador unico e estavel da partida.
- `status`: enum `draft | live | paused | closed`.
- `createdAt`: timestamp UTC de criacao.
- `updatedAt`: timestamp UTC da ultima alteracao persistida.
- `currentPeriod`: inteiro entre `1` e `4`.
- `clock`: objeto de tempo restante do periodo atual.
- `homeTeam`: objeto `TeamSelection`.
- `awayTeam`: objeto `TeamSelection`.

**Validation Rules**:
- `gameId` deve ser unico e nao vazio.
- `currentPeriod` deve permanecer entre `1` e `4`.
- Partidas novas devem ter `homeTeam.clubId` e `awayTeam.clubId` preenchidos antes da criacao.
- Partidas antigas sem `clubId` continuam legiveis, desde que mantenham `name` e `logoUrl` nos formatos atuais.

**Relationships**:
- Uma `Game` referencia dois clubes do catalogo por meio de `homeTeam.clubId` e `awayTeam.clubId` quando criada pelo fluxo novo.

## Entity: ClubCatalogSnapshot

**Purpose**: Representa o conjunto de clubes oficiais disponibilizado para a UI e para as validacoes do backend durante a temporada 2026.

**Fields**:
- `season`: valor fixo `2026`.
- `clubs`: lista ordenada de `ChampionshipClub`.

**Validation Rules**:
- A lista deve conter somente entradas aprovadas pela spec.
- A lista deve ser estavel durante a execucao da feature, sem depender de carga remota.

## State Transitions

### Team Selection Lifecycle

- `empty -> selected`: quando o operador escolhe um clube valido para um lado da partida.
- `selected -> replaced`: quando o operador troca o clube por outro da lista oficial antes da confirmacao valida da configuracao.
- `selected -> invalid`: quando a escolha resulta no mesmo `clubId` nos dois lados; a partida nao pode ser criada ou atualizada nesse estado.

### Game Creation Readiness

- `incomplete setup -> ready`: quando `homeTeam.clubId` e `awayTeam.clubId` estao preenchidos com clubes distintos do catalogo.
- `ready -> created`: quando a criacao persiste a partida com `clubId`, `name` e `logoUrl` derivados para ambos os lados.
- `legacy loaded -> readable`: quando uma partida antiga sem `clubId` e carregada e continua exibivel com os campos historicos existentes.
