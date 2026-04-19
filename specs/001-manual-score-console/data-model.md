# Data Model: Console Manual de Placar

## Entity: Game

**Purpose**: Representa uma partida identificada por URL unica e contendo o estado operacional exibido no painel e no overlay.

**Fields**:
- `gameId`: string curta unica e estavel por partida.
- `status`: enum `draft | live | paused | closed`.
- `createdAt`: timestamp UTC de criacao.
- `updatedAt`: timestamp UTC da ultima alteracao persistida.
- `currentPeriod`: inteiro entre `1` e `4`.
- `clock`: objeto `GameClock`.
- `homeTeam`: objeto `TeamState`.
- `awayTeam`: objeto `TeamState`.

**Validation Rules**:
- `gameId` deve ser unico e nao vazio.
- `currentPeriod` deve estar entre `1` e `4` nesta versao.
- `status` deve refletir coerencia com o estado do relogio.

**Relationships**:
- Um `Game` possui exatamente um `homeTeam`, um `awayTeam` e um `clock`.

## Entity: TeamState

**Purpose**: Representa o estado exibivel e editavel de um dos times da partida.

**Fields**:
- `side`: enum `home | away`.
- `name`: string nao vazia apos configuracao.
- `logoUrl`: string opcional com URL ou referencia valida de imagem.
- `score`: inteiro `>= 0`.
- `fouls`: inteiro `>= 0`.

**Validation Rules**:
- `score` nao pode ser negativo.
- `fouls` nao pode ser negativo.
- `name` deve aceitar edicao parcial durante configuracao, mas a partida so pode ser publicada como pronta quando ambos os nomes existirem.

## Entity: GameClock

**Purpose**: Representa o tempo restante do periodo atual e o estado do cronometro controlado manualmente segundo a regra FIBA.

**Fields**:
- `elapsedSeconds`: inteiro entre `0` e `600`, representando o tempo restante do periodo atual em segundos.
- `isRunning`: boolean.
- `lastStartedAt`: timestamp UTC opcional, preenchido quando o cronometro entra em execucao.

**Validation Rules**:
- `elapsedSeconds` nao pode ser negativo nem ultrapassar `600`.
- `lastStartedAt` deve ser nulo quando `isRunning` for `false`.

## Entity: AdminCredential

**Purpose**: Representa a configuracao de senha unica utilizada para autorizar operacoes administrativas.

**Fields**:
- `passwordSource`: enum `environment | local_settings`.
- `isConfigured`: boolean.

**Validation Rules**:
- Operacoes administrativas devem falhar se nenhuma senha estiver configurada.
- O valor real da senha nunca deve integrar respostas da API ou logs informativos.

## Entity: GameSnapshot

**Purpose**: Representa o documento serializado persistido em blob para restauracao do estado da partida.

**Fields**:
- `version`: inteiro da estrutura do documento.
- `game`: objeto `Game` completo.

**Validation Rules**:
- Todo snapshot deve conter `version` e `game`.
- A leitura deve rejeitar snapshots invalidos ou incompletos com erro controlado.

## State Transitions

### Game Status

- `draft -> live`: quando a partida esta configurada e o operador inicia operacao valida.
- `live -> paused`: quando o cronometro e pausado e a partida segue aberta.
- `paused -> live`: quando o cronometro e retomado.
- `live -> closed`: quando a partida e encerrada manualmente.
- `paused -> closed`: quando a partida e encerrada a partir de estado pausado.

### Period Progression

- `1 -> 2 -> 3 -> 4`: progressao manual valida e obrigatoriamente sequencial.
- A transicao para o proximo periodo so e valida quando `elapsedSeconds = 0` no periodo corrente.
- Permanecer no mesmo periodo e permitido apenas para correcoes operacionais que nao alterem `currentPeriod`.
- Qualquer valor fora de `1..4` e invalido nesta versao.

### Clock Transitions

- `stopped -> running`: ao iniciar o cronometro com tempo restante maior que `00:00`.
- `running -> paused`: ao pausar.
- `paused -> running`: ao retomar.
- `running -> stopped`: automaticamente ao atingir `00:00`.
- Mudancas de periodo redefinem `elapsedSeconds` para `600` e deixam o cronometro parado.
- Ajustes manuais de `elapsedSeconds` no periodo corrente nao mudam `currentPeriod` e podem ocorrer com o cronometro parado ou em execucao.
- Atualizacoes de `elapsedSeconds` devem preservar a faixa valida `0..600`.