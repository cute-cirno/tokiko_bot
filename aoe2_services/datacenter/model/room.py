from model.player import Player
from datetime import datetime


class Room:
    def __init__(self, data: dict):
        self.id: int = data.get("id", 0)
        self.status: str = data.get("status", "")
        self.game: str = data.get("game", "")
        self.rms: str = data.get("rms", "")
        self.lobby: str = data.get("lobby", "")
        self.lobby_created: int = data.get("lobby_created", 0)
        self.link: str = data.get("link", "")
        self.server: str = data.get("server", "")
        self.slots: int = data.get("slots", 0)
        self.occupied_slots: int = data.get("occupied_slots", 0)
        self.average_rating: int = data.get("average_rating", 0)
        self.average_1v1_rating: int = data.get("average_1v1_rating", 0)
        self.average_tg_rating: int = data.get("average_tg_rating", 0)
        self.type: str = data.get("type", "")
        self.teams: list[dict] = data.get("teams", [])
        self.scenario: str = data.get("scenario", "")
        self.spectating_disabled: bool = data.get("spectating_disabled", False)
        self.rematch: bool = data.get("rematch", False)
        self.spectating_delay: int = data.get("spectating_delay", 0)
        self.data_mod: str = data.get("data_mod", "")
        self.custom: bool = data.get("custom", False)
        self.campaign: str = data.get("campaign", "")
        self.verified: bool = data.get("verified", False)
        self.pro: bool = data.get("pro", False)
        self.min_rating: int = data.get("min_rating", 0)
        self.leaderboard: str = data.get("leaderboard", "")
        self.max_rating: int = data.get("max_rating", 0)
        # ongoing
        self.started: int = data.get("started", 0)
        self.twitch: bool = data.get("twitch", False)
        self.ranked: bool = data.get("ranked", False)
        self.diplomacy: str = data.get("diplomacy", "")
        self.controller: bool = data.get("controller", False)
        self.ai: bool = data.get("ai", False)
        # lobby
        self.password: bool = data.get("password", False)
        # expire
        self.expired: int = int(datetime.now().timestamp())
        self.players: list[Player] = [
            Player(player_data) for player_data in data.get("players", [])
        ]
    
    @property
    def player_set(self) -> set[int]:
        return {p.id for p in self.players}