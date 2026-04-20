import unittest

from scoreboard_state import BlobGameStore, DEFAULT_LAYOUT_ID, build_initial_game


class LayoutPersistenceTests(unittest.TestCase):
    def test_get_game_response_keeps_layout_id_from_cached_game(self) -> None:
        store = BlobGameStore(connection_string=None, container_name="games")
        game = build_initial_game("sesi-araraquara", "ad-santo-andre", "broadcast-split")
        store._cache[game["gameId"]] = game

        payload = store.get_game_response(game["gameId"])

        self.assertEqual(payload["layoutId"], "broadcast-split")

    def test_get_game_response_applies_default_layout_to_legacy_cached_game(self) -> None:
        store = BlobGameStore(connection_string=None, container_name="games")
        legacy_game = build_initial_game("sesi-araraquara", "ad-santo-andre", "classic")
        legacy_game.pop("layoutId", None)
        store._cache[legacy_game["gameId"]] = legacy_game

        payload = store.get_game_response(legacy_game["gameId"])

        self.assertEqual(payload["layoutId"], DEFAULT_LAYOUT_ID)