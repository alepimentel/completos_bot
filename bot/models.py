from datetime import date, datetime, time, timedelta
from os import environ

import peewee

db = peewee.SqliteDatabase(environ["DATABASE_URL"], pragmas={"foreign_keys": 1})


class BaseModel(peewee.Model):
    class Meta:
        database = db
        legacy_table_names = False


class User(BaseModel):
    bot = peewee.BooleanField()
    user_id = peewee.IntegerField(unique=True)
    username = peewee.CharField(unique=True, max_length=32)

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
    chat_id = peewee.IntegerField()

    @property
    def config(self):
        return self.configs.get()

    def members(self):
        return (
            User.select()
            .join(ChatMember)
            .where(
                User.bot == False, ChatMember.chat == self, ChatMember.left_at.is_null()
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
    chat = peewee.ForeignKeyField(Chat)
    user = peewee.ForeignKeyField(User)
    left_at = peewee.DateTimeField(null=True)


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

    chat = peewee.ForeignKeyField(Chat, backref="configs", unique=True)
    period = peewee.SmallIntegerField(constraints=[peewee.Check("period > 0")])
    default_time = peewee.TimeField(default=time(hour=19))
    default_weekday = peewee.SmallIntegerField(
        choices=WEEKDAYS,
        constraints=[peewee.Check("default_weekday BETWEEN 0 AND 6")],
        default=3,
    )

    @property
    def week_period(self):
        return timedelta(weeks=self.chat.config.period)

    def next_default_day(self):
        days_until_next_default = (self.default_weekday - date.today().weekday()) % 7

        return date.today() + timedelta(days=days_until_next_default)

    def should_send_poll(self):
        last_poll = self.chat.polls.order_by(Poll.id.desc()).first()
        last_meal = self.chat.meals.order_by(Meal.id.desc()).first()

        old_poll = (
            last_poll is None
            or date.today() - last_poll.created_at.date() >= self.week_period
        )
        old_meal = (
            last_meal is None
            or self.next_default_day() - last_meal.date >= self.week_period
        )

        return old_meal and old_poll


class Meal(BaseModel):
    chat = peewee.ForeignKeyField(Chat, backref="meals")
    host = peewee.ForeignKeyField(User)
    place = peewee.CharField(max_length=64)
    date = peewee.DateField()

    def members(self):
        return MealMember.select().where(MealMember.meal == self)


class MealMember(BaseModel):
    user = peewee.ForeignKeyField(User)
    meal = peewee.ForeignKeyField(Meal, backref="participants")

    class Meta:
        indexes = ((("user", "meal"), True),)


class Poll(BaseModel):
    chat = peewee.ForeignKeyField(Chat, backref="polls")
    creator = peewee.ForeignKeyField(User)
    meal = peewee.ForeignKeyField(Meal, null=True)

    poll_id = peewee.CharField(null=True)
    message_id = peewee.IntegerField(null=True)
    created_at = peewee.DateTimeField(default=datetime.now)
    closed_at = peewee.DateTimeField(null=True)

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
            PollOption.select(peewee.fn.SUM(PollOption.votes))
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
    poll = peewee.ForeignKeyField(Poll, backref="options")

    text = peewee.CharField(max_length=64)
    votes = peewee.SmallIntegerField(default=0)


class DefaultOption(BaseModel):
    chat = peewee.ForeignKeyField(Chat, backref="default_options")
    text = peewee.CharField(max_length=64)

    class Meta:
        indexes = ((("chat", "text"), True),)
