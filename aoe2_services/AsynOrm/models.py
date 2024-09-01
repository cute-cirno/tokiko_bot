from tortoise.models import Model
from tortoise import fields


class Aoe2Aka(Model):
    name = fields.CharField(max_length=255)
    player_id = fields.IntField()

    class Meta:
        table = 'aoe2_aka'
        indexes = [
            ('name',),
            ('player_id',),
        ]


class Aoe2Fan(Model):
    player_id = fields.IntField()
    qq_id = fields.IntField()
    group_id = fields.IntField()
    sub = fields.BooleanField(default=True)
    end = fields.BooleanField(default=False)
    mark = fields.CharField(max_length=255, null=True)
    create_time = fields.DatetimeField(null=True, auto_now=True)

    class Meta:
        table = 'aoe2_fan'
        unique_together = ('player_id', 'group_id', 'qq_id')


class Aoe2Player(Model):
    player_id = fields.IntField(pk=True)
    player_name = fields.CharField(max_length=255)
    rating_1v1 = fields.IntField(null=True)
    rating_tg = fields.IntField(null=True)
    country = fields.CharField(max_length=255, null=True)

    class Meta:
        table = 'aoe2_player'


class TodoList(Model):
    id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=11)
    thing = fields.CharField(max_length=255, null=True)
    completed = fields.BooleanField(default=False)
    create_at = fields.DatetimeField(null=True)
    complete_at = fields.DatetimeField(null=True)

    class Meta:
        table = 'todo_list'