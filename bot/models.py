from datetime import datetime
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

        chat_member.left_at = now()
        chat_member.save()


class ChatMember(BaseModel):
    chat = ForeignKeyField(Chat)
    user = ForeignKeyField(User)
    left_at = DateTimeField(null=True)


class Meal(BaseModel):
    chat = ForeignKeyField(Chat, backref="meal")
    host = ForeignKeyField(User)
    place = CharField(max_length=64)
    date = DateField()

    def members(self):
        return MealMember.select().where(MealMember.meal == self)


class MealMember(BaseModel):
    user = ForeignKeyField(User)
    meal = ForeignKeyField(Meal)

    class Meta:
        indexes = ((("user", "meal"), True),)


class Poll(BaseModel):
    chat = ForeignKeyField(Chat)
    creator = ForeignKeyField(User)
    meal = ForeignKeyField(Meal, null=True)

    poll_id = CharField(null=True)
    message_id = IntegerField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])
    closed_at = DateTimeField(null=True)

    def close(self):
        self.closed_at = datetime.now()
        self.save()

    def elected_option(self):
        if self.closed_at is None:
            return None

        return (
            PollOption.select()
            .where(PollOption.poll == self)
            .order_by(PollOption.votes.desc())
            .first()
        )


class PollOption(BaseModel):
    poll = ForeignKeyField(Poll)

    text = CharField(max_length=64)
    votes = SmallIntegerField(default=0)
