import azure.functions as func
import requests, json, logging

# SESI / Araraquara
ENTITY_ID = "dd09acde-4392-11ee-895e-0bacda3bcd2b"

app = func.FunctionApp()

@app.route(route="index", auth_level=func.AuthLevel.ANONYMOUS)
def index(req: func.HttpRequest) -> func.HttpResponse:
    """Serve o HTML estático do placar"""
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Placar SESI Basquete (Overlay)</title>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      background: transparent;
      display: flex;
      justify-content: left;
      align-items: center;
      font-family: 'Arial Black', 'Segoe UI', sans-serif;
      color: transparent;
    }

    .placar-container {
      display: flex;
      flex-direction: column;
      gap: 6px;
      animation: fadeInUp 3s ease-out;
    }

    .linha-time {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 160px;
      gap: 10px;
    }

    .logo-time {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      object-fit: cover;
      background-color: #fff;
      box-shadow: 0 0 6px rgba(0,0,0,0.4);
    }

    .time {
      flex: 1;
      text-align: center;
      font-size: 0.5rem;
      font-weight: 700;
      letter-spacing: 0.5px;
      border-radius: 6px;
      padding: 8px 10px;
      color: #fff;
      text-shadow: 5px 5px 5px rgba(0,0,0,0.4);
    }

    .time.casa {
      background-color: #d62828; /* vermelho SESI */
    }

    .time.fora {
      background-color: #3a3a3a; /* cinza SESI */
    }

    .centro {
      background-color: #ffffff;
      color: #000;
      font-size: 0.95rem;
      font-weight: 700;
      text-align: center;
      padding: 10px 0;
      width: 160px;
      border-radius: 6px;
      box-shadow: 0 0 8px rgba(0,0,0,0.25);
    }

    .cronometro {
      background-color: #ffffff;
      color: #000;
      padding: 6px 18px;
      font-weight: 800;
      font-size: 0.65rem;
      text-align: center;
      border-radius: 4px;
      box-shadow: 0 0 10px rgba(0,0,0,0.25);
    }

    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  </style>
</head>
<body>

  <div class="placar-container">

    <div class="linha-time">
      <img id="logo_casa" class="logo-time" src="" alt="Logo Casa">
      <div id="nome_casa" class="time casa"></div>
    </div>

    <div class="linha-time">
        <div id="nome_fora" class="time fora"></div>
        <img id="logo_fora" class="logo-time" src="" alt="Logo Fora">
    </div>

    <div id="placar" class="centro"></div>

    <!--<div id="cronometro" class="cronometro">03:25</div>-->
    
  </div>

    <script>
        // Extrai o parâmetro competition da URL atual
        const urlParams = new URLSearchParams(window.location.search);
        const competition = urlParams.get('competition');
        
        // URL da API (mesmo domínio - sem CORS!)
        const API_URL = '/api/placar';

        function atualizarPlacar() {
            if (!competition) {
                document.getElementById('error').textContent = 'Parâmetro competition não encontrado na URL';
                document.getElementById('error').style.display = 'block';
                document.getElementById('loading').style.display = 'none';
                return;
            }

            const apiUrl = `${API_URL}?competition=${encodeURIComponent(competition)}&_ts=${Date.now()}`;
            
            fetch(apiUrl, { 
                cache: 'no-store',
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                // Atualiza o DOM com os dados
                document.getElementById('logo_casa').src = data.logo_casa || '';
                document.getElementById('logo_fora').src = data.logo_fora || '';
                document.getElementById('nome_casa').textContent = data.nome_casa || 'Time Casa';
                document.getElementById('nome_fora').textContent = data.nome_fora || 'Time Fora';
                document.getElementById("placar").textContent = `${data.placar_casa || '0'} - ${data.placar_fora || '0'}`;

                
                // Esconde loading e error
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'none';
            })
            .catch(err => {
                console.error('Erro ao buscar placar:', err);
                document.getElementById('error').textContent = `Erro: ${err.message}`;
                document.getElementById('error').style.display = 'block';
                document.getElementById('loading').style.display = 'none';
            });
        }

        // Carrega o placar imediatamente
        atualizarPlacar();

        // Atualiza a cada 20 segundos
        setInterval(atualizarPlacar, 20000);
    </script>
</body>
</html>"""
    
    return func.HttpResponse(html_content, mimetype="text/html")

@app.route(route="placar", auth_level=func.AuthLevel.ANONYMOUS)
def placar(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    competition = req.params.get('competition')
    if not competition:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None
        if req_body:
            competition = req_body.get('competition')

    if competition:
        API_PREFIX = "https://eapi.web.prod.cloud.atriumsports.com/v1/embed/235/fixtures"
        url = f"{API_PREFIX}?state={competition}"
        try:
            dados = get_placar_data(url)
            if not dados:
                return func.HttpResponse(
                    json.dumps({'error': 'Jogo do SESI?'}),
                    mimetype="application/json",
                    status_code=404
                )
            # Sempre retorna JSON
            return func.HttpResponse(
                json.dumps(dados),
                mimetype="application/json"
            )
        except Exception as e:
            return func.HttpResponse(f'Erro: {e}', status_code=500)
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a competition in the query string or in the request body for a personalized response.",
            status_code=401
        )
    
def get_placar_data(url):
    # Busca o JSON bruto da API
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    # Salva o conteúdo de data em um arquivo JSON
    #with open('data.json', 'w', encoding='utf-8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=2)
    fixtures = data.get('data', {}).get('fixtures', [])
    for fixture in fixtures:
        competitors = fixture.get('competitors', [])
        if any(c.get('entityId') == ENTITY_ID for c in competitors):
            if len(competitors) == 2:
                time_casa = next((c for c in competitors if c.get('isHome')), competitors[0])
                time_fora = next((c for c in competitors if not c.get('isHome')), competitors[1])
                # Dados para o template
                return {
                    'logo_casa': time_casa.get('logo', ''),
                    'logo_fora': time_fora.get('logo', ''),
                    'nome_casa': time_casa.get('code', ''),
                    'nome_fora': time_fora.get('code', ''),
                    'placar_casa': time_casa.get('score', '0'),
                    'placar_fora': time_fora.get('score', '0'),
                }
    return None
