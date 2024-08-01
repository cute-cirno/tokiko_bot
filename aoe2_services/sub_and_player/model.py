from typing import Dict, List, Optional, Union
import time


class OngoingPlayerModel:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get("id", 0)
        self.name: str = data.get("name", "AI")
        self.twitch: str = data.get("twitch", "")
        self.number: int = data.get("number", 0)
        self.rating: int = data.get("rating", 0)
        self.rating_1v1: int = data.get("rating_1v1", 0)
        self.rating_tg: int = data.get("rating_tg", 0)
        self.country: str = data.get("country", "")
        self.civilization: str = data.get("civilization", "")
        self.color: int = data.get("color", 0)
        self.color_hex: str = data.get("color_hex", "")
        self.team: int = data.get("team", 0)


class OngoingModel:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get("id", 0)
        self.status: str = data.get("status", "ongoing")
        self.rms: str = data.get("rms", "")
        self.lobby_created: int = data.get("lobby_created", 0)
        self.ranked: bool = data.get("ranked", False)
        self.server: str = data.get("server", "")
        self.slots: int = data.get("slots", 0)
        self.diplomacy: bool = data.get("diplomacy", False)
        self.start_time: int = data.get("started", 0)
        self.average_rating: float = float(data.get("average_rating", 0))
        self.started: int = data.get("started", 0)
        self.type: str = data.get("type", "")
        self.lobby: str = data.get("lobby", "")
        self.spectating_delay: int = data.get("spectating_delay", 0)
        self.spectating_disabled: bool = data.get("spectating_disabled", False)
        self.players: List[OngoingPlayerModel] = [
            OngoingPlayerModel(player_data) for player_data in data.get("players", [])
        ]


class Ongoing:
    def __init__(self) -> None:
        self._all_room: Dict[int, OngoingModel] = {}
        self._player_id_at_room: Dict[int, int] = {}
        self._player_name_at_room: Dict[str, int] = {}
        self._room_expired: Dict[int, int] = {}

    def remove_room(self, room_id: int):
        if room_id in self._all_room:
            for player in self._all_room[room_id].players:
                if player.id == 0:
                    continue
                self._player_id_at_room.pop(player.id, None)
                self._player_name_at_room.pop(player.name, None)
            self._all_room.pop(room_id)
            self._room_expired.pop(room_id, None)

    def add_room(self, room: OngoingModel):
        self._all_room[room.id] = room
        self._room_expired[room.id] = room.started + 3600
        for player in room.players:
            if player.id == 0:
                continue
            self._player_id_at_room[player.id] = room.id
            self._player_name_at_room[player.name] = room.id

    def get_room(self, identifier: Union[int, str]) -> Optional[OngoingModel]:
        if isinstance(identifier, int):
            room_id = self._player_id_at_room.get(identifier,None)
        elif isinstance(identifier, str):
            for name, room_id in self._player_name_at_room.items():
                if identifier.lower() in name.lower():
                    break
        if room_id is not None:
            return self._all_room.get(room_id)
        return None

    def get_room_by_id(self, room_id: int) -> Optional[OngoingModel]:
        return self._all_room.get(room_id, None)

    def remove_expired_room(self):
        now = int(time.time())
        expired_rooms = [
            room_id
            for room_id, expired_time in self._room_expired.items()
            if expired_time < now
        ]
        for room_id in expired_rooms:
            self.remove_room(room_id)
            
    @property
    def room_count(self) -> int:
        return len(self._all_room)


class LobbyPlayerModel:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get("id", 0)
        self.name: str = data.get("name", "AI")
        self.number: int = data.get("number", 0)
        self.rating_tg: int = data.get("rating_tg", 0)
        self.country: str = data.get("country", "")
        self.random_civilization: bool = data.get("random_civilization", False)
        self.random_color: bool = data.get("random_color", False)
        self.team: int = data.get("team", 0)


class LobbyModel:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get("id", 0)
        self.status: str = data.get("status", "lobby")
        self.game: str = data.get("game", "")
        self.rms: str = data.get("rms", "")
        self.lobby: str = data.get("lobby", "")
        self.lobby_created: int = data.get("lobby_created", 0)
        self.ai: bool = data.get("ai", False)
        self.link: str = data.get("link", "")
        self.server: str = data.get("server", "")
        self.slots: int = data.get("slots", 0)
        self.occupied_slots: int = data.get("occupied_slots", 0)
        self.average_rating: int = data.get("average_rating", 0)
        self.average_1v1_rating: int = data.get("average_1v1_rating", 0)
        self.average_tg_rating: int = data.get("average_tg_rating", 0)
        self.password: bool = data.get("password", False)
        self.type: str = data.get("type", "")
        self.players: List[LobbyPlayerModel] = [
            LobbyPlayerModel(player_data) for player_data in data.get("players", [])
        ]
        self.teams: List[dict] = data.get(
            "teams", []
        )  # Teams can be a list of dictionaries
        self.scenario: str = data.get("scenario", "")
        self.spectating_disabled: bool = data.get("spectating_disabled", False)
        self.rematch: bool = data.get("rematch", False)
        self.spectating_delay: int = data.get("spectating_delay", 0)
        self.data_mod: str = data.get("data_mod", "")
        self.custom: bool = data.get("custom", False)
        self.campaign: str = data.get("campaign", "")
        self.verified: bool = data.get("verified", False)
        self.pro: bool = data.get("pro", False)
        self.ranked: bool = data.get("ranked", False)
        self.min_rating: int = data.get("min_rating", 0)
        self.leaderboard: str = data.get("leaderboard", "")
        self.max_rating: int = data.get("max_rating", 0)
        self.twitch: bool = data.get("twitch", False)


class Lobby:
    def __init__(self) -> None:
        self._all_room: Dict[int, LobbyModel] = {}
        self._player_id_at_room: Dict[int, int] = {}
        self._player_name_at_room: Dict[str, int] = {}
        self._room_expired: Dict[int, int] = {}

    def add_room(self, lobby: LobbyModel):
        self._all_room[lobby.id] = lobby
        for player in lobby.players:
            if player.id == 0:
                continue
            self._player_id_at_room[player.id] = lobby.id
            self._player_name_at_room[player.name] = lobby.id

    def remove_room(self, lobby_id: int):
        if lobby_id in self._all_room:
            for player in self._all_room[lobby_id].players:
                self._player_id_at_room.pop(player.id, None)
                self._player_name_at_room.pop(player.name, None)
            del self._all_room[lobby_id]
            
    def get_room(self, identifier: Union[int, str]) -> Optional[LobbyModel]:
        if isinstance(identifier, int):
            room_id = self._player_id_at_room.get(identifier,None)
        elif isinstance(identifier, str):
            for name, room_id in self._player_name_at_room.items():
                if identifier.lower() in name.lower():
                    break
        if room_id is not None:
            return self._all_room.get(room_id)
        return None

    def get_room_by_player(self, player_id: int) -> int:
        return self._player_id_at_room.get(player_id, 0)

    def get_room_by_id(self, lobby_id: int) -> Optional[LobbyModel]:
        return self._all_room.get(lobby_id, None)
    
    @property
    def room_count(self) -> int:
        return len(self._all_room)
