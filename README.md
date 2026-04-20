# 🏆 Placar SESI - Azure Functions

Sistema de placar em tempo real para jogos do SESI, com backend em Azure
Functions e frontend servido como HTML/CSS/JS vanilla.

## 🚀 Funcionalidades

- **Placar em tempo real** - Atualização automática a cada 20 segundos
- **Console manual protegido** - Painel autenticado por senha unica para operar placar, faltas, periodo e cronometro
- **Galeria de layouts apos o login** - Escolha visual obrigatoria do layout do placar antes do setup da partida
- **Overlay publico por jogo** - URL publica por partida para uso em Streamlabs e outras transmissões
- **Cronometro FIBA** - Contagem regressiva de 10 minutos por periodo, com pausa, retomada e reset ao trocar de quarto
- **Interface responsiva** - Adaptada para desktop e mobile
- **Cache otimizado** - Sem problemas de cache com dados antigos
- **API JSON** - Retorna dados estruturados para integração
- **Zero dependências frontend** - HTML/CSS/JS puro

## 📡 API

### Endpoints

#### 🎯 Interface Web (HTML)
```
GET /api/index?competition={codigo}
```
Retorna a interface HTML completa do placar.

#### 🎛️ Console Manual (HTML)
```
GET /api/control
```
Retorna o painel manual protegido por senha unica.

#### 📺 Overlay Publico por Jogo (HTML)
```
GET /api/overlay/{gameId}
```
Retorna o overlay publico de uma partida manual.

#### 📊 Dados JSON
```
GET /api/placar?competition={codigo}
```
Retorna apenas os dados do placar em formato JSON.

#### 🏀 Estado Publico de Partida Manual
```
GET /api/games/{gameId}
```
Retorna o estado atual de uma partida manual para o overlay.

#### 🔐 Sessao do Console
```
POST /api/control/session
```
Valida a senha unica do painel.

#### 🛠️ Criacao e Atualizacao de Partidas
```
POST /api/games
PATCH /api/games/{gameId}
DELETE /api/games/{gameId}
```
Permite criar, atualizar e encerrar partidas manuais com o header `X-Admin-Password`.

### Fluxo do console manual

1. Login com a senha administrativa em `/api/control`.
2. Escolha obrigatoria de um layout de placar na galeria exibida apos o login.
3. Setup normal da partida com escolha dos clubes mandante e visitante.
4. Operacao usual do painel, mantendo o comportamento existente de ocultacao e reabertura do sidebar.

### Exemplo de criacao de partida manual

```json
{
  "homeClubId": "sesi-araraquara",
  "awayClubId": "ad-santo-andre",
  "layoutId": "classic"
}
```

`layoutId` identifica o layout selecionado na galeria e passa a acompanhar o estado publico da partida.

### Parâmetros

- **competition** (obrigatório): Código identificador do jogo/competição

### Exemplo de Resposta JSON
```json
{
  "logo_casa": "https://example.com/logo1.png",
  "logo_fora": "https://example.com/logo2.png", 
  "nome_casa": "SESI Araraquara",
  "nome_fora": "Time Adversário",
  "placar_casa": "2",
  "placar_fora": "1"
}
```

## 🔧 Instalação e Deploy

### Pré-requisitos
- [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local)
- Python 3.10 ou 3.11
- Conta Azure

### Desenvolvimento Local

1. **Clone o repositório:**
```bash
git clone https://github.com/asdrub/placarSesiPy.git
cd placarSesiPy
```

2. **Configure ambiente virtual:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate     # Windows
```

3. **Instale dependências:**
```bash
pip install -r requirements.txt
```

4. **Instale as dependencias tambem para o worker local:**
```bash
python -m pip install --target=.python_packages/lib/site-packages -r requirements.txt
```

5. **Se usar `UseDevelopmentStorage=true`, inicie o Azurite**

6. **Execute localmente:**
```bash
PYTHONPATH="$PWD/.python_packages/lib/site-packages:$PYTHONPATH" func start
```

7. **Acesse:**
```
http://localhost:7071/api/index?competition=SEU_CODIGO
http://localhost:7071/api/control
```

### Deploy para Azure

```bash
func azure functionapp publish placarSesiFunctionApp
```

## 🌐 URLs de Produção

- **Interface:** `https://placarsesifunctionapp.azurewebsites.net/api/index?competition={codigo}`
- **Console manual:** `https://placarsesifunctionapp.azurewebsites.net/api/control`
- **Overlay manual:** `https://placarsesifunctionapp.azurewebsites.net/api/overlay/{gameId}`
- **API JSON:** `https://placarsesifunctionapp.azurewebsites.net/api/placar?competition={codigo}`

## 🏗️ Arquitetura

O runtime atual da Function App e Python. O frontend entregue ao navegador usa
JavaScript vanilla embutido no HTML. Qualquer migracao do backend para
JavaScript deve ser tratada como decisao de arquitetura e so vale quando reduzir
complexidade geral e custo operacional de forma objetiva.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Functions App                          │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   /api/index    │    │        /api/placar                  │ │
│  │                 │    │                                     │ │
│  │ • Overlay legado│    │ • Consulta API externa              │ │
│  │ • HTML embutido │    │ • Filtra dados do SESI              │ │
│  │ • Polling 20s   │────┤ • Retorna JSON                      │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │  /api/control   │    │      /api/games/{gameId}            │ │
│  │                 │    │                                     │ │
│  │ • Painel manual │    │ • Leitura publica do estado         │ │
│  │ • Senha unica   │────┤ • PATCH/DELETE autenticados         │ │
│  │ • Galeria layout│    │ • Persistencia em blob JSON         │ │
│  │ • Autosave      │    │ • layoutId persistido               │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
│                    ┌─────────────────────────────────────┐      │
│                    │    /api/overlay/{gameId}            │      │
│                    │ • Overlay publico por jogo          │      │
│                    │ • Polling curto                     │      │
│                    └─────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │     API Externa Atrium      │
                    │  (Fonte dos dados reais)    │
                    └─────────────────────────────┘
```

## 🎨 Customização

### Cores dos Times
As cores são definidas no CSS embutido no `function_app.py`:

```css
.time.aqa { background: #c00; }    /* Time casa - vermelho */
.time.ita { background: #1a9c2c; } /* Time fora - verde */
```

### Intervalo de Atualização
Para alterar o intervalo de atualização (padrão: 20 segundos):

```javascript
setInterval(atualizarPlacar, 20000); // 20000ms = 20s
```

## 🔍 Solução de Problemas

### Cache Persistente
Se os dados não atualizarem:
1. Verifique se o parâmetro `_ts` está sendo adicionado às requisições
2. Confirme os headers `cache: 'no-store'`
3. Use Ctrl+F5 para forçar refresh completo

### Erro de CORS
**Não deve acontecer** - HTML e API estão no mesmo domínio.

### Dados Não Encontrados
Verifique se:
- O código `competition` está correto
- A API externa está respondendo
- O ENTITY_ID do SESI está configurado corretamente

## 📝 Dependências

- **azure-functions**: Runtime do Azure Functions
- **azure-storage-blob**: Persistencia enxuta por blob JSON das partidas manuais
- **requests**: Cliente HTTP para consultar API externa

## ✅ Validacao rapida da nova feature

1. Inicie a Function App com `PYTHONPATH="$PWD/.python_packages/lib/site-packages:$PYTHONPATH" func start`.
2. Abra `http://localhost:7071/api/control`.
3. Faça login e confirme a exibicao da galeria de layouts antes do setup da partida.
4. Escolha um layout, crie a partida e verifique que o overlay continua acessivel pela URL gerada.

## 📐 Diretrizes de desenvolvimento

- Priorizar a menor solucao que resolva o caso de uso com clareza.
- Reaproveitar codigo e capacidades existentes antes de adicionar novas
  abstracoes ou dependencias.
- Manter o backend em Python por padrao; considerar JavaScript apenas com ganho
  comprovado de simplicidade ou leveza.
- Preservar uso enxuto de recursos e logs apenas nos pontos essenciais.
- Manter seguranca minima: segredos fora do codigo, validacao de entrada e erros
  sem exposicao excessiva.

As regras normativas completas estao em `.specify/memory/constitution.md`.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/asdrub/placarSesiPy/issues)
- **Email**: [Adicionar email de contato]

---

**Desenvolvido com ❤️ para acompanhar os jogos do SESI Araraquara em tempo real!**