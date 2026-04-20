# Data Model: Galeria de Layouts de Placar

## Entity: ScoreboardLayoutOption

**Purpose**: Representa uma opcao oficial de layout disponivel para selecao na galeria inicial do painel.

**Fields**:
- `layoutId`: identificador estavel e unico do layout.
- `displayName`: nome visivel ao operador na galeria.
- `previewLabel`: texto curto de apoio para explicar o estilo do layout.
- `previewAsset`: referencia visual usada como miniatura ou bloco de preview.
- `isDefault`: marcador do layout padrao atual.

**Validation Rules**:
- `layoutId` deve ser unico dentro do catalogo.
- `displayName` deve ser nao vazio.
- O catalogo deve conter apenas layouts aprovados para a entrega.
- Deve existir exatamente um layout padrao para fallback de partidas antigas.

**Relationships**:
- Um `ScoreboardLayoutOption` pode ser selecionado por uma `GameLayoutSelection`.

## Entity: GameLayoutSelection

**Purpose**: Representa a escolha do layout associada a uma partida em configuracao ou operacao.

**Fields**:
- `layoutId`: referencia ao layout escolhido.
- `selectedAt`: timestamp logico da escolha mais recente.
- `source`: origem da escolha, normalmente `gallery`.

**Validation Rules**:
- `layoutId` deve existir no catalogo de layouts quando presente.
- A selecao so pode ser alterada enquanto a partida estiver em `draft`.
- Partidas antigas sem `layoutId` permanecem legiveis usando fallback para o layout padrao.

**Relationships**:
- Uma `Game` possui zero ou uma `GameLayoutSelection` persistida.

## Entity: Game

**Purpose**: Representa a partida operada no painel, agora com escolha de layout persistida alem dos dados ja existentes de placar.

**Fields**:
- `gameId`: identificador unico da partida.
- `status`: enum `draft | live | paused | closed`.
- `createdAt`: timestamp UTC de criacao.
- `updatedAt`: timestamp UTC da ultima alteracao persistida.
- `currentPeriod`: inteiro entre `1` e `4`.
- `clock`: estado do cronometro.
- `homeTeam`: selecao de clube do mandante.
- `awayTeam`: selecao de clube do visitante.
- `layoutId`: identificador do layout visual selecionado para a partida.

**Validation Rules**:
- `layoutId` deve ser obrigatorio para novas partidas criadas pelo fluxo com galeria.
- `layoutId` deve pertencer ao catalogo oficial de layouts.
- `layoutId` nao pode ser alterado quando `status != draft`.
- Partidas legadas sem `layoutId` devem continuar exibiveis com fallback para o layout padrao.

**Relationships**:
- Uma `Game` referencia um `ScoreboardLayoutOption` por meio de `layoutId`.

## Entity: LayoutGallerySession

**Purpose**: Representa o estado transitório do operador entre login e setup, enquanto ainda nao existe uma partida persistida.

**Fields**:
- `isAuthenticated`: indica que o login foi concluido.
- `selectedLayoutId`: layout escolhido antes da criacao da partida.
- `canProceedToSetup`: indica se o setup pode ser liberado.

**Validation Rules**:
- `selectedLayoutId` deve ser obrigatorio antes de liberar o setup.
- A sessao nao substitui a persistencia definitiva no objeto `Game`.

## State Transitions

### Layout Selection Lifecycle

- `not-selected -> selected`: quando o operador escolhe um layout valido na galeria.
- `selected -> replaced`: quando o operador troca para outro layout ainda durante `draft`.
- `selected -> locked`: quando a partida deixa de estar em `draft` e a troca de layout passa a ser bloqueada.

### Panel Flow Lifecycle

- `login -> gallery`: quando a autenticacao do painel e concluida com sucesso.
- `gallery -> setup`: quando um layout valido e escolhido.
- `setup -> live-operation`: quando a partida ja criada entra no fluxo operacional normal do painel.

### Legacy Compatibility

- `legacy-without-layout -> readable`: quando uma partida antiga e carregada e recebe fallback visual para o layout padrao sem quebrar painel nem overlay.
