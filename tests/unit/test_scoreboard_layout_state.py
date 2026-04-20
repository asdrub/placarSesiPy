import unittest

from scoreboard_state import DEFAULT_LAYOUT_ID, InvalidGameUpdate, apply_game_update, build_initial_game, serialize_game


class ScoreboardLayoutStateTests(unittest.TestCase):
    def test_build_initial_game_requires_valid_layout_id(self) -> None:
        game = build_initial_game(
            "sesi-araraquara",
            "ad-santo-andre",
            layout_id="classic",
        )

        self.assertEqual(game["layoutId"], "classic")

    def test_serialize_game_falls_back_to_default_layout_for_legacy_payload(self) -> None:
        legacy_game = build_initial_game(
            "sesi-araraquara",
            "ad-santo-andre",
            layout_id="classic",
        )
        legacy_game.pop("layoutId", None)

        payload = serialize_game(legacy_game)

        self.assertEqual(payload["layoutId"], DEFAULT_LAYOUT_ID)

    def test_apply_game_update_blocks_layout_change_after_draft(self) -> None:
        game = build_initial_game(
            "sesi-araraquara",
            "ad-santo-andre",
            layout_id="classic",
        )
        game["status"] = "live"

        with self.assertRaises(InvalidGameUpdate):
            apply_game_update(game, {"layoutId": "compact-led"})


if __name__ == "__main__":
    unittest.main()