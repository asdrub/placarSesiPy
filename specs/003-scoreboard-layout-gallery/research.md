# Research: Galeria de Layouts de Placar

## Decision 1: Inserir uma etapa `galleryPanel` entre login e setup

- Decision: Adicionar uma secao nova no mesmo `#configPanel`, exibida logo apos o login e antes do `gamePanel` atual.
- Rationale: O fluxo atual ja alterna paineis via classes `hidden`, e a funcao `setConfigOpen()` ja governa o recolhimento lateral sem depender de uma estrutura extra. Inserir a galeria como uma etapa intermediaria reaproveita o sidebar atual e evita criar rota, pagina ou shell novos.
- Alternatives considered:
  - Abrir a galeria em modal sobre o painel: rejeitado porque introduz outro mecanismo de foco, empilha estados visuais e aumenta risco de conflito com a barra lateral.
  - Criar uma nova pagina antes de `/api/control`: rejeitado porque duplicaria autenticacao e quebraria o fluxo atual do console manual.

## Decision 2: Persistir `layoutId` no nivel da partida

- Decision: Armazenar `layoutId` diretamente no objeto `game` salvo no blob JSON e devolvido por `GET /api/games/{gameId}`.
- Rationale: O layout e metadado da partida, nao de um time nem da sessao local. Persistir no nivel raiz da partida garante consistencia entre painel, overlay e recargas de pagina, alem de manter a estrutura atual do blob com extensao minima.
- Alternatives considered:
  - Guardar a selecao apenas em `sessionStorage`: rejeitado porque a escolha se perderia em reloads e nao chegaria ao overlay.
  - Guardar o layout fora do objeto `game`: rejeitado porque criaria outra fonte de verdade e complicaria a serializacao.

## Decision 3: Tratar o catalogo de layouts como lista estatica local

- Decision: Definir um catalogo fechado de layouts com `layoutId`, `displayName` e metadados de preview, injetado no HTML do painel e validado no backend.
- Rationale: A spec pede uma galeria antes do setup, mas nao pede gerenciamento dinamico. Lista estatica reduz superficie de falha, dispensa endpoint adicional e segue o principio de simplicidade da constituicao.
- Alternatives considered:
  - Buscar layouts de um endpoint JSON dedicado: rejeitado porque adiciona chamada HTTP e manutencao sem necessidade comprovada.
  - Configurar layouts via arquivo externo ou CMS: rejeitado porque aumenta variaveis operacionais para um conjunto pequeno e estavel de opcoes.

## Decision 4: Permitir troca de layout apenas em `draft`

- Decision: Aceitar `layoutId` em criacao de partida e em `PATCH /api/games/{gameId}` apenas enquanto o status da partida for `draft`.
- Rationale: Isso preserva previsibilidade visual durante a operacao e segue o mesmo principio usado para impedir alteracoes estruturais relevantes depois que a partida entra em estados operacionais. Tambem reduz risco de mudanca brusca no overlay ao vivo.
- Alternatives considered:
  - Permitir troca de layout em qualquer status: rejeitado por risco operacional e de inconsistencias visuais no ar.
  - Tornar o layout imutavel logo apos a criacao: rejeitado porque impediria ajuste fino enquanto o setup ainda esta em preparacao.

## Decision 5: Fazer o overlay escolher a apresentacao a partir do `layoutId`

- Decision: Manter um unico endpoint `/api/overlay/{gameId}` e selecionar o markup/CSS variante no cliente ou no HTML servido, com base no `layoutId` presente no estado da partida.
- Rationale: Preserva a URL publica atual, evita proliferacao de rotas e mantém retrocompatibilidade para jogos antigos sem `layoutId`, que podem cair no layout padrao atual.
- Alternatives considered:
  - Criar um endpoint por layout: rejeitado porque duplica superficie HTTP e obriga o operador a lidar com URLs diferentes.
  - Renderizar apenas um layout e usar a galeria como preferencia cosmetica do setup: rejeitado porque nao entregaria valor real ao pedido de multiplos layouts de placar.
