import unittest

from function_app import admin_html


class ControlSetupAfterLayoutTests(unittest.TestCase):
    def test_admin_html_keeps_current_setup_fields_after_layout_stage(self) -> None:
        html = admin_html()

        self.assertIn('id="homeClubId"', html)
        self.assertIn('id="awayClubId"', html)
        self.assertIn('id="homeScore"', html)
        self.assertIn('id="awayScore"', html)

    def test_create_game_javascript_sends_layout_id(self) -> None:
        html = admin_html()

        self.assertIn('layoutId: state.selectedLayoutId', html)
        self.assertIn('state.setupStage = \'setup\'', html)
        self.assertIn('id="changeLayoutButton"', html)