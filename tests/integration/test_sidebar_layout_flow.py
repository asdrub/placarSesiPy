import unittest

from function_app import admin_html


class SidebarLayoutFlowTests(unittest.TestCase):
    def test_sidebar_controls_are_preserved_with_layout_gallery(self) -> None:
        html = admin_html()

        self.assertIn('function setConfigOpen(nextOpen)', html)
        self.assertIn('id="menuButton"', html)
        self.assertIn('id="hideConfigButton"', html)

    def test_layout_flow_can_return_to_gallery_without_breaking_sidebar_logic(self) -> None:
        html = admin_html()

        self.assertIn('function openLayoutGallery()', html)
        self.assertIn('state.autoCollapsedGameId = state.gameId;', html)
        self.assertIn('setConfigOpen(state.configOpen);', html)