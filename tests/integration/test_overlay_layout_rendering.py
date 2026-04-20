import unittest

from function_app import overlay_html


class OverlayLayoutRenderingTests(unittest.TestCase):
    def test_overlay_html_contains_variant_markup_and_fallback(self) -> None:
        html = overlay_html()

        self.assertIn("board--broadcast-split", html)
        self.assertIn("compact-led-strip", html)
        self.assertIn("game.layoutId || 'classic'", html)

    def test_overlay_html_retains_public_game_fetch_flow(self) -> None:
        html = overlay_html()

        self.assertIn("fetch(`/api/games/${encodeURIComponent(gameId)}`", html)
        self.assertIn("renderGame(data);", html)