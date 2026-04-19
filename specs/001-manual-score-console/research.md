# Research: Console Manual de Placar

## Decision 1: Keep Python as the backend runtime

**Decision**: Manter o backend em Python e evitar migracao para JavaScript nesta feature.

**Rationale**: O projeto ja possui uma Function App Python funcional, com dependencias minimas e deploy simples. A feature adiciona operacao de estado, HTML adicional e novas rotas HTTP, mas nao exige nenhum padrao que torne JavaScript objetivamente mais simples ou mais leve. A migracao aumentaria custo de transicao, mudaria toolchain e nao reduz o numero de componentes necessarios.

**Alternatives considered**:
- Migrar todo o backend para JavaScript: rejeitado por aumento de escopo, toolchain paralelo e ausencia de ganho comprovado.
- Implementacao hibrida Python + JavaScript no backend: rejeitada por duplicar responsabilidades e elevar manutencao.

## Decision 2: Persist per-game state as JSON blobs in the Function App storage account

**Decision**: Persistir o estado de cada partida em um blob JSON na mesma storage account usada pela Function App, com uso opcional de cache em memoria apenas como otimizacao local.

**Rationale**: A feature exige que o estado nao se perca em recargas de pagina e precisa gerar URLs unicas por jogo. Estado apenas em memoria nao e confiavel em Azure Functions, porque nao sobrevive a recycle ou escala. Usar blob JSON reaproveita uma dependencia estrutural ja obrigatoria da plataforma, evita a introducao de um banco dedicado e mantem o modelo de leitura/escrita simples para volumes baixos.

**Alternatives considered**:
- Dicionario em memoria somente: rejeitado por nao ser autoritativo nem sobreviver a reinicio/escala.
- Azure Table Storage: rejeitado por adicionar modelagem e consultas desnecessarias para um documento pequeno por jogo.
- Cosmos DB ou Redis: rejeitados por custo e complexidade incompativeis com o MVP.

## Decision 3: Use short polling instead of real-time push infrastructure

**Decision**: Atualizar o overlay e o painel por polling HTTP curto, alvo de 1 a 2 segundos, em vez de usar WebSocket ou SignalR no MVP.

**Rationale**: A spec pede atualizacao em tempo real perceptivel, mas o volume e baixo e o fluxo e centrado em um operador principal. Polling curto em endpoints HTTP e suficiente para cumprir o objetivo de <=2s na maior parte dos casos, preserva a arquitetura stateless e reduz o numero de servicos, conexoes persistentes e pontos de falha.

**Alternatives considered**:
- Azure SignalR Service: rejeitado por adicionar servico e fluxo de conexao desproporcionais ao escopo.
- WebSocket customizado: rejeitado por complexidade operacional e menor aderencia ao modelo atual da Function App.
- Polling de 20 segundos como no overlay atual: rejeitado por nao atender o comportamento esperado da mesa de controle ao vivo.

## Decision 4: Model admin authentication as a single configured password

**Decision**: Modelar autenticacao administrativa como uma senha unica configurada fora do codigo-fonte e validada nas operacoes de painel/estado.

**Rationale**: A spec pede explicitamente autenticacao simples por senha unica. Isso atende o baseline minimo de seguranca do projeto sem introduzir usuarios, sessoes complexas ou provedores externos. O segredo deve vir de configuracao local e de ambiente no Azure, nunca hardcoded em texto real de producao.

**Alternatives considered**:
- OAuth ou Entra ID: rejeitados por excesso de complexidade e desvio do escopo.
- Painel totalmente anonimo: rejeitado por conflito direto com a spec e com a constituicao.
- Senha embutida literalmente no repositorio: rejeitada por violar o minimo de seguranca exigido.

## Decision 5: Reuse the current route-serving pattern and isolate only state-specific logic

**Decision**: Reaproveitar o padrao atual de rotas HTTP que servem HTML e JSON, isolando apenas a logica de validacao e persistencia de estado se o crescimento do `function_app.py` justificar isso.

**Rationale**: O repositorio e pequeno e hoje concentra a app num unico arquivo. A menor mudanca viavel e manter o ponto de entrada atual, criar as novas rotas administrativas/publicas e extrair apenas helpers puros de estado, validacao e storage caso isso reduza repeticao e facilite testes. Isso evita um refactor estrutural desnecessario.

**Alternatives considered**:
- Refatorar para multi-package completo: rejeitado por expandir o escopo sem necessidade funcional.
- Manter absolutamente tudo num unico arquivo sem criterio: rejeitado porque duas UIs e varias operacoes de estado podem degradar legibilidade rapidamente.

## Decision 6: Define the public contract around game-centric endpoints

**Decision**: Estruturar o contrato em torno de um identificador unico de partida e endpoints separados para criar, consultar e atualizar seu estado, alem das paginas HTML do painel e do overlay.

**Rationale**: O requisito central e a existencia de uma URL unica por jogo e a sincronizacao do mesmo estado entre controle e apresentacao. Um contrato orientado a `gameId` reduz acoplamento com a origem antiga de dados por `competition` e facilita persistencia, validacao e testes de integracao.

**Alternatives considered**:
- Manter o modelo antigo baseado apenas em `competition`: rejeitado porque a feature passou a depender de estado manual e autenticado, nao apenas de consulta externa.
- Endpoint unico para HTML e estado: rejeitado por misturar responsabilidades e tornar cache/seguranca mais opacos.