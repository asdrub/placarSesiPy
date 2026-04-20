import json
import logging
import os
from typing import Any, Dict, Optional
from urllib.parse import urlsplit

import azure.functions as func
import requests

from club_catalog import club_catalog
from scoreboard_layout_catalog import DEFAULT_LAYOUT_ID, scoreboard_layout_catalog
from scoreboard_state import BlobGameStore, GameNotFoundError, GameStateError, InvalidGameUpdate

# SESI / Araraquara
ENTITY_ID = "dd09acde-4392-11ee-895e-0bacda3bcd2b"
LEGACY_API_PREFIX = "https://eapi.web.prod.cloud.atriumsports.com/v1/embed/235/fixtures"
OVERLAY_POLL_MS = 1500

app = func.FunctionApp()
store = BlobGameStore(
    connection_string=os.getenv("AzureWebJobsStorage"),
    container_name=os.getenv("SCOREBOARD_STATE_CONTAINER", "games"),
)


def json_response(payload: Dict[str, Any], status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(payload), mimetype="application/json", status_code=status_code)


def no_content_response() -> func.HttpResponse:
    return func.HttpResponse(status_code=204)


def parse_json_request(req: func.HttpRequest) -> Dict[str, Any]:
    try:
        payload = req.get_json()
    except ValueError as exc:
        raise InvalidGameUpdate("Request body must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise InvalidGameUpdate("Request body must be a JSON object")
    return payload


def get_admin_password() -> str:
    return os.getenv("ADMIN_PASSWORD", "").strip()


def require_admin(req: func.HttpRequest) -> Optional[func.HttpResponse]:
    configured_password = get_admin_password()
    if not configured_password:
        logging.error("ADMIN_PASSWORD is not configured")
        return json_response({"error": "Administrative password is not configured"}, status_code=503)

    provided = req.headers.get("X-Admin-Password", "").strip()
    if provided != configured_password:
        return json_response({"error": "Unauthorized"}, status_code=401)
    return None


def base_url(req: func.HttpRequest) -> str:
    forwarded_proto = req.headers.get("x-forwarded-proto")
    host = req.headers.get("host")
    if host:
        proto = forwarded_proto or urlsplit(req.url).scheme or "http"
        if not forwarded_proto and host.startswith(("127.0.0.1", "localhost")):
            proto = "http"
        return f"{proto}://{host}"
    return req.url.split("/api/")[0]


def game_urls(req: func.HttpRequest, game_id: str) -> Dict[str, str]:
    root = base_url(req)
    return {
    "adminUrl": f"{root}/api/control?gameId={game_id}",
        "overlayUrl": f"{root}/api/overlay/{game_id}",
        "stateUrl": f"{root}/api/games/{game_id}",
    }


def overlay_html() -> str:
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Placar Overlay</title>
  <style>
    :root {{
      --panel: rgba(12, 19, 34, 0.82);
      --text: #f8fafc;
      --muted: #cbd5e1;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; background: transparent; font-family: "Trebuchet MS", "Segoe UI", sans-serif; }}
    body {{ display: flex; align-items: flex-end; justify-content: center; padding: 10px; }}
    .shell {{ min-width: 520px; background: linear-gradient(135deg, rgba(7, 12, 24, 0.94), rgba(20, 31, 52, 0.88)); color: var(--text); border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 12px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.25); overflow: hidden; }}
    .status {{ display: flex; justify-content: space-between; padding: 5px 10px; background: rgba(255,255,255,0.06); font-size: 0.9rem; letter-spacing: 0.08em; text-transform: uppercase; }}
    .board {{ display: grid; grid-template-columns: 1fr auto 1fr; align-items: stretch; gap: 6px; padding: 8px 8px 10px; }}
    .board.board--broadcast-split {{ grid-template-columns: 1fr 140px 1fr; }}
    .board.board--compact-led {{ grid-template-columns: 1fr; gap: 4px; }}
    .team {{ display: grid; grid-template-columns: 48px 1fr; gap: 8px; align-items: center; padding: 6px; border-radius: 10px; min-height: 56px; }}
    .team.away {{ grid-template-columns: 1fr 48px; }}
    .team.home {{ background: linear-gradient(135deg, rgba(198,40,40,0.92), rgba(127,29,29,0.92)); }}
    .team.away {{ background: linear-gradient(135deg, rgba(31,41,55,0.96), rgba(15,23,42,0.92)); }}
    .team.compact {{ min-height: auto; grid-template-columns: 36px 1fr auto; padding: 4px 6px; }}
    .logo {{ width: 40px; height: 40px; object-fit: cover; border-radius: 8px; background: rgba(255,255,255,0.94); border: 2px solid rgba(255,255,255,0.28); }}
    .team.compact .logo {{ width: 32px; height: 32px; border-radius: 7px; }}
    .team-name {{ font-size: 1rem; font-weight: 700; line-height: 1.1; }}
    .team-meta {{ margin-top: 4px; color: rgba(255,255,255,0.88); font-size: 0.8rem; }}
    .middle {{ display: grid; gap: 4px; min-width: 100px; align-content: center; }}
    .score {{ text-align: center; font-size: 2.1rem; font-weight: 800; letter-spacing: 0.08em; background: rgba(255,255,255,0.08); border-radius: 10px; padding: 6px 6px; }}
    .clock {{ text-align: center; font-size: 1.1rem; font-weight: 700; background: rgba(255,255,255,0.08); border-radius: 8px; padding: 6px 6px; }}
    .stacked-score {{ display: grid; gap: 4px; align-content: center; }}
    .stacked-score .score {{ font-size: 1.5rem; }}
    .compact-led-strip {{ display: grid; gap: 4px; }}
    .compact-score {{ font-size: 1rem; font-weight: 800; padding: 4px 6px; border-radius: 7px; background: rgba(255,255,255,0.08); }}
    .empty {{ padding: 10px; text-align: center; color: var(--muted); }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="status">
      <span id="status">Aguardando partida</span>
      <span id="period">Q1</span>
    </div>
    <div id="content" class="empty">Carregando placar...</div>
  </div>
  <script>
    const gameId = window.location.pathname.split('/').pop();
    let currentGame = null;
    let overlayTickHandle = null;

    function formatClock(seconds) {{
      const safe = Math.max(0, Number(seconds || 0));
      const minutes = Math.floor(safe / 60).toString().padStart(2, '0');
      const remainder = Math.floor(safe % 60).toString().padStart(2, '0');
      return `${{minutes}}:${{remainder}}`;
    }}

    function annotateGame(game) {{
      if (!game || typeof game !== 'object') {{
        return game;
      }}
      game._clientReceivedAt = Date.now();
      return game;
    }}

    function clientClockSeconds(game) {{
      const base = Math.max(0, Number(game?.clock?.elapsedSeconds ?? 0));
      if (!game?.clock?.isRunning) {{
        return base;
      }}
      const receivedAt = Number(game?._clientReceivedAt || Date.now());
      const elapsed = Math.max(0, Math.floor((Date.now() - receivedAt) / 1000));
      return Math.max(0, base - elapsed);
    }}

    function renderOverlayClock() {{
      if (!currentGame) {{
        return;
      }}
      const clockNode = document.querySelector('#content .clock');
      if (!clockNode) {{
        return;
      }}
      clockNode.textContent = formatClock(clientClockSeconds(currentGame));
    }}

    function startOverlayTicker() {{
      if (overlayTickHandle) {{
        clearInterval(overlayTickHandle);
      }}
      overlayTickHandle = setInterval(renderOverlayClock, 250);
    }}

    function renderEmpty(message) {{
      document.getElementById('content').className = 'empty';
      document.getElementById('content').textContent = message;
      document.getElementById('status').textContent = 'Sem dados';
      document.getElementById('period').textContent = '--';
    }}

    function renderGame(game) {{
      currentGame = annotateGame(game);
      const layoutId = game.layoutId || '{DEFAULT_LAYOUT_ID}';
      const content = document.getElementById('content');
      if (layoutId === 'broadcast-split') {{
        content.className = 'board board--broadcast-split';
        content.innerHTML = `
          <section class="team home">
            <img class="logo" src="${{game.homeTeam.logoUrl || ''}}" alt="Logo time casa">
            <div>
              <div class="team-name">${{game.homeTeam.name || 'Time Casa'}}</div>
              <div class="team-meta">Faltas: ${{game.homeTeam.fouls ?? 0}}</div>
            </div>
          </section>
          <section class="stacked-score">
            <div class="score">${{game.homeTeam.score ?? 0}} - ${{game.awayTeam.score ?? 0}}</div>
            <div class="clock">${{formatClock(clientClockSeconds(currentGame))}}</div>
          </section>
          <section class="team away">
            <div>
              <div class="team-name">${{game.awayTeam.name || 'Time Visitante'}}</div>
              <div class="team-meta">Faltas: ${{game.awayTeam.fouls ?? 0}}</div>
            </div>
            <img class="logo" src="${{game.awayTeam.logoUrl || ''}}" alt="Logo time visitante">
          </section>`;
      }} else if (layoutId === 'compact-led') {{
        content.className = 'compact-led-strip';
        content.innerHTML = `
          <section class="team home compact">
            <img class="logo" src="${{game.homeTeam.logoUrl || ''}}" alt="Logo time casa">
            <div>
              <div class="team-name">${{game.homeTeam.name || 'Time Casa'}}</div>
              <div class="team-meta">Faltas: ${{game.homeTeam.fouls ?? 0}}</div>
            </div>
            <div class="compact-score">${{game.homeTeam.score ?? 0}}</div>
          </section>
          <section class="middle">
            <div class="score">${{game.homeTeam.score ?? 0}} - ${{game.awayTeam.score ?? 0}}</div>
            <div class="clock">${{formatClock(clientClockSeconds(currentGame))}}</div>
          </section>
          <section class="team away compact">
            <img class="logo" src="${{game.awayTeam.logoUrl || ''}}" alt="Logo time visitante">
            <div>
              <div class="team-name">${{game.awayTeam.name || 'Time Visitante'}}</div>
              <div class="team-meta">Faltas: ${{game.awayTeam.fouls ?? 0}}</div>
            </div>
            <div class="compact-score">${{game.awayTeam.score ?? 0}}</div>
          </section>`;
      }} else {{
        content.className = 'board';
        content.innerHTML = `
        <section class="team home">
          <img class="logo" src="${{game.homeTeam.logoUrl || ''}}" alt="Logo time casa">
          <div>
            <div class="team-name">${{game.homeTeam.name || 'Time Casa'}}</div>
            <div class="team-meta">Faltas: ${{game.homeTeam.fouls ?? 0}}</div>
          </div>
        </section>
        <section class="middle">
          <div class="score">${{game.homeTeam.score ?? 0}} - ${{game.awayTeam.score ?? 0}}</div>
          <div class="clock">${{formatClock(clientClockSeconds(currentGame))}}</div>
        </section>
        <section class="team away">
          <div>
            <div class="team-name">${{game.awayTeam.name || 'Time Visitante'}}</div>
            <div class="team-meta">Faltas: ${{game.awayTeam.fouls ?? 0}}</div>
          </div>
          <img class="logo" src="${{game.awayTeam.logoUrl || ''}}" alt="Logo time visitante">
        </section>`;
      }}
      document.getElementById('status').textContent = (game.status || 'draft').toUpperCase();
      document.getElementById('period').textContent = `Q${{game.currentPeriod || 1}}`;
      startOverlayTicker();
    }}

    async function fetchGame() {{
      try {{
        const response = await fetch(`/api/games/${{encodeURIComponent(gameId)}}`, {{ cache: 'no-store' }});
        if (response.status === 404) {{
          renderEmpty('Partida ainda nao configurada.');
          return;
        }}
        if (!response.ok) {{
          throw new Error(`HTTP ${{response.status}}`);
        }}
        const data = await response.json();
        renderGame(data);
      }} catch (error) {{
        console.error(error);
        if (!currentGame) {{
          renderEmpty('Nao foi possivel carregar o placar.');
        }}
      }}
    }}

    fetchGame();
    setInterval(fetchGame, {OVERLAY_POLL_MS});
  </script>
</body>
</html>'''


def admin_html() -> str:
    club_catalog_json = json.dumps(club_catalog, ensure_ascii=False)
    layout_catalog_json = json.dumps(scoreboard_layout_catalog, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Console de Placar 2026</title>
  <style>
    :root {{
      --bg: #f6efe4;
      --bg-top: #fffaf0;
      --ink: #1f2937;
      --accent: #d35400;
      --accent-dark: #9a3412;
      --line: #e7d8c9;
      --panel-bg: rgba(255,255,255,0.86);
      --panel-shadow: 0 10px 24px rgba(154, 52, 18, 0.08);
      --input-bg: #ffffff;
      --muted: #6b7280;
      --secondary-bg: #e5ded4;
      --disabled-bg: #d6cfc5;
      --disabled-ink: #8b8377;
      --clock-bg: #111827;
      --clock-ink: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; background: radial-gradient(circle at top, var(--bg-top), var(--bg)); color: var(--ink); transition: background 0.2s ease, color 0.2s ease; }}
    body.dark-mode {{
      --bg: #111827;
      --bg-top: #1f2937;
      --ink: #f3f4f6;
      --accent: #ea580c;
      --accent-dark: #fdba74;
      --line: #374151;
      --panel-bg: rgba(17, 24, 39, 0.86);
      --panel-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
      --input-bg: #0f172a;
      --muted: #cbd5e1;
      --secondary-bg: #334155;
      --disabled-bg: #1f2937;
      --disabled-ink: #94a3b8;
      --clock-bg: #020617;
      --clock-ink: #f8fafc;
    }}
    .page {{ max-width: 1260px; margin: 0 auto; padding: 16px 20px 20px; }}
    .hero {{ display: flex; justify-content: space-between; gap: 14px; align-items: end; margin-bottom: 14px; }}
    h1 {{ margin: 0; font-size: clamp(1.45rem, 2vw, 2.1rem); line-height: 1.05; font-weight: 800; letter-spacing: -0.03em; }}
    h2 {{ margin: 0; font-size: 1rem; line-height: 1.1; font-weight: 800; letter-spacing: 0.02em; }}
    .muted {{ color: var(--muted); margin: 0; font-size: 0.88rem; line-height: 1.3; }}
    .notice {{ min-height: 20px; font-weight: 700; color: var(--accent-dark); font-size: 0.92rem; }}
    .hero-actions {{ display: flex; align-items: center; gap: 12px; }}
    .theme-toggle {{ display: inline-flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 999px; background: var(--panel-bg); border: 1px solid var(--line); box-shadow: var(--panel-shadow); color: var(--ink); font-size: 0.82rem; font-weight: 700; letter-spacing: 0.03em; }}
    .theme-toggle input {{ appearance: none; width: 42px; height: 24px; border-radius: 999px; background: var(--secondary-bg); position: relative; cursor: pointer; transition: background 0.2s ease; border: 1px solid var(--line); }}
    .theme-toggle input::after {{ content: ''; position: absolute; top: 2px; left: 2px; width: 18px; height: 18px; border-radius: 50%; background: var(--clock-ink); transition: transform 0.2s ease; }}
    .theme-toggle input:checked {{ background: var(--accent); }}
    .theme-toggle input:checked::after {{ transform: translateX(18px); }}
    .menu-button {{ display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 14px; font-size: 1.2rem; background: var(--panel-bg); color: var(--accent-dark); border: 1px solid var(--line); box-shadow: var(--panel-shadow); padding: 0; }}
    .layout {{ display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 14px; align-items: start; }}
    .layout.sidebar-collapsed {{ grid-template-columns: minmax(0, 1fr); }}
    .panel {{ background: var(--panel-bg); border: 1px solid var(--line); border-radius: 20px; padding: 14px; box-shadow: var(--panel-shadow); }}
    .config-panel {{ transition: opacity 0.2s ease, transform 0.2s ease; }}
    .layout.sidebar-collapsed .config-panel {{ display: none; }}
    .hidden {{ display: none !important; }}
    label {{ display: block; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 5px; color: var(--muted); }}
    input[type="text"], input[type="password"], input[type="url"], input[type="number"], select {{ width: 100%; border-radius: 12px; border: 1px solid var(--line); padding: 10px 12px; font: inherit; background: var(--input-bg); color: var(--ink); }}
    input:focus, select:focus {{ outline: 2px solid rgba(211,84,0,0.25); border-color: var(--accent); }}
    input[readonly] {{ opacity: 0.85; cursor: default; }}
    button {{ border: 0; border-radius: 12px; padding: 10px 14px; font: inherit; font-weight: 700; cursor: pointer; background: var(--accent); color: white; }}
    button.secondary {{ background: var(--secondary-bg); color: var(--ink); }}
    button.ghost {{ background: transparent; color: var(--accent-dark); border: 1px solid var(--line); }}
    .stack {{ display: grid; gap: 10px; }}
    .team-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .score-row {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-top: 8px; }}
    .score-row button {{ padding: 12px 8px; font-size: 1rem; }}
    .period-row {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }}
    .period-row button.active,
    .period-row button.active:disabled {{ background: #111827; color: #f9fafb; box-shadow: inset 0 0 0 2px var(--accent); }}
    .period-row button:disabled {{ background: var(--disabled-bg); color: var(--disabled-ink); cursor: not-allowed; }}
    .clock {{ display: grid; grid-template-columns: minmax(0, 1fr) auto auto auto; gap: 8px; align-items: center; }}
    .clock-display {{ font-size: 1.7rem; font-weight: 800; text-align: center; padding: 10px 14px; border-radius: 16px; background: var(--clock-bg); color: var(--clock-ink); line-height: 1; }}
    .meta-card {{ background: var(--input-bg); border: 1px dashed var(--line); border-radius: 16px; padding: 12px; font-size: 0.88rem; }}
    .meta-card a {{ color: var(--accent-dark); word-break: break-all; }}
    .club-preview {{ display: grid; grid-template-columns: 52px minmax(0, 1fr); gap: 10px; align-items: center; padding: 10px 12px; border: 1px dashed var(--line); border-radius: 16px; background: var(--input-bg); }}
    .club-preview img {{ width: 52px; height: 52px; object-fit: contain; border-radius: 12px; background: rgba(255,255,255,0.92); padding: 4px; }}
    .club-preview.is-empty img {{ display: none; }}
    .club-preview strong {{ display: block; font-size: 0.95rem; line-height: 1.2; }}
    .club-preview span {{ display: block; color: var(--muted); font-size: 0.8rem; }}
    .layout-gallery {{ display: grid; gap: 10px; }}
    .layout-option {{ display: grid; gap: 8px; text-align: left; padding: 14px; border: 1px solid var(--line); border-radius: 16px; background: var(--input-bg); color: var(--ink); }}
    .layout-option.active {{ box-shadow: inset 0 0 0 2px var(--accent); border-color: var(--accent); }}
    .layout-option small {{ color: var(--muted); font-weight: 600; }}
    .layout-preview {{ border-radius: 12px; border: 1px dashed var(--line); padding: 10px; min-height: 72px; background: linear-gradient(135deg, rgba(211,84,0,0.08), rgba(17,24,39,0.04)); display: grid; place-items: center; font-size: 0.8rem; color: var(--muted); }}
    .layout-actions {{ display: grid; gap: 10px; }}
    .panel-toolbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; }}
    .panel-toolbar h2 {{ margin: 0; }}
    @media (max-width: 860px) {{
      .page {{ padding: 14px; }}
      .hero {{ align-items: start; flex-direction: column; }}
      .hero-actions {{ width: 100%; justify-content: space-between; }}
      .layout {{ grid-template-columns: 1fr; }}
      .layout.sidebar-collapsed {{ grid-template-columns: 1fr; }}
      .layout.sidebar-collapsed .config-panel {{ display: none; }}
      .team-grid {{ grid-template-columns: 1fr; }}
      .clock {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div>
        <p class="muted">Mesa de controle manual</p>
        <h1>Console de Placar 2026</h1>
      </div>
      <div class="hero-actions">
        <label class="theme-toggle" for="darkModeSwitch">
          <span>Tema Escuro</span>
          <input id="darkModeSwitch" type="checkbox" role="switch" aria-label="Ativar modo escuro">
        </label>
        <button id="menuButton" class="menu-button hidden" type="button" aria-label="Abrir configuracao da partida" aria-expanded="true">☰</button>
        <div class="notice" id="notice"></div>
      </div>
    </section>
    <div id="layout" class="layout">
      <aside id="configPanel" class="panel stack config-panel">
        <section id="loginPanel" class="stack">
          <h2>Autenticacao</h2>
          <label for="password">Senha unica</label>
          <input id="password" type="password" placeholder="Informe a senha configurada">
          <button id="loginButton">Entrar</button>
        </section>
        <section id="galleryPanel" class="stack hidden">
          <div class="panel-toolbar">
            <h2>Escolha o layout</h2>
            <button id="backToGalleryButton" class="ghost hidden" type="button">Voltar para layouts</button>
          </div>
          <p class="muted">Selecione o modelo visual do placar antes de abrir o setup da partida.</p>
          <div id="layoutGallery" class="layout-gallery"></div>
          <div class="layout-actions">
            <div class="meta-card">
              <div><strong>Layout selecionado:</strong> <span id="selectedLayoutText">Nenhum</span></div>
              <div id="selectedLayoutHint" class="muted">Escolha uma opcao para liberar o setup.</div>
            </div>
            <button id="continueSetupButton" class="secondary" disabled>Continuar para o setup</button>
          </div>
        </section>
        <section id="gamePanel" class="stack hidden">
          <div class="panel-toolbar">
            <h2>Partida</h2>
            <button id="hideConfigButton" class="ghost hidden" type="button">Ocultar</button>
          </div>
          <div>
            <p class="muted">Crie uma nova partida ou continue a partir de um gameId existente.</p>
          </div>
          <div id="layoutSummaryCard" class="meta-card hidden">
            <div><strong>Layout atual:</strong> <span id="layoutNameText">--</span></div>
            <div id="layoutPreviewText" class="muted">--</div>
          </div>
          <button id="changeLayoutButton" class="secondary hidden" type="button">Trocar layout</button>
          <label for="homeClubId">Time casa</label>
          <select id="homeClubId">
            <option value="">Selecione o clube mandante</option>
          </select>
          <div id="homeClubPreview" class="club-preview is-empty">
            <img id="homeClubPreviewLogo" src="" alt="">
            <div>
              <strong id="homeClubPreviewName">Nenhum clube selecionado</strong>
              <span>Nome e logo oficiais preenchidos automaticamente.</span>
            </div>
          </div>
          <label for="awayClubId">Time visitante</label>
          <select id="awayClubId">
            <option value="">Selecione o clube visitante</option>
          </select>
          <div id="awayClubPreview" class="club-preview is-empty">
            <img id="awayClubPreviewLogo" src="" alt="">
            <div>
              <strong id="awayClubPreviewName">Nenhum clube selecionado</strong>
              <span>Nome e logo oficiais preenchidos automaticamente.</span>
            </div>
          </div>
          <button id="createGameButton">Criar partida</button>
          <button id="loadGameButton" class="secondary">Carregar pela URL atual</button>
          <button id="closeGameButton" class="ghost hidden">Encerrar partida</button>
          <div class="meta-card hidden" id="linksCard">
            <div><strong>gameId:</strong> <span id="gameIdText">--</span></div>
            <div><strong>Overlay:</strong> <a id="overlayLink" href="#" target="_blank" rel="noreferrer">--</a></div>
          </div>
        </section>
      </aside>
      <main id="controlPanel" class="panel hidden stack">
        <section class="team-grid">
          <article class="stack">
            <h2>Casa</h2>
            <label for="homeNameLive">Clube selecionado</label>
            <input id="homeNameLive" type="text" readonly>
            <label for="homeScore">Pontos</label>
            <input id="homeScore" type="number" min="0">
            <div class="score-row">
              <button data-team="home" data-delta="1">+1</button>
              <button data-team="home" data-delta="2">+2</button>
              <button data-team="home" data-delta="3">+3</button>
            </div>
            <label for="homeFouls">Faltas</label>
            <input id="homeFouls" type="number" min="0">
          </article>
          <article class="stack">
            <h2>Visitante</h2>
            <label for="awayNameLive">Clube selecionado</label>
            <input id="awayNameLive" type="text" readonly>
            <label for="awayScore">Pontos</label>
            <input id="awayScore" type="number" min="0">
            <div class="score-row">
              <button data-team="away" data-delta="1">+1</button>
              <button data-team="away" data-delta="2">+2</button>
              <button data-team="away" data-delta="3">+3</button>
            </div>
            <label for="awayFouls">Faltas</label>
            <input id="awayFouls" type="number" min="0">
          </article>
        </section>
        <section class="stack">
          <h2>Periodo</h2>
          <div class="period-row" id="periodButtons">
            <button data-period="1">1</button>
            <button data-period="2">2</button>
            <button data-period="3">3</button>
            <button data-period="4">4</button>
          </div>
        </section>
        <section class="stack">
          <h2>Cronometro</h2>
          <div class="clock">
            <div class="clock-display" id="clockDisplay">00:00</div>
            <button id="resetClockButton" class="ghost">Ajustar</button>
            <button id="toggleClockButton">Iniciar</button>
            <button id="pauseClockButton" class="secondary">Pausar</button>
          </div>
        </section>
      </main>
    </div>
  </div>
  <script>
    const pollMs = {OVERLAY_POLL_MS};
    const clubCatalog = {club_catalog_json};
    const layoutCatalog = {layout_catalog_json};
    const clubCatalogById = Object.fromEntries(clubCatalog.map((club) => [club.clubId, club]));
    const layoutCatalogById = Object.fromEntries(layoutCatalog.map((layout) => [layout.layoutId, layout]));
    const defaultLayoutId = (layoutCatalog.find((layout) => layout.isDefault) || layoutCatalog[0] || {{ layoutId: '{DEFAULT_LAYOUT_ID}' }}).layoutId;
    const queryGameId = new URLSearchParams(window.location.search).get('gameId');
    const state = {{ password: sessionStorage.getItem('adminPassword') || '', gameId: queryGameId || '', game: null, configOpen: true, autoCollapsedGameId: '', setupStage: 'login', selectedLayoutId: sessionStorage.getItem('selectedLayoutId') || '' }};
    let pollHandle = null;
    let clockTickHandle = null;
    const themeStorageKey = 'scoreboardTheme';
    const saveTimers = new Map();
    const elements = {{
      darkModeSwitch: document.getElementById('darkModeSwitch'),
      layout: document.getElementById('layout'),
      configPanel: document.getElementById('configPanel'),
      notice: document.getElementById('notice'),
      menuButton: document.getElementById('menuButton'),
      hideConfigButton: document.getElementById('hideConfigButton'),
      loginPanel: document.getElementById('loginPanel'),
      galleryPanel: document.getElementById('galleryPanel'),
      gamePanel: document.getElementById('gamePanel'),
      controlPanel: document.getElementById('controlPanel'),
      password: document.getElementById('password'),
      loginButton: document.getElementById('loginButton'),
      layoutGallery: document.getElementById('layoutGallery'),
      continueSetupButton: document.getElementById('continueSetupButton'),
      selectedLayoutText: document.getElementById('selectedLayoutText'),
      selectedLayoutHint: document.getElementById('selectedLayoutHint'),
      layoutSummaryCard: document.getElementById('layoutSummaryCard'),
      layoutNameText: document.getElementById('layoutNameText'),
      layoutPreviewText: document.getElementById('layoutPreviewText'),
      changeLayoutButton: document.getElementById('changeLayoutButton'),
      backToGalleryButton: document.getElementById('backToGalleryButton'),
      createGameButton: document.getElementById('createGameButton'),
      loadGameButton: document.getElementById('loadGameButton'),
      closeGameButton: document.getElementById('closeGameButton'),
      linksCard: document.getElementById('linksCard'),
      gameIdText: document.getElementById('gameIdText'),
      overlayLink: document.getElementById('overlayLink'),
      homeClubId: document.getElementById('homeClubId'),
      awayClubId: document.getElementById('awayClubId'),
      homeClubPreview: document.getElementById('homeClubPreview'),
      awayClubPreview: document.getElementById('awayClubPreview'),
      homeClubPreviewLogo: document.getElementById('homeClubPreviewLogo'),
      awayClubPreviewLogo: document.getElementById('awayClubPreviewLogo'),
      homeClubPreviewName: document.getElementById('homeClubPreviewName'),
      awayClubPreviewName: document.getElementById('awayClubPreviewName'),
      homeNameLive: document.getElementById('homeNameLive'),
      homeScore: document.getElementById('homeScore'),
      homeFouls: document.getElementById('homeFouls'),
      awayNameLive: document.getElementById('awayNameLive'),
      awayScore: document.getElementById('awayScore'),
      awayFouls: document.getElementById('awayFouls'),
      clockDisplay: document.getElementById('clockDisplay'),
      resetClockButton: document.getElementById('resetClockButton'),
      toggleClockButton: document.getElementById('toggleClockButton'),
      pauseClockButton: document.getElementById('pauseClockButton'),
      periodButtons: Array.from(document.querySelectorAll('[data-period]')),
      scoreButtons: Array.from(document.querySelectorAll('[data-team][data-delta]')),
    }};

    function populateClubSelectors() {{
      const options = clubCatalog.map((club) => `<option value="${{club.clubId}}">${{club.displayName}}</option>`).join('');
      elements.homeClubId.insertAdjacentHTML('beforeend', options);
      elements.awayClubId.insertAdjacentHTML('beforeend', options);
    }}

    function setSelectedLayout(layoutId) {{
      if (!layoutId || !layoutCatalogById[layoutId]) {{
        state.selectedLayoutId = '';
        sessionStorage.removeItem('selectedLayoutId');
      }} else {{
        state.selectedLayoutId = layoutId;
        sessionStorage.setItem('selectedLayoutId', layoutId);
      }}
      renderLayoutGallery();
      renderLayoutSelectionSummary();
    }}

    function getActiveLayout() {{
      return layoutCatalogById[state.selectedLayoutId] || layoutCatalogById[defaultLayoutId];
    }}

    function renderLayoutGallery() {{
      elements.layoutGallery.innerHTML = layoutCatalog.map((layout) => `
        <button type="button" class="layout-option${{layout.layoutId === state.selectedLayoutId ? ' active' : ''}}" data-layout-id="${{layout.layoutId}}">
          <strong>${{layout.displayName}}</strong>
          <small>${{layout.previewLabel}}</small>
          <div class="layout-preview">${{layout.previewAsset}}</div>
        </button>
      `).join('');
      Array.from(elements.layoutGallery.querySelectorAll('[data-layout-id]')).forEach((button) => {{
        button.addEventListener('click', () => setSelectedLayout(button.dataset.layoutId));
      }});
    }}

    function renderLayoutSelectionSummary() {{
      const layout = getActiveLayout();
      const hasSelection = Boolean(state.selectedLayoutId);
      elements.continueSetupButton.disabled = !hasSelection;
      elements.selectedLayoutText.textContent = hasSelection ? layout.displayName : 'Nenhum';
      elements.selectedLayoutHint.textContent = hasSelection
        ? layout.previewLabel
        : 'Escolha uma opcao para liberar o setup.';
      elements.layoutSummaryCard.classList.toggle('hidden', !layout);
      if (layout) {{
        elements.layoutNameText.textContent = layout.displayName;
        elements.layoutPreviewText.textContent = layout.previewLabel;
      }}
    }}

    function renderSetupStage() {{
      elements.loginPanel.classList.toggle('hidden', state.setupStage !== 'login');
      elements.galleryPanel.classList.toggle('hidden', state.setupStage !== 'gallery');
      elements.gamePanel.classList.toggle('hidden', state.setupStage !== 'setup');
      const canChangeLayout = !state.game || state.game.status === 'draft';
      elements.changeLayoutButton.classList.toggle('hidden', !canChangeLayout || state.setupStage !== 'setup');
      elements.backToGalleryButton.classList.toggle('hidden', state.setupStage !== 'setup' || Boolean(state.game));
      renderLayoutGallery();
      renderLayoutSelectionSummary();
    }}

    async function continueToSetup() {{
      if (!state.selectedLayoutId) {{
        setNotice('Escolha um layout antes de abrir o setup.', true);
        return;
      }}
      if (state.gameId && state.game && state.game.status === 'draft' && state.game.layoutId !== state.selectedLayoutId) {{
        await patchGame({{ layoutId: state.selectedLayoutId }});
      }}
      state.setupStage = 'setup';
      renderSetupStage();
      const layout = getActiveLayout();
      setNotice(`Layout selecionado: ${{layout.displayName}}.`);
    }}

    function openLayoutGallery() {{
      if (state.game && state.game.status !== 'draft') {{
        setNotice('O layout so pode ser alterado enquanto a partida estiver em draft.', true);
        return;
      }}
      state.setupStage = 'gallery';
      renderSetupStage();
    }}

    function applyTheme(mode) {{
      const darkMode = mode === 'dark';
      document.body.classList.toggle('dark-mode', darkMode);
      elements.darkModeSwitch.checked = darkMode;
    }}

    function initializeTheme() {{
      const savedTheme = localStorage.getItem(themeStorageKey);
      applyTheme(savedTheme === 'dark' ? 'dark' : 'light');
    }}

    function setConfigOpen(nextOpen) {{
      state.configOpen = Boolean(nextOpen);
      elements.layout.classList.toggle('sidebar-collapsed', !state.configOpen && Boolean(state.game));
      elements.configPanel.classList.toggle('hidden', !state.configOpen && Boolean(state.game));
      elements.menuButton.classList.toggle('hidden', !state.game);
      elements.menuButton.setAttribute('aria-expanded', String(state.configOpen));
      elements.menuButton.setAttribute('aria-label', state.configOpen ? 'Ocultar configuracao da partida' : 'Abrir configuracao da partida');
      elements.menuButton.textContent = state.configOpen ? '✕' : '☰';
      elements.hideConfigButton.classList.toggle('hidden', !state.game || !state.configOpen);
    }}

    function shouldAutoHideConfig(game) {{
      return Boolean(game) && game.status && game.status !== 'draft';
    }}

    function shouldAutoCollapseNow(game) {{
      return shouldAutoHideConfig(game) && state.gameId && state.autoCollapsedGameId !== state.gameId;
    }}

    function setNotice(message, isError = false) {{
      elements.notice.textContent = message || '';
      elements.notice.style.color = isError ? '#991b1b' : '#9a3412';
    }}

    function authHeaders() {{
      return {{ 'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Admin-Password': state.password }};
    }}

    function formatClock(seconds) {{
      const safe = Math.max(0, Number(seconds || 0));
      const minutes = Math.floor(safe / 60).toString().padStart(2, '0');
      const remainder = Math.floor(safe % 60).toString().padStart(2, '0');
      return `${{minutes}}:${{remainder}}`;
    }}

    function annotateGame(game) {{
      if (!game || typeof game !== 'object') {{
        return game;
      }}
      game._clientReceivedAt = Date.now();
      return game;
    }}

    function clientClockSeconds(game) {{
      const base = Math.max(0, Number(game?.clock?.elapsedSeconds ?? 0));
      if (!game?.clock?.isRunning) {{
        return base;
      }}
      const receivedAt = Number(game?._clientReceivedAt || Date.now());
      const elapsed = Math.max(0, Math.floor((Date.now() - receivedAt) / 1000));
      return Math.max(0, base - elapsed);
    }}

    function renderClockDisplay() {{
      if (!state.game) {{
        elements.clockDisplay.textContent = '00:00';
        return;
      }}
      elements.clockDisplay.textContent = formatClock(clientClockSeconds(state.game));
    }}

    function startClockTicker() {{
      if (clockTickHandle) {{
        clearInterval(clockTickHandle);
      }}
      clockTickHandle = setInterval(renderClockDisplay, 250);
    }}

    function parseClockInput(rawValue) {{
      const normalized = String(rawValue || '').trim();
      if (!normalized) {{
        throw new Error('Informe o novo tempo no formato MM:SS.');
      }}
      if (/^\\d+$/.test(normalized)) {{
        const totalSeconds = Number(normalized);
        if (Number.isNaN(totalSeconds) || totalSeconds < 0 || totalSeconds > 600) {{
          throw new Error('O cronometro deve ficar entre 00:00 e 10:00.');
        }}
        return totalSeconds;
      }}
      const match = normalized.match(/^(\\d{{1,2}}):(\\d{{2}})$/);
      if (!match) {{
        throw new Error('Use o formato MM:SS para ajustar o cronometro.');
      }}
      const minutes = Number(match[1]);
      const seconds = Number(match[2]);
      if (seconds > 59) {{
        throw new Error('Os segundos do cronometro devem ficar entre 00 e 59.');
      }}
      const totalSeconds = (minutes * 60) + seconds;
      if (totalSeconds < 0 || totalSeconds > 600) {{
        throw new Error('O cronometro deve ficar entre 00:00 e 10:00.');
      }}
      return totalSeconds;
    }}

    function syncInput(element, value) {{
      if (document.activeElement !== element) {{
        element.value = value ?? '';
      }}
    }}

    function syncSelect(element, value) {{
      if (document.activeElement !== element) {{
        element.value = value ?? '';
      }}
    }}

    function renderClubPreview(selectElement, previewElement, logoElement, nameElement) {{
      const club = clubCatalogById[selectElement.value] || null;
      previewElement.classList.toggle('is-empty', !club);
      if (!club) {{
        logoElement.src = '';
        logoElement.alt = '';
        nameElement.textContent = 'Nenhum clube selecionado';
        return;
      }}
      logoElement.src = club.logoUrl;
      logoElement.alt = `Logo ${{club.displayName}}`;
      nameElement.textContent = club.displayName;
    }}

    function renderClubSelectionState() {{
      renderClubPreview(elements.homeClubId, elements.homeClubPreview, elements.homeClubPreviewLogo, elements.homeClubPreviewName);
      renderClubPreview(elements.awayClubId, elements.awayClubPreview, elements.awayClubPreviewLogo, elements.awayClubPreviewName);
      const missingSelection = !elements.homeClubId.value || !elements.awayClubId.value;
      const duplicatedSelection = !missingSelection && elements.homeClubId.value === elements.awayClubId.value;
      elements.createGameButton.disabled = missingSelection || duplicatedSelection;
      elements.createGameButton.title = duplicatedSelection
        ? 'Selecione clubes diferentes para mandante e visitante.'
        : (missingSelection ? 'Selecione os dois clubes para criar a partida.' : 'Criar partida');
    }}

    function syncClubSelectorsFromGame(game) {{
      syncSelect(elements.homeClubId, game?.homeTeam?.clubId || '');
      syncSelect(elements.awayClubId, game?.awayTeam?.clubId || '');
      renderClubSelectionState();
    }}

    function validateClubSelection() {{
      if (!elements.homeClubId.value || !elements.awayClubId.value) {{
        throw new Error('Selecione os clubes mandante e visitante antes de criar a partida.');
      }}
      if (elements.homeClubId.value === elements.awayClubId.value) {{
        throw new Error('Os clubes mandante e visitante devem ser diferentes.');
      }}
    }}

    async function updateTeamClub(teamKey, clubId) {{
      if (!state.gameId || !state.game || state.game.status !== 'draft' || !clubId) {{
        return;
      }}
      await patchGame({{ [teamKey]: {{ clubId }} }});
      setNotice('Clube atualizado no setup da partida.');
    }}

    function renderLinks() {{
      if (!state.gameId) {{
        elements.linksCard.classList.add('hidden');
        elements.closeGameButton.classList.add('hidden');
        elements.menuButton.classList.add('hidden');
        return;
      }}
      const overlayUrl = `${{window.location.origin}}/api/overlay/${{state.gameId}}`;
      elements.linksCard.classList.remove('hidden');
      elements.closeGameButton.classList.remove('hidden');
      elements.gameIdText.textContent = state.gameId;
      elements.overlayLink.href = overlayUrl;
      elements.overlayLink.textContent = overlayUrl;
    }}

    function renderGame() {{
      const game = state.game;
      if (!game) {{
        elements.controlPanel.classList.add('hidden');
        state.autoCollapsedGameId = '';
        syncClubSelectorsFromGame(null);
        elements.homeClubId.disabled = false;
        elements.awayClubId.disabled = false;
        if (state.setupStage === 'setup' && !state.selectedLayoutId) {{
          state.setupStage = 'gallery';
        }}
        renderSetupStage();
        setConfigOpen(true);
        return;
      }}
      if (shouldAutoCollapseNow(game)) {{
        state.autoCollapsedGameId = state.gameId;
        state.configOpen = false;
      }}
      setSelectedLayout(game.layoutId || defaultLayoutId);
      state.setupStage = 'setup';
      renderSetupStage();
      elements.controlPanel.classList.remove('hidden');
      syncClubSelectorsFromGame(game);
      const clubsLocked = game.status && game.status !== 'draft';
      elements.homeClubId.disabled = Boolean(clubsLocked);
      elements.awayClubId.disabled = Boolean(clubsLocked);
      syncInput(elements.homeNameLive, game.homeTeam.name);
      syncInput(elements.homeScore, game.homeTeam.score);
      syncInput(elements.homeFouls, game.homeTeam.fouls);
      syncInput(elements.awayNameLive, game.awayTeam.name);
      syncInput(elements.awayScore, game.awayTeam.score);
      syncInput(elements.awayFouls, game.awayTeam.fouls);
      const remainingSeconds = clientClockSeconds(game);
      const currentPeriod = Number(game.currentPeriod || 1);
      renderClockDisplay();
      elements.toggleClockButton.textContent = game.clock?.isRunning ? 'Rodando' : 'Iniciar';
      elements.periodButtons.forEach((button) => {{
        const buttonPeriod = Number(button.dataset.period);
        const isActive = buttonPeriod === currentPeriod;
        let disabled = false;
        let reason = '';
        if (buttonPeriod < currentPeriod) {{
          disabled = true;
          reason = 'Periodo ja encerrado.';
        }} else if (isActive) {{
          disabled = true;
          reason = remainingSeconds > 0 ? 'Periodo atual em andamento.' : 'Periodo atual encerrado.';
        }} else if (buttonPeriod === currentPeriod + 1) {{
          disabled = remainingSeconds > 0;
          reason = disabled ? 'O proximo periodo so pode ser liberado quando o cronometro do atual chegar a 00:00.' : 'Liberar proximo periodo.';
        }} else {{
          disabled = true;
          reason = 'Os periodos devem ser ativados em sequencia.';
        }}
        button.classList.toggle('active', isActive);
        button.disabled = disabled;
        button.title = reason;
      }});
      renderLinks();
      setConfigOpen(state.configOpen);
      startClockTicker();
    }}

    async function resetClock() {{
      if (!state.game) {{ return; }}
      const suggested = formatClock(state.game.clock?.elapsedSeconds);
      const typed = window.prompt('Informe o novo tempo do periodo atual no formato MM:SS.', suggested);
      if (typed === null) {{ return; }}
      try {{
        const totalSeconds = parseClockInput(typed);
        await patchGame({{ clock: {{ elapsedSeconds: totalSeconds }} }});
        setNotice(`Cronometro ajustado para ${{formatClock(totalSeconds)}}.`);
      }} catch (error) {{
        setNotice(error.message, true);
      }}
    }}

    async function request(url, options = {{}}) {{
      const response = await fetch(url, options);
      if (response.status === 204) {{ return null; }}
      let data = null;
      try {{ data = await response.json(); }} catch (_error) {{ data = null; }}
      if (!response.ok) {{ throw new Error(data?.error || `HTTP ${{response.status}}`); }}
      return data;
    }}

    async function login() {{
      try {{
        const password = elements.password.value.trim();
        await request('/api/control/session', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json', 'Accept': 'application/json' }}, body: JSON.stringify({{ password }}) }});
        state.password = password;
        sessionStorage.setItem('adminPassword', password);
        state.setupStage = state.gameId ? 'setup' : 'gallery';
        renderSetupStage();
        setNotice('Painel liberado.');
        if (state.gameId) {{ await loadGame(); }}
      }} catch (error) {{
        setNotice(error.message, true);
      }}
    }}

    async function createGame() {{
      try {{
        validateClubSelection();
        if (!state.selectedLayoutId) {{
          throw new Error('Escolha um layout antes de criar a partida.');
        }}
        const payload = {{
          homeClubId: elements.homeClubId.value,
          awayClubId: elements.awayClubId.value,
          layoutId: state.selectedLayoutId,
        }};
        const created = await request('/api/games', {{ method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) }});
        state.gameId = created.gameId;
        history.replaceState(null, '', `?gameId=${{encodeURIComponent(state.gameId)}}`);
        await loadGame();
        setNotice('Partida criada com sucesso.');
      }} catch (error) {{
        setNotice(error.message, true);
      }}
    }}

    async function loadGame() {{
      if (!state.gameId) {{
        setNotice('Nenhum gameId informado.', true);
        return;
      }}
      try {{
        state.game = annotateGame(await request(`/api/games/${{encodeURIComponent(state.gameId)}}`, {{ headers: {{ 'Accept': 'application/json' }} }}));
        renderGame();
        startPolling();
      }} catch (error) {{
        setNotice(error.message, true);
      }}
    }}

    async function patchGame(payload) {{
      if (!state.gameId) {{ return; }}
      try {{
        state.game = annotateGame(await request(`/api/games/${{encodeURIComponent(state.gameId)}}`, {{ method: 'PATCH', headers: authHeaders(), body: JSON.stringify(payload) }}));
        renderGame();
      }} catch (error) {{
        setNotice(error.message, true);
      }}
    }}

    async function closeGame() {{
      if (!state.gameId) {{ return; }}
      try {{
        await request(`/api/games/${{encodeURIComponent(state.gameId)}}`, {{ method: 'DELETE', headers: authHeaders() }});
        stopPolling();
        state.game = null;
        state.gameId = '';
        state.autoCollapsedGameId = '';
        setSelectedLayout('');
        state.setupStage = 'gallery';
        elements.homeClubId.value = '';
        elements.awayClubId.value = '';
        history.replaceState(null, '', window.location.pathname);
        renderGame();
        renderLinks();
        setConfigOpen(true);
        setNotice('Partida encerrada.');
      }} catch (error) {{
        setNotice(error.message, true);
      }}
    }}

    function startPolling() {{
      stopPolling();
      pollHandle = setInterval(async () => {{
        if (!state.gameId) {{ return; }}
        try {{
          state.game = annotateGame(await request(`/api/games/${{encodeURIComponent(state.gameId)}}`, {{ headers: {{ 'Accept': 'application/json' }} }}));
          renderGame();
        }} catch (_error) {{}}
      }}, pollMs);
    }}

    function stopPolling() {{
      if (pollHandle) {{ clearInterval(pollHandle); pollHandle = null; }}
    }}

    function schedulePatch(key, payloadBuilder) {{
      if (saveTimers.has(key)) {{ clearTimeout(saveTimers.get(key)); }}
      saveTimers.set(key, setTimeout(() => {{
        saveTimers.delete(key);
        patchGame(payloadBuilder());
      }}, 350));
    }}

    elements.loginButton.addEventListener('click', login);
    elements.darkModeSwitch.addEventListener('change', () => {{
      const nextTheme = elements.darkModeSwitch.checked ? 'dark' : 'light';
      localStorage.setItem(themeStorageKey, nextTheme);
      applyTheme(nextTheme);
    }});
    elements.menuButton.addEventListener('click', () => setConfigOpen(!state.configOpen));
    elements.hideConfigButton.addEventListener('click', () => setConfigOpen(false));
    elements.continueSetupButton.addEventListener('click', continueToSetup);
    elements.changeLayoutButton.addEventListener('click', openLayoutGallery);
    elements.backToGalleryButton.addEventListener('click', openLayoutGallery);
    elements.createGameButton.addEventListener('click', createGame);
    elements.loadGameButton.addEventListener('click', loadGame);
    elements.closeGameButton.addEventListener('click', closeGame);
    elements.resetClockButton.addEventListener('click', resetClock);
    elements.toggleClockButton.addEventListener('click', () => patchGame({{ clock: {{ isRunning: true }} }}));
    elements.pauseClockButton.addEventListener('click', () => patchGame({{ clock: {{ isRunning: false }} }}));
    elements.periodButtons.forEach((button) => button.addEventListener('click', () => patchGame({{ currentPeriod: Number(button.dataset.period) }})));
    elements.scoreButtons.forEach((button) => button.addEventListener('click', () => {{
      if (!state.game) {{ return; }}
      const teamKey = button.dataset.team === 'home' ? 'homeTeam' : 'awayTeam';
      const current = Number(state.game[teamKey].score || 0);
      patchGame({{ [teamKey]: {{ score: current + Number(button.dataset.delta) }} }});
    }}));
    elements.homeScore.addEventListener('input', () => schedulePatch('homeScore', () => ({{ homeTeam: {{ score: Number(elements.homeScore.value || 0) }} }})));
    elements.homeFouls.addEventListener('input', () => schedulePatch('homeFouls', () => ({{ homeTeam: {{ fouls: Number(elements.homeFouls.value || 0) }} }})));
    elements.awayScore.addEventListener('input', () => schedulePatch('awayScore', () => ({{ awayTeam: {{ score: Number(elements.awayScore.value || 0) }} }})));
    elements.awayFouls.addEventListener('input', () => schedulePatch('awayFouls', () => ({{ awayTeam: {{ fouls: Number(elements.awayFouls.value || 0) }} }})));
    elements.homeClubId.addEventListener('change', async () => {{
      renderClubSelectionState();
      if (elements.homeClubId.value && elements.homeClubId.value === elements.awayClubId.value) {{
        setNotice('Os clubes mandante e visitante devem ser diferentes.', true);
        return;
      }}
      await updateTeamClub('homeTeam', elements.homeClubId.value);
    }});
    elements.awayClubId.addEventListener('change', async () => {{
      renderClubSelectionState();
      if (elements.awayClubId.value && elements.homeClubId.value === elements.awayClubId.value) {{
        setNotice('Os clubes mandante e visitante devem ser diferentes.', true);
        return;
      }}
      await updateTeamClub('awayTeam', elements.awayClubId.value);
    }});

    populateClubSelectors();
    renderClubSelectionState();
    renderSetupStage();
    initializeTheme();
    setConfigOpen(true);
    if (state.password) {{ elements.password.value = state.password; login(); }}
  </script>
</body>
</html>'''


@app.route(route="index", auth_level=func.AuthLevel.ANONYMOUS)
def index(req: func.HttpRequest) -> func.HttpResponse:
    html_content = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Placar SESI Basquete (Overlay)</title>
  <style>
    html, body { margin: 0; padding: 0; height: 100%; background: transparent; display: flex; justify-content: left; align-items: center; font-family: 'Arial Black', 'Segoe UI', sans-serif; color: transparent; }
    .placar-container { display: flex; flex-direction: column; gap: 6px; animation: fadeInUp 3s ease-out; }
    .linha-time { display: flex; align-items: center; justify-content: center; width: 160px; gap: 10px; }
    .logo-time { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background-color: #fff; box-shadow: 0 0 6px rgba(0,0,0,0.4); }
    .time { flex: 1; text-align: center; font-size: 0.5rem; font-weight: 700; letter-spacing: 0.5px; border-radius: 6px; padding: 8px 10px; color: #fff; text-shadow: 5px 5px 5px rgba(0,0,0,0.4); }
    .time.casa { background-color: #d62828; }
    .time.fora { background-color: #3a3a3a; }
    .centro { background-color: #ffffff; color: #000; font-size: 0.95rem; font-weight: 700; text-align: center; padding: 10px 0; width: 160px; border-radius: 6px; box-shadow: 0 0 8px rgba(0,0,0,0.25); }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body>
  <div class="placar-container">
    <div class="linha-time"><img id="logo_casa" class="logo-time" src="" alt="Logo Casa"><div id="nome_casa" class="time casa"></div></div>
    <div class="linha-time"><div id="nome_fora" class="time fora"></div><img id="logo_fora" class="logo-time" src="" alt="Logo Fora"></div>
    <div id="placar" class="centro"></div>
  </div>
  <script>
    const urlParams = new URLSearchParams(window.location.search);
    const competition = urlParams.get('competition');
    const apiUrl = `/api/placar?competition=${{encodeURIComponent(competition || '')}}`;
    async function atualizarPlacar() {{
      if (!competition) {{ return; }}
      const response = await fetch(`${{apiUrl}}&_ts=${{Date.now()}}`, {{ cache: 'no-store' }});
      if (!response.ok) {{ return; }}
      const data = await response.json();
      document.getElementById('logo_casa').src = data.logo_casa || '';
      document.getElementById('logo_fora').src = data.logo_fora || '';
      document.getElementById('nome_casa').textContent = data.nome_casa || 'Time Casa';
      document.getElementById('nome_fora').textContent = data.nome_fora || 'Time Fora';
      document.getElementById('placar').textContent = `${{data.placar_casa || '0'}} - ${{data.placar_fora || '0'}}`;
    }}
    atualizarPlacar();
    setInterval(atualizarPlacar, 20000);
  </script>
</body>
</html>'''
    return func.HttpResponse(html_content, mimetype="text/html")


@app.route(route="placar", auth_level=func.AuthLevel.ANONYMOUS)
def placar(req: func.HttpRequest) -> func.HttpResponse:
    competition = req.params.get("competition")
    if not competition:
        return json_response({"error": "competition is required"}, status_code=401)

    try:
        dados = get_placar_data(f"{LEGACY_API_PREFIX}?state={competition}")
    except requests.RequestException:
        logging.exception("Legacy placar request failed")
        return json_response({"error": "Unable to fetch legacy placar data"}, status_code=502)
    except Exception:
        logging.exception("Unexpected legacy placar error")
        return json_response({"error": "Unexpected legacy placar error"}, status_code=500)

    if not dados:
        return json_response({"error": "Game not found for configured entity"}, status_code=404)
    return json_response(dados)


@app.route(route="control", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def control(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(admin_html(), mimetype="text/html")


@app.route(route="overlay/{gameId}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def overlay(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(overlay_html(), mimetype="text/html")


@app.route(route="control/session", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def control_session(req: func.HttpRequest) -> func.HttpResponse:
    payload = parse_json_request(req)
    configured_password = get_admin_password()
    if not configured_password:
        return json_response({"error": "Administrative password is not configured"}, status_code=503)
    if payload.get("password", "").strip() != configured_password:
        return json_response({"error": "Unauthorized"}, status_code=401)
    return no_content_response()


@app.route(route="games", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def games(req: func.HttpRequest) -> func.HttpResponse:
    unauthorized = require_admin(req)
    if unauthorized:
        return unauthorized

    try:
        payload = parse_json_request(req)
        clubs_by_name = {club["displayName"]: club["clubId"] for club in club_catalog}
        home = payload.get("homeTeam") or {}
        away = payload.get("awayTeam") or {}
        home_club_id = payload.get("homeClubId") or clubs_by_name.get((home.get("name") or "").strip())
        away_club_id = payload.get("awayClubId") or clubs_by_name.get((away.get("name") or "").strip())
        layout_id = payload.get("layoutId")
        game = store.create_game(home_club_id=home_club_id, away_club_id=away_club_id, layout_id=layout_id)
    except InvalidGameUpdate as exc:
        return json_response({"error": str(exc)}, status_code=422)
    except GameStateError as exc:
        logging.exception("Failed to create game")
        return json_response({"error": str(exc)}, status_code=500)

    payload = dict(game)
    payload.update(game_urls(req, game["gameId"]))
    logging.info("Created game %s", game["gameId"])
    return json_response(payload, status_code=201)


@app.route(route="games/{gameId}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "PATCH", "DELETE"])
def game_by_id(req: func.HttpRequest) -> func.HttpResponse:
    game_id = req.route_params.get("gameId", "")

    try:
        if req.method == "GET":
            return json_response(store.get_game_response(game_id))

        unauthorized = require_admin(req)
        if unauthorized:
            return unauthorized

        if req.method == "PATCH":
            payload = parse_json_request(req)
            updated = store.update_game(game_id, payload)
            logging.info("Updated game %s", game_id)
            return json_response(updated)

        if req.method == "DELETE":
            store.delete_game(game_id)
            logging.info("Deleted game %s", game_id)
            return no_content_response()
    except GameNotFoundError:
        return json_response({"error": "Game not found"}, status_code=404)
    except InvalidGameUpdate as exc:
        return json_response({"error": str(exc)}, status_code=422)
    except GameStateError as exc:
        logging.exception("Game store failure")
        return json_response({"error": str(exc)}, status_code=500)
    except Exception:
        logging.exception("Unexpected error in game handler")
        return json_response({"error": "Unexpected server error"}, status_code=500)

    return json_response({"error": "Method not allowed"}, status_code=405)


def get_placar_data(url: str) -> Optional[Dict[str, Any]]:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    fixtures = data.get("data", {}).get("fixtures", [])
    for fixture in fixtures:
        competitors = fixture.get("competitors", [])
        if any(c.get("entityId") == ENTITY_ID for c in competitors):
            if len(competitors) == 2:
                time_casa = next((c for c in competitors if c.get("isHome")), competitors[0])
                time_fora = next((c for c in competitors if not c.get("isHome")), competitors[1])
                return {
                    "logo_casa": time_casa.get("logo", ""),
                    "logo_fora": time_fora.get("logo", ""),
                    "nome_casa": time_casa.get("code", ""),
                    "nome_fora": time_fora.get("code", ""),
                    "placar_casa": time_casa.get("score", "0"),
                    "placar_fora": time_fora.get("score", "0"),
                }
    return None
