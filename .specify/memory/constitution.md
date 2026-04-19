<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Principle 1 placeholder -> I. Simplicidade Antes de Tudo
- Principle 2 placeholder -> II. Reuso Sem Duplicacao
- Principle 3 placeholder -> III. Runtime Guiado por Evidencia
- Principle 4 placeholder -> IV. Leveza Operacional e Observabilidade Suficiente
- Principle 5 placeholder -> V. Seguranca Minima Obrigatoria
Added sections:
- Limites Tecnicos
- Fluxo de Trabalho e Revisao
Removed sections:
- None
Templates requiring updates:
- updated .specify/templates/plan-template.md
- updated .specify/templates/spec-template.md
- updated .specify/templates/tasks-template.md
- updated README.md
Follow-up TODOs:
- None
-->

# Placar SESI Constitution

## Core Principles

### I. Simplicidade Antes de Tudo
Toda mudanca MUST comecar pela menor solucao que resolva o problema atual com
clareza. Novas camadas, abstracoes, dependencias, arquivos ou servicos so podem
ser introduzidos quando a alternativa simples for insuficiente e essa decisao
estiver explicitamente justificada no plano. O objetivo e manter leitura,
manutencao e operacao baratas.

### II. Reuso Sem Duplicacao
Toda implementacao MUST verificar primeiro o que ja existe no repositorio e na
plataforma Azure Functions antes de criar nova logica. Reuso de funcoes,
helpers, contratos e comportamento existente e preferencial; duplicacao literal
ou conceitual MUST ser evitada. Extracoes de utilitarios so devem acontecer
quando reduzirem repeticao sem tornar o fluxo mais opaco.

### III. Runtime Guiado por Evidencia
Python e o runtime de referencia atual do backend. Migracao total ou parcial
para JavaScript so SHOULD acontecer quando houver evidencia objetiva de melhora
geral em simplicidade do codigo, leveza operacional, cold start, cadeia de
dependencias ou manutencao. Toda proposta de migracao MUST registrar ganho
esperado, custo de transicao e criterio de reversao; sem isso, a decisao padrao
permanece em Python.

### IV. Leveza Operacional e Observabilidade Suficiente
Cada entrega MUST privilegiar baixo consumo de memoria, poucas dependencias,
menos chamadas externas e configuracao enxuta. Timeouts, tratamento de falhas e
logs essenciais MUST existir nos pontos de integracao externos e nas rotas HTTP,
mas a instrumentacao MUST permanecer proporcional ao tamanho do sistema. O
projeto nao adota observabilidade pesada por padrao; coleta apenas o necessario
para diagnosticar falhas reais.

### V. Seguranca Minima Obrigatoria
Seguranca avancada nao e um objetivo central deste projeto, mas um patamar
minimo MUST ser mantido. Isso inclui nao expor segredos no codigo, validar
entradas externas, retornar erros sem vazar detalhes sensiveis e usar apenas o
nivel de permissao necessario na Azure Function e em integracoes auxiliares.
Sempre que simplicidade e seguranca entrarem em tensao, a escolha MUST manter o
minimo seguro sem transformar o projeto em uma arquitetura pesada.

## Limites Tecnicos

- O projeto MUST favorecer uma estrutura pequena e direta, com poucos modulos e
  responsabilidades explicitamente delimitadas.
- Novas dependencias de runtime MUST ser evitadas quando a biblioteca padrao ou
  a SDK ja existente resolverem o problema com clareza equivalente.
- Mudancas em chamadas externas MUST definir timeout, comportamento de erro e
  impacto esperado em latencia e uso de recursos.
- Novos servicos Azure, persistencia adicional ou filas so SHOULD ser adotados
  quando a necessidade operacional for concreta e documentada.

## Fluxo de Trabalho e Revisao

- Todo spec MUST declarar limites de escopo, expectativas de recurso e casos de
  falha relevantes para a entrega.
- Todo plan MUST registrar a verificacao de simplicidade, reuso, escolha de
  runtime e controles minimos de seguranca antes da implementacao.
- Todo tasks.md MUST incluir tarefas para revisar reuso, validar dependencias,
  proteger entradas e garantir logs essenciais quando a entrega tocar esses
  pontos.
- Code review MUST rejeitar complexidade nao justificada, duplicacao evitavel,
  migracao de runtime sem evidencia e qualquer regressao do baseline minimo de
  seguranca.
- Testes nao sao obrigatorios por volume, mas SHOULD cobrir transformacoes
  criticas, parsing, selecao de dados e regressos em integracoes externas
  quando esses riscos estiverem presentes.

## Governance

Esta constituicao prevalece sobre instrucoes locais de processo quando houver
conflito. Toda alteracao MUST atualizar tambem os templates afetados e qualquer
documentacao operacional que tenha ficado desalinhada.

Mudancas seguem versionamento semantico da constituicao: MAJOR para remocao ou
redefinicao incompativel de principios, MINOR para novos principios ou
expansoes normativas, PATCH para clarificacoes sem mudanca de direcao.

Toda proposta de emenda MUST registrar motivacao, impacto nos artefatos do Spec
Kit e verificacao de consistencia com README e guias de trabalho. Toda revisao
de implementacao SHOULD incluir uma checagem explicita contra estes principios.

**Version**: 1.0.0 | **Ratified**: 2026-04-18 | **Last Amended**: 2026-04-18
