from datetime import datetime, time
from os import environ

from peewee import *


db = SqliteDatabase(environ["DATABASE_URL"], pragmas={"foreign_keys": 1})


class BaseModel(Model):
    class Meta:
        database = db
        legacy_table_names = False


class User(BaseModel):
    bot = BooleanField()
    user_id = IntegerField(unique=True)
    username = CharField(unique=True, max_length=32)

    @classmethod
    def get_or_create_and_add_to_chat(cls, user_id, chat_id, defaults):
        chat = Chat.get(Chat.chat_id == chat_id)
        user, _ = cls.get_or_create(user_id=user_id, defaults=defaults)
        ChatMember.get_or_create(chat=chat, user=user)

        return user

    def in_chat(self, chat):
        return (
            ChatMember.select()
            .where(ChatMember.chat == chat, ChatMember.user == self)
            .count()
            == 1
        )


class Chat(BaseModel):
    chat_id = IntegerField()

    @property
    def config(self):
        return self.configs.get()

    def members(self):
        return (
            User.select()
            .join(ChatMember)
            .where(
                User.bot == False, ChatMember.chat == self, ChatMember.left_at == None
            )
        )

    def member_count(self):
        return self.members().count()

    def add_member(self, user):
        ChatMember.create(chat=self, member=user)

    def remove_member(self, user):
        chat_member = ChatMember.get(ChatMember.member == user)

        chat_member.left_at = datetime.now()
        chat_member.save()


class ChatMember(BaseModel):
    chat = ForeignKeyField(Chat)
    user = ForeignKeyField(User)
    left_at = DateTimeField(null=True)


class GatheringsConfiguration(BaseModel):
    WEEKDAYS = (
        (0, "monday"),
        (1, "tuesday"),
        (2, "wednesday"),
        (3, "thursday"),
        (4, "friday"),
        (5, "saturday"),
        (6, "sunday"),
    )

    chat = ForeignKeyField(Chat, backref="configs", unique=True)
    period = SmallIntegerField(constraints=[Check("period > 0")])
    default_time = TimeField(default=time(hour=19))
    default_weekday = SmallIntegerField(
        choices=WEEKDAYS,
        constraints=[Check("default_weekday BETWEEN 0 AND 6")],
        default=3,
    )


class Meal(BaseModel):
    chat = ForeignKeyField(Chat, backref="meal")
    host = ForeignKeyField(User)
    place = CharField(max_length=64)
    date = DateField()

    def members(self):
        return MealMember.select().where(MealMember.meal == self)


class MealMember(BaseModel):
    user = ForeignKeyField(User)
    meal = ForeignKeyField(Meal, backref="participants")

    class Meta:
        indexes = ((("user", "meal"), True),)


class Poll(BaseModel):
    chat = ForeignKeyField(Chat)
    creator = ForeignKeyField(User)
    meal = ForeignKeyField(Meal, null=True)

    poll_id = CharField(null=True)
    message_id = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.now)
    closed_at = DateTimeField(null=True)

    async def send(self, bot):
        options = [option.text for option in self.options]

        poll_response = await bot.send_poll(
            self.chat.chat_id,
            "A dónde vamos?",
            options,
            is_anonymous=False,
            allows_multiple_answers=True,
        )

        self.poll_id = poll_response.poll.id
        self.message_id = poll_response.message_id
        self.save()

    def close(self):
        self.closed_at = datetime.now()
        self.save()

    def votes(self):
        return (
            PollOption.select(fn.SUM(PollOption.votes))
            .where(PollOption.poll == self)
            .first()
            .votes
        )

    def elected_option(self):
        if self.closed_at is None or self.votes() == 0:
            return None

        return (
            PollOption.select()
            .where(PollOption.poll == self)
            .order_by(PollOption.votes.desc())
            .first()
        )


class PollOption(BaseModel):
    poll = ForeignKeyField(Poll, backref="options")

    text = CharField(max_length=64)
    votes = SmallIntegerField(default=0)


class DefaultOption(BaseModel):
    chat = ForeignKeyField(Chat, backref="default_options")
    text = CharField(max_length=64)

    class Meta:
        indexes = ((("chat", "text"), True),)
