import json
import os
import unittest
from unittest import mock

import azure.functions as func

import function_app
from scoreboard_state import build_initial_game


class _DummyStore:
    def create_game(self, home_club_id: str, away_club_id: str, layout_id: str):
        return build_initial_game(home_club_id, away_club_id, layout_id)


class LayoutGameCreationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.password_patch = mock.patch.dict(os.environ, {"ADMIN_PASSWORD": "secret"}, clear=False)
        self.password_patch.start()
        self.store_patch = mock.patch.object(function_app, "store", _DummyStore())
        self.store_patch.start()

    def tearDown(self) -> None:
        self.store_patch.stop()
        self.password_patch.stop()

    def _request(self, payload: dict) -> func.HttpRequest:
        return func.HttpRequest(
            method="POST",
            url="http://localhost:7071/api/games",
            headers={"X-Admin-Password": "secret", "Content-Type": "application/json"},
            params={},
            route_params={},
            body=json.dumps(payload).encode("utf-8"),
        )

    def test_post_games_accepts_layout_id(self) -> None:
        response = function_app.games(
            self._request(
                {
                    "homeClubId": "sesi-araraquara",
                    "awayClubId": "ad-santo-andre",
                    "layoutId": "classic",
                }
            )
        )

        self.assertEqual(response.status_code, 201)
        payload = json.loads(response.get_body())
        self.assertEqual(payload["layoutId"], "classic")

    def test_post_games_rejects_missing_layout_id(self) -> None:
        response = function_app.games(
            self._request(
                {
                    "homeClubId": "sesi-araraquara",
                    "awayClubId": "ad-santo-andre",
                }
            )
        )

        self.assertEqual(response.status_code, 422)
        payload = json.loads(response.get_body())
        self.assertIn("layoutId", payload["error"])