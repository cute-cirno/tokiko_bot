from datetime import datetime, timedelta


class Sub():
    def __init__(self, **sub_info):
        self.nickname: str = sub_info.get("mark", "")
        self.player_id: int = sub_info.get("player_id",0)
        self.create_time: datetime = (
            sub_info.get("create_time", datetime.now()))
        self.priority: int = 10
        self.group_id: int = sub_info.get("group_id", 0)
        self.qq_id: int = sub_info.get("qq_id", 0)
        self.sub: bool = bool(sub_info.get("sub", False))
        self.end: bool = bool(sub_info.get("end", False))
        self.sub_type: int = 0

    def isexpire(self) -> bool:
        if self.sub_type == 0:
            delta = timedelta(days=90)
        elif self.sub_type == 1:
            delta = timedelta(days=30)
        elif self.sub_type == 2:
            delta = timedelta(days=7)
        elif self.sub_type == 3:
            delta = timedelta(hours=12)
        return datetime.now() > self.create_time + delta
