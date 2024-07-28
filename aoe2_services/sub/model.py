from typing import Dict, List
import time


class OngoingPlayerModel:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get('id', 0)
        self.name: str = data.get('name', 'AI')
        self.twitch: str = data.get('twitch', '')
        self.number: int = data.get('number', 0)
        self.rating: int = data.get('rating', 0)
        self.rating_1v1: int = data.get('rating_1v1', 0)
        self.rating_tg: int = data.get('rating_tg', 0)
        self.country: str = data.get('country', '')
        self.civilization: str = data.get('civilization', '')
        self.color: int = data.get('color', 0)
        self.color_hex: str = data.get('color_hex', '')
        self.team: int = data.get('team', 0)
        

class OngoingRoomModel:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get('id', 0)
        self.status: str = data.get('status', 'ongoing')
        self.map_name: str = data.get('game', '')
        self.lobby_created: int = data.get('lobby_created', 0)
        self.ranked: bool = data.get('ranked', False)
        self.server: str = data.get('server', '')
        self.slots: int = data.get('slots', 0)
        self.start_time: int = data.get('started', 0)
        self.average_rating: float = float(data.get('average_rating', 0))
        self.started: int = data.get('started', 0)
        self.type: str = data.get('type', '')
        self.lobby: str = data.get('lobby', '')
        self.spectating_delay: int = data.get('spectating_delay', 0)
        self.spectating_disabled: bool = data.get('spectating_disabled', False)
        self.players: List[OngoingPlayerModel] = [OngoingPlayerModel(player_data) for player_data in data.get('players', [])]



class Ongoing:
    def __init__(self) -> None:
        self.all_room: Dict[int, OngoingRoomModel] = {}
        self.player_at_room: Dict[int, int] = {}
        self.room_expired: Dict[int, int] = {}

    def remove_room(self, room_id: int):
        if room_id in self.all_room:
            for player in self.all_room[room_id].players:
                self.player_at_room.pop(player.id, None)
            self.all_room.pop(room_id)
            self.room_expired.pop(room_id, None)

    def add_room(self, room: OngoingRoomModel):
        if room.id in self.all_room:
            print(f"Room {room.id} already exists. Updating existing room.")
        self.all_room[room.id] = room
        self.room_expired[room.id] = room.started + 3600
        for player in room.players:
            self.player_at_room[player.id] = room.id
        print(f"Room {room.id} added or updated with {len(room.players)} players.")

    def get_room_by_player(self, player_id: int):
        room_id = self.player_at_room.get(player_id, 0)
        return room_id
    
    def remove_expired_room(self):
        now = int(time.time())
        expired_rooms = [room_id for room_id, expired_time in self.room_expired.items() if expired_time < now]
        for room_id in expired_rooms:
            self.remove_room(room_id)
            print(f"Expired room {room_id} has been removed.")


class LobbyPlayerModel:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get('id', 0)
        self.name: str = data.get('name', 'AI')
        self.number: int = data.get('number', 0)
        self.rating_tg: int = data.get('rating_tg', 0)
        self.country: str = data.get('country', '')
        self.random_civilization: bool = data.get('random_civilization', False)
        self.random_color: bool = data.get('random_color', False)
        self.team: int = data.get('team', 0)



class LobbyModel:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get('id', 0)
        self.status: str = data.get('status', 'lobby')
        self.game: str = data.get('game', '')
        self.rms: str = data.get('rms', '')
        self.lobby: str = data.get('lobby', '')
        self.lobby_created: int = data.get('lobby_created', 0)
        self.ai: bool = data.get('ai', False)
        self.link: str = data.get('link', '')
        self.server: str = data.get('server', '')
        self.slots: int = data.get('slots', 0)
        self.occupied_slots: int = data.get('occupied_slots', 0)
        self.average_rating: int = data.get('average_rating', 0)
        self.average_1v1_rating: int = data.get('average_1v1_rating', 0)
        self.average_tg_rating: int = data.get('average_tg_rating', 0)
        self.password: bool = data.get('password', False)
        self.type: str = data.get('type', '')
        self.players: List[LobbyPlayerModel] = [LobbyPlayerModel(player_data) for player_data in data.get('players', [])]
        self.teams: List[dict] = data.get('teams', [])  # Teams can be a list of dictionaries
        self.scenario: str = data.get('scenario', '')
        self.spectating_disabled: bool = data.get('spectating_disabled', False)
        self.rematch: bool = data.get('rematch', False)
        self.spectating_delay: int = data.get('spectating_delay', 0)
        self.data_mod: str = data.get('data_mod', '')
        self.custom: bool = data.get('custom', False)
        self.campaign: str = data.get('campaign', '')
        self.verified: bool = data.get('verified', False)
        self.pro: bool = data.get('pro', False)
        self.ranked: bool = data.get('ranked', False)
        self.min_rating: int = data.get('min_rating', 0)
        self.leaderboard: str = data.get('leaderboard', '')
        self.max_rating: int = data.get('max_rating', 0)
        self.twitch: bool = data.get('twitch', False)

    

class Lobby:
    def __init__(self) -> None:
        self.all_lobbies: Dict[int, LobbyModel] = {}

    def add_lobby(self, lobby: LobbyModel):
        self.all_lobbies[lobby.id] = lobby
        print(f"Lobby {lobby.id} added with {len(lobby.players)} players.")

    def remove_lobby(self, lobby_id: int):
        if lobby_id in self.all_lobbies:
            del self.all_lobbies[lobby_id]
            print(f"Lobby {lobby_id} removed.")

    def get_lobby(self, lobby_id: int):
        return self.all_lobbies.get(lobby_id, None)
