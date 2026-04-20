# Research: Seletor de Clubes 2026

## Decision 1: Keep Python and the current Azure Functions route pattern

**Decision**: Manter o backend em Python e aplicar a feature dentro do padrao atual de Azure Functions que serve HTML e JSON a partir do mesmo app.

**Rationale**: A mudanca pedida e pequena e localizada: trocar campos livres por selecao predefinida, validar clube duplicado e propagar o resultado para o estado existente do jogo. O codigo atual ja possui rotas HTTP, persistencia em blob e renderizacao do painel e overlay. Reusar essa estrutura entrega a menor mudanca viavel.

**Alternatives considered**:
- Migrar parte da feature para um frontend separado: rejeitado por ampliar escopo e duplicar a cadeia de build.
- Migrar backend para JavaScript: rejeitado por nao trazer ganho objetivo de simplicidade ou leveza para um catalogo estatico.

## Decision 2: Implement the 2026 club list as a static in-repo catalog

**Decision**: Implementar a lista oficial dos 5 clubes de 2026 como um catalogo estatico no repositorio, com `clubId`, nome oficial e URL oficial de logo.

**Rationale**: O conjunto de opcoes foi explicitamente fixado na spec. Um catalogo local evita dependencia externa, reduz risco operacional, elimina necessidade de endpoint remoto e mantem o setup disponivel mesmo sem conectividade adicional alem da propria Function App.

**Alternatives considered**:
- Buscar clubes em API externa: rejeitado por custo operacional e aumento de falhas possiveis.
- Configurar clubes em arquivo externo editavel por ambiente: rejeitado por introduzir variabilidade desnecessaria para uma lista fechada nesta entrega.

## Decision 3: Preserve the existing public team shape and add optional club identity metadata

**Decision**: Preservar no estado publico da partida os campos atuais `name` e `logoUrl`, adicionando `clubId` como metadata opcional para jogos novos.

**Rationale**: Overlay, painel principal e persistencia atual ja consomem `name` e `logoUrl`. Manter esse formato reduz retrabalho e preserva compatibilidade com partidas antigas. `clubId` entra apenas como chave de validacao, rastreabilidade e futura reidratacao do catalogo sem quebrar leitores existentes.

**Alternatives considered**:
- Substituir `name` e `logoUrl` por objeto de clube aninhado: rejeitado por exigir refactor maior no painel, overlay e contrato existente.
- Nao persistir `clubId`: rejeitado por dificultar validacao consistente e suporte a jogos criados com o catalogo.

## Decision 4: Replace free-text setup fields with fixed-select controls and block direct name/logo editing in the main setup flow

**Decision**: Substituir os campos de texto de setup por seletores fechados de clube para mandante e visitante e remover a necessidade de digitar nome e URL de logo no fluxo principal.

**Rationale**: Esse e o comportamento central requerido pela spec. A troca reduz erro humano, padroniza nomes e logos e reaproveita o restante do fluxo de criacao de partida. O painel principal e o overlay continuam usando dados derivados da selecao.

**Alternatives considered**:
- Manter selecao e texto livre lado a lado: rejeitado por reintroduzir o problema de inconsistencia visual.
- Manter texto livre como fallback no fluxo principal: rejeitado por contrariar a substituicao pedida.

## Decision 5: Validate club selection at both creation and update boundaries

**Decision**: Validar o `clubId` permitido e a proibicao de usar o mesmo clube nos dois lados tanto na criacao da partida quanto em qualquer ajuste permitido antes do inicio.

**Rationale**: A regra de negocio precisa valer independentemente da origem da acao, inclusive chamadas HTTP diretas. Concentrar a validacao no backend preserva a seguranca minima do projeto e evita confiar apenas no comportamento da interface.

**Alternatives considered**:
- Validar apenas no JavaScript do painel: rejeitado por permitir bypass via chamadas diretas a API.
- Permitir o mesmo clube nos dois lados e alertar apenas visualmente: rejeitado por conflitar com requisito funcional explicito.

## Decision 6: Keep overlay rendering unchanged and update only the contracts that feed it

**Decision**: Manter a renderizacao do overlay sem mudancas estruturais, ajustando apenas o payload de criacao/atualizacao e o estado persistido que alimenta `name` e `logoUrl`.

**Rationale**: O overlay atual ja renderiza corretamente nomes e logos a partir do estado retornado por `/api/games/{gameId}`. Como a feature altera a origem desses dados, nao o formato de exibicao, a menor mudanca viavel e preservar a view publica.

**Alternatives considered**:
- Criar endpoint novo para catalogo consumido pelo overlay: rejeitado por nao gerar valor funcional.
- Refatorar o overlay para ler um objeto de clube novo: rejeitado por aumento de escopo sem necessidade.
