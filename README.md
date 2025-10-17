# 🏆 Placar SESI - Azure Functions

Sistema de placar em tempo real para jogos do SESI, desenvolvido com Azure Functions e JavaScript vanilla.

## 🚀 Funcionalidades

- **Placar em tempo real** - Atualização automática a cada 20 segundos
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

#### 📊 Dados JSON
```
GET /api/placar?competition={codigo}
```
Retorna apenas os dados do placar em formato JSON.

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

4. **Execute localmente:**
```bash
func start
```

5. **Acesse:**
```
http://localhost:7071/api/index?competition=SEU_CODIGO
```

### Deploy para Azure

```bash
func azure functionapp publish placarSesiFunctionApp
```

## 🌐 URLs de Produção

- **Interface:** `https://placarsesifunctionapp.azurewebsites.net/api/index?competition={codigo}`
- **API JSON:** `https://placarsesifunctionapp.azurewebsites.net/api/placar?competition={codigo}`

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Functions App                          │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   /api/index    │    │        /api/placar                  │ │
│  │                 │    │                                     │ │
│  │ • Serve HTML    │    │ • Consulta API externa              │ │
│  │ • CSS embutido  │    │ • Filtra dados do SESI              │ │
│  │ • JavaScript    │────┤ • Retorna JSON                      │ │
│  │                 │    │ • Headers anti-cache                │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
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
- **requests**: Cliente HTTP para consultar API externa

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