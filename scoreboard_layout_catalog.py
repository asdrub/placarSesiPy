scoreboard_layout_catalog = [
    {
        "layoutId": "classic",
        "displayName": "Classico",
        "previewLabel": "Modelo atual com foco em leitura rapida.",
        "previewAsset": "classic-preview",
        "isDefault": True,
    },
    {
        "layoutId": "broadcast-split",
        "displayName": "Broadcast Split",
        "previewLabel": "Times destacados em blocos laterais com painel central forte.",
        "previewAsset": "broadcast-split-preview",
        "isDefault": False,
    },
    {
        "layoutId": "compact-led",
        "displayName": "Compact LED",
        "previewLabel": "Variacao compacta para overlays mais enxutos.",
        "previewAsset": "compact-led-preview",
        "isDefault": False,
    },
    {
        "layoutId": "tv-block",
        "displayName": "TV Block",
        "previewLabel": "Estilo TV com blocos coloridos, linhas e logos laterais.",
        "previewAsset": "<div style='display:flex;align-items:center;gap:4px;'><span style='background:#fff;border-radius:3px;padding:2px 4px;color:#222;font-size:0.8em;'>2ND</span><span style='background:#000;color:#fff;border-radius:3px;padding:2px 4px;font-size:0.8em;'>00:05</span><span style='background:#e53935;color:#fff;border-radius:3px;padding:2px 6px;font-weight:700;'>42</span><span style='background:#1e88e5;color:#fff;border-radius:3px;padding:2px 6px;font-weight:700;'>9</span></div>",
        "isDefault": False,
    },
]

LAYOUTS_BY_ID = {layout["layoutId"]: layout for layout in scoreboard_layout_catalog}
DEFAULT_LAYOUT_ID = next(
    layout["layoutId"] for layout in scoreboard_layout_catalog if layout.get("isDefault")
)