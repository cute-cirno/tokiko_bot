class Player:
    def __init__(self, data: dict) -> None:
        self.id: int = data.get("id", 0)
        self.name: str = data.get("name", "AI")
        self.number: int = data.get("number", 0)
        self.rating: int = data.get("rating", 0)
        self.rating_1v1: int = data.get("rating_1v1", 0)
        self.rating_tg: int = data.get("rating_tg", 0)
        self.country: str = data.get("country", "")
        # ongoing
        self.civilization: str = data.get("civilization", "")
        self.color: int = data.get("color", 0)
        self.color_hex: str = data.get("color_hex", "")
        self.team: int = data.get("team", 0)
        # lobby
        self.random_civilization: bool = data.get("random_civilization", False)
        self.random_color: bool = data.get("random_color", False)
