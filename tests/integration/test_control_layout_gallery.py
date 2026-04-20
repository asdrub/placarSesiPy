import unittest

from function_app import admin_html


class ControlLayoutGalleryTests(unittest.TestCase):
    def test_admin_html_contains_layout_gallery_stage(self) -> None:
        html = admin_html()

        self.assertIn('id="galleryPanel"', html)
        self.assertIn('id="layoutGallery"', html)
        self.assertIn('id="continueSetupButton"', html)

    def test_admin_html_embeds_known_layout_options(self) -> None:
        html = admin_html()

        self.assertIn('classic', html)
        self.assertIn('broadcast-split', html)
        self.assertIn('compact-led', html)