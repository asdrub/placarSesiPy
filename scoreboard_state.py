import copy
import json
import re
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient
from club_catalog import club_catalog
from scoreboard_layout_catalog import DEFAULT_LAYOUT_ID, LAYOUTS_BY_ID

DEVSTORE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    "QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;"
    "TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
)

FIBA_PERIOD_SECONDS = 600
CLUBS_BY_ID = {club["clubId"]: club for club in club_catalog}


class GameStateError(Exception):
    pass


class GameNotFoundError(GameStateError):
    pass


class InvalidGameUpdate(GameStateError):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iso_to_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def sanitize_game_id(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", value.lower())


def generate_game_id() -> str:
    return sanitize_game_id(f"game-{secrets.token_hex(4)}")


def validate_non_negative_int(value: Any, field_name: str, max_value: int = 9999) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidGameUpdate(f"{field_name} must be an integer") from exc

    if parsed < 0 or parsed > max_value:
        raise InvalidGameUpdate(f"{field_name} must be between 0 and {max_value}")
    return parsed


def validate_period(value: Any) -> int:
    period = validate_non_negative_int(value, "currentPeriod", max_value=4)
    if period < 1:
        raise InvalidGameUpdate("currentPeriod must be between 1 and 4")
    return period


def validate_name(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise InvalidGameUpdate(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise InvalidGameUpdate(f"{field_name} cannot be empty")
    return normalized


def optional_string(value: Any, field_name: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise InvalidGameUpdate(f"{field_name} must be a string")
    return value.strip()


def _team(side: str, name: str, logo_url: str, club_id: Optional[str] = None) -> Dict[str, Any]:
    team = {
        "side": side,
        "name": validate_name(name, f"{side}Team.name"),
        "logoUrl": optional_string(logo_url, f"{side}Team.logoUrl"),
        "score": 0,
        "fouls": 0,
    }
    if club_id:
        team["clubId"] = club_id
    return team


def resolve_club(club_id: Any, field_name: str) -> Dict[str, Any]:
    normalized = optional_string(club_id, field_name)
    if not normalized:
        raise InvalidGameUpdate(f"{field_name} cannot be empty")
    club = CLUBS_BY_ID.get(normalized)
    if club is None:
        raise InvalidGameUpdate(f"{field_name} must reference a valid club")
    return club


def resolve_layout(layout_id: Any, field_name: str = "layoutId") -> Dict[str, Any]:
    normalized = optional_string(layout_id, field_name)
    if not normalized:
        raise InvalidGameUpdate(f"{field_name} cannot be empty")
    layout = LAYOUTS_BY_ID.get(normalized)
    if layout is None:
        raise InvalidGameUpdate(f"{field_name} must reference a valid layout")
    return layout


def ensure_layout_id(game: Dict[str, Any]) -> str:
    layout_id = game.get("layoutId")
    if isinstance(layout_id, str) and layout_id in LAYOUTS_BY_ID:
        return layout_id
    game["layoutId"] = DEFAULT_LAYOUT_ID
    return DEFAULT_LAYOUT_ID


def validate_club_selection(home_club_id: Any, away_club_id: Any) -> None:
    home_club = resolve_club(home_club_id, "homeClubId")
    away_club = resolve_club(away_club_id, "awayClubId")
    if home_club["clubId"] == away_club["clubId"]:
        raise InvalidGameUpdate("homeClubId and awayClubId must be different")


def build_initial_game(home_club_id: Any, away_club_id: Any, layout_id: Any) -> Dict[str, Any]:
    validate_club_selection(home_club_id, away_club_id)
    home_club = resolve_club(home_club_id, "homeClubId")
    away_club = resolve_club(away_club_id, "awayClubId")
    layout = resolve_layout(layout_id, "layoutId")
    timestamp = utc_now_iso()

    return {
        "gameId": generate_game_id(),
        "layoutId": layout["layoutId"],
        "status": "draft",
        "createdAt": timestamp,
        "updatedAt": timestamp,
        "currentPeriod": 1,
        "clock": {
            "elapsedSeconds": FIBA_PERIOD_SECONDS,
            "isRunning": False,
            "lastStartedAt": None,
        },
        "homeTeam": _team(
            "home",
            home_club["displayName"],
            home_club["logoUrl"],
            club_id=home_club["clubId"],
        ),
        "awayTeam": _team(
            "away",
            away_club["displayName"],
            away_club["logoUrl"],
            club_id=away_club["clubId"],
        ),
    }


class GameManager:
    def __init__(self, container_name: str):
        self._container_name = container_name
        self._container_client = None

    def create_game(self, home_name: str, away_name: str, home_logo: str, away_logo: str) -> Dict[str, Any]:
        game = {
            "home": {
                "name": home_name,
                "logoUrl": home_logo,
                "score": 0,
                "fouls": 0
            },
            "away": {
                "name": away_name,
                "logoUrl": away_logo,
                "score": 0,
                "fouls": 0
            },
            "status": "draft"
        }
        self.save_game(game)
        return game

    def save_game(self, game: Dict[str, Any]) -> None:
        container = self._ensure_container()
        document = {"version": 1, "game": game}
        container.upload_blob(name=self._blob_name(game["gameId"]), data=json.dumps(document).encode("utf-8"), overwrite=True)

    def _ensure_container(self):
        if self._container_client is None:
            self._container_client = BlobServiceClient.from_connection_string("<connection_string>").get_container_client(self._container_name)
        return self._container_client

    def _blob_name(self, game_id: str) -> str:
        return f"{game_id}.json"


def compute_clock_seconds(game: Dict[str, Any]) -> int:
    clock = game["clock"]
    base_seconds = validate_non_negative_int(clock.get("elapsedSeconds", FIBA_PERIOD_SECONDS), "clock.elapsedSeconds", max_value=FIBA_PERIOD_SECONDS)
    if not clock.get("isRunning"):
        return base_seconds

    last_started = iso_to_datetime(clock.get("lastStartedAt"))
    if not last_started:
        return base_seconds

    elapsed_delta = datetime.now(timezone.utc) - last_started
    return max(0, base_seconds - max(0, int(elapsed_delta.total_seconds())))


def normalize_clock(game: Dict[str, Any]) -> None:
    remaining_seconds = compute_clock_seconds(game)
    game["clock"]["elapsedSeconds"] = remaining_seconds
    if remaining_seconds <= 0:
        game["clock"]["elapsedSeconds"] = 0
        game["clock"]["isRunning"] = False
        game["clock"]["lastStartedAt"] = None
        if game.get("status") == "live":
            game["status"] = "paused"
        return

    if game["clock"].get("isRunning"):
        game["clock"]["lastStartedAt"] = utc_now_iso()
    else:
        game["clock"]["lastStartedAt"] = None


def freeze_clock(game: Dict[str, Any]) -> None:
    normalize_clock(game)
    game["clock"]["isRunning"] = False
    game["clock"]["lastStartedAt"] = None


def start_clock(game: Dict[str, Any]) -> None:
    normalize_clock(game)
    if game["clock"].get("isRunning"):
        return
    if game["clock"].get("elapsedSeconds", 0) <= 0:
        return
    game["clock"]["isRunning"] = True
    game["clock"]["lastStartedAt"] = utc_now_iso()
    if game["status"] in {"draft", "paused"}:
        game["status"] = "live"


def validate_period_transition(game: Dict[str, Any], next_period: int) -> None:
    current_period = validate_period(game.get("currentPeriod", 1))
    if next_period == current_period:
        return
    if next_period < current_period:
        raise InvalidGameUpdate("currentPeriod cannot go backwards")
    if next_period != current_period + 1:
        raise InvalidGameUpdate("currentPeriod can only advance one period at a time")
    if compute_clock_seconds(game) > 0:
        raise InvalidGameUpdate("currentPeriod can only advance after the current period clock reaches 00:00")


def serialize_game(game: Dict[str, Any]) -> Dict[str, Any]:
    payload = copy.deepcopy(game)
    ensure_layout_id(payload)
    normalize_clock(payload)
    payload["clock"].pop("lastStartedAt", None)
    return payload


def apply_game_update(game: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(updates, dict):
        raise InvalidGameUpdate("Request body must be a JSON object")

    ensure_layout_id(game)

    for team_key in ("homeTeam", "awayTeam"):
        if team_key in updates:
            team_patch = updates[team_key]
            if not isinstance(team_patch, dict):
                raise InvalidGameUpdate(f"{team_key} must be an object")
            target = game[team_key]
            if "clubId" in team_patch:
                club = resolve_club(team_patch["clubId"], f"{team_key}.clubId")
                target["clubId"] = club["clubId"]
                target["name"] = club["displayName"]
                target["logoUrl"] = club["logoUrl"]
            if "name" in team_patch:
                if target.get("clubId"):
                    raise InvalidGameUpdate(f"{team_key}.name cannot be edited directly for catalog teams")
                target["name"] = validate_name(team_patch["name"], f"{team_key}.name")
            if "logoUrl" in team_patch:
                if target.get("clubId"):
                    raise InvalidGameUpdate(f"{team_key}.logoUrl cannot be edited directly for catalog teams")
                target["logoUrl"] = optional_string(team_patch["logoUrl"], f"{team_key}.logoUrl")
            if "score" in team_patch:
                target["score"] = validate_non_negative_int(team_patch["score"], f"{team_key}.score", max_value=999)
            if "fouls" in team_patch:
                target["fouls"] = validate_non_negative_int(team_patch["fouls"], f"{team_key}.fouls", max_value=99)

    home_club_id = game.get("homeTeam", {}).get("clubId")
    away_club_id = game.get("awayTeam", {}).get("clubId")
    if home_club_id and away_club_id and home_club_id == away_club_id:
        raise InvalidGameUpdate("homeTeam.clubId and awayTeam.clubId must be different")

    if "layoutId" in updates:
        if game.get("status") != "draft":
            raise InvalidGameUpdate("layoutId can only be changed while status is draft")
        layout = resolve_layout(updates["layoutId"], "layoutId")
        game["layoutId"] = layout["layoutId"]

    if "currentPeriod" in updates:
        next_period = validate_period(updates["currentPeriod"])
        validate_period_transition(game, next_period)
        if next_period != game["currentPeriod"]:
            freeze_clock(game)
            game["currentPeriod"] = next_period
            game["clock"]["elapsedSeconds"] = FIBA_PERIOD_SECONDS
            game["clock"]["isRunning"] = False
            game["clock"]["lastStartedAt"] = None
            if game["status"] not in {"draft", "closed"}:
                game["status"] = "paused"

    if "clock" in updates:
        clock_patch = updates["clock"]
        if not isinstance(clock_patch, dict):
            raise InvalidGameUpdate("clock must be an object")
        if "elapsedSeconds" in clock_patch:
            game["clock"]["elapsedSeconds"] = validate_non_negative_int(clock_patch["elapsedSeconds"], "clock.elapsedSeconds", max_value=FIBA_PERIOD_SECONDS)
            if game["clock"].get("isRunning"):
                game["clock"]["lastStartedAt"] = utc_now_iso()
        if "isRunning" in clock_patch:
            is_running = bool(clock_patch["isRunning"])
            if is_running:
                start_clock(game)
            else:
                freeze_clock(game)

    if "status" in updates:
        status = updates["status"]
        if status not in {"draft", "live", "paused", "closed"}:
            raise InvalidGameUpdate("status must be one of draft, live, paused, closed")
        game["status"] = status
        if status == "paused":
            freeze_clock(game)
        elif status == "live" and not game["clock"].get("isRunning"):
            start_clock(game)
        elif status == "closed":
            freeze_clock(game)

    normalize_clock(game)
    game["updatedAt"] = utc_now_iso()
    return game


class BlobGameStore:
    def __init__(self, connection_string: Optional[str], container_name: str) -> None:
        self._connection_string = connection_string
        self._container_name = container_name or "games"
        self._blob_service_client: Optional[BlobServiceClient] = None
        self._container_client = None
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _ensure_container(self):
        if not self._connection_string:
            raise GameStateError("AzureWebJobsStorage is not configured")
        connection_string = self._connection_string.strip()
        if connection_string == "UseDevelopmentStorage=true":
            connection_string = DEVSTORE_CONNECTION_STRING
        if self._container_client is None:
            self._blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            self._container_client = self._blob_service_client.get_container_client(self._container_name)
            try:
                self._container_client.create_container()
            except ResourceExistsError:
                pass
        return self._container_client

    def _blob_name(self, game_id: str) -> str:
        return f"{sanitize_game_id(game_id)}.json"

    def create_game(self, home_club_id: str, away_club_id: str, layout_id: str) -> Dict[str, Any]:
        game = build_initial_game(home_club_id, away_club_id, layout_id)
        self.save_game(game)
        return serialize_game(game)

    def save_game(self, game: Dict[str, Any]) -> None:
        container = self._ensure_container()
        document = {"version": 1, "game": game}
        container.upload_blob(name=self._blob_name(game["gameId"]), data=json.dumps(document).encode("utf-8"), overwrite=True)
        self._cache[game["gameId"]] = copy.deepcopy(game)

    def load_game(self, game_id: str) -> Dict[str, Any]:
        game_id = sanitize_game_id(game_id)
        if game_id in self._cache:
            cached = copy.deepcopy(self._cache[game_id])
            normalize_clock(cached)
            self._cache[game_id] = copy.deepcopy(cached)
            return cached

        container = self._ensure_container()
        try:
            blob = container.download_blob(self._blob_name(game_id))
        except ResourceNotFoundError as exc:
            raise GameNotFoundError("Game not found") from exc

        payload = json.loads(blob.readall())
        game = payload.get("game")
        if not isinstance(game, dict):
            raise GameStateError("Stored game payload is invalid")
        ensure_layout_id(game)
        normalize_clock(game)
        self._cache[game_id] = copy.deepcopy(game)
        return copy.deepcopy(game)

    def get_game_response(self, game_id: str) -> Dict[str, Any]:
        return serialize_game(self.load_game(game_id))

    def update_game(self, game_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        game = self.load_game(game_id)
        updated = apply_game_update(game, updates)
        self.save_game(updated)
        return serialize_game(updated)

    def delete_game(self, game_id: str) -> None:
        game_id = sanitize_game_id(game_id)
        container = self._ensure_container()
        try:
            container.delete_blob(self._blob_name(game_id))
        except ResourceNotFoundError as exc:
            raise GameNotFoundError("Game not found") from exc
        self._cache.pop(game_id, None)