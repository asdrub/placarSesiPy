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
]

LAYOUTS_BY_ID = {layout["layoutId"]: layout for layout in scoreboard_layout_catalog}
DEFAULT_LAYOUT_ID = next(
    layout["layoutId"] for layout in scoreboard_layout_catalog if layout.get("isDefault")
)