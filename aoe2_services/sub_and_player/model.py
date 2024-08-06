from typing import List, Dict, Any,Tuple, Optional, Union
import time

class Room:
    def __init__(self, data: Dict[str, Any]):
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
        self.players: List[Dict[str, Any]] = data.get("players", [])
        self.teams: List[Dict[str, Any]] = data.get("teams", [])
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


class OngoingPlayer:
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


class OngoingRoom(Room):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.started: int = data.get("started", 0)
        self.twitch: bool = data.get("twitch", False)
        self.ranked: bool = data.get("ranked", False)
        self.diplomacy: str = data.get("diplomacy", "")
        self.started: int = data.get("started", 0)
        self.controller: bool = data.get("controller", False)
        self.ai: bool = data.get("ai", False)
        self.players: List[OngoingPlayer] = [
            OngoingPlayer(player_data) for player_data in data.get("players", [])
        ]


class Ongoing:
    def __init__(self) -> None:
        self._all_room: Dict[int, OngoingRoom] = {}
        self._player_at_room: Dict[Tuple[int, str], int] = {}
        self._room_expired: Dict[int, int] = {}

    def remove_room(self, room_id: int):
        if room_id in self._all_room:
            for player in self._all_room[room_id].players:
                if player.id == 0:
                    continue
                self._player_at_room.pop((player.id, player.name), None)
            self._all_room.pop(room_id)
            self._room_expired.pop(room_id, None)

    def add_room(self, room: OngoingRoom):
        self._all_room[room.id] = room
        self._room_expired[room.id] = room.started + 3600
        for player in room.players:
            if player.id == 0:
                continue
            self._player_at_room[(player.id, player.name)] = room.id

    def get_room(self, identifier: Union[int, str]) -> List[Optional[OngoingRoom]]:
        if isinstance(identifier, int):
            for k,room_id in self._player_at_room.items():
                if k[0] == identifier:
                    return [self._all_room.get(room_id,None)]
        else:
            candidate_rooms = [room_id for k, room_id in self._player_at_room.items() if identifier.lower() == k[1].lower()]
            if len(candidate_rooms) == 0:
                candidate_rooms = [room_id for k, room_id in self._player_at_room.items() if identifier.lower() in k[1].lower()]
            return [self._all_room.get(room_id,None) for room_id in candidate_rooms]
        return []

    def get_room_by_id(self, room_id: int) -> Optional[OngoingRoom]:
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
    
    def initialize(self):
        self._all_room.clear()
        self._player_at_room.clear()
        self._room_expired.clear()


class LobbyPlayer:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get("id", 0)
        self.name: str = data.get("name", "AI")
        self.number: int = data.get("number", 0)
        self.rating_tg: int = data.get("rating_tg", 0)
        self.country: str = data.get("country", "")
        self.random_civilization: bool = data.get("random_civilization", False)
        self.random_color: bool = data.get("random_color", False)
        self.team: int = data.get("team", 0)


class LobbyRoom(Room):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.ai: bool = data.get("ai", False)
        self.password: bool = data.get("password", False)
        self.ranked: bool = data.get("ranked", False)
        self.twitch: bool = data.get("twitch", False)
        self.players: List[LobbyPlayer] = [
            LobbyPlayer(player_data) for player_data in data.get("players", [])
        ]


class Lobby:
    def __init__(self) -> None:
        self._all_room: Dict[int, LobbyRoom] = {}
        self._player_at_room: Dict[Tuple[int, str], int] = {}
        self._room_expired: Dict[int, int] = {}

    def add_room(self, lobby: LobbyRoom):
        self._all_room[lobby.id] = lobby
        for player in lobby.players:
            if player.id == 0:
                continue
            self._player_at_room[(player.id, player.name)] = lobby.id

    def remove_room(self, lobby_id: int):
        if lobby_id in self._all_room:
            for player in self._all_room[lobby_id].players:
                self._player_at_room.pop((player.id, player.name), None)
            del self._all_room[lobby_id]
            
    def get_room(self, identifier: Union[int, str]) -> List[Optional[LobbyRoom]]:
        if isinstance(identifier, int):
            for k,room_id in self._player_at_room.items():
                if k[0] == identifier:
                    return [self._all_room.get(room_id)]
        else:
            candidate_rooms = [room_id for k, room_id in self._player_at_room.items() if identifier.lower() == k[1].lower()]
            if len(candidate_rooms) == 0:
                candidate_rooms = [room_id for k, room_id in self._player_at_room.items() if identifier.lower() in k[1].lower()]
            return [self._all_room.get(room_id,None) for room_id in candidate_rooms]
        return []
    
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
    
    def initialize(self):
        self._all_room.clear()
        self._player_at_room.clear()
        self._room_expired.clear()
