import azure.functions as func
import requests, json, logging
from jinja2 import Environment, FileSystemLoader, select_autoescape

# SESI / Araraquara
# SESI / Araraquara
ENTITY_ID = "dd09acde-4392-11ee-895e-0bacda3bcd2b"

# Configuração do Jinja2 para carregar templates da pasta 'templates'
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

app = func.FunctionApp()

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
                return func.HttpResponse('Jogo do SESI não encontrado', status_code=404)
            if req.params.get('json') == '1':
                return func.HttpResponse(
                    json.dumps(dados),
                    mimetype="application/json"
                )
            # Renderiza o template HTML usando Jinja2
            template = env.get_template('placar.html')
            html_content = template.render(**dados)
            return func.HttpResponse(html_content, mimetype="text/html")
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
                    'nome_casa': time_casa.get('name', ''),
                    'nome_fora': time_fora.get('name', ''),
                    'placar_casa': time_casa.get('score', '0'),
                    'placar_fora': time_fora.get('score', '0'),
                }
    return None
