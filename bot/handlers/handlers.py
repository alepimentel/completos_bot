from datetime import date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from peewee import fn

from bot.models import db, Chat, ChatMember, Meal, MealMember, Poll, PollOption, User


@db.transaction()
async def receive_poll_update(update, context):
    poll = Poll.get_or_none(poll_id=update.poll.id)

    if poll is None:
        return

    for option in update.poll.options:
        poll_option = PollOption.get(
            PollOption.poll == poll, PollOption.text == option.text
        )
        poll_option.votes = option.voter_count
        poll_option.save()

    if poll.closed_at:
        await schedule_meal(context.bot, poll)

    if poll.chat.member_count() == update.poll.total_voter_count and not poll.closed_at:
        if not update.poll.is_closed:
            await context.bot.stop_poll(poll.chat.chat_id, poll.message_id)
            poll.close()


async def schedule_meal(bot, poll):
    host = (
        User.select(User.id, fn.COUNT(Meal.id).alias("count"))
        .join(ChatMember)
        .where(ChatMember.chat_id == poll.chat)
        .join_from(User, Meal)
        .group_by(User.id)
        .first()
    ) or poll.chat.members().first()

    if poll.elected_option() is None:
        return await bot.send_message(
            poll.chat.chat_id, "Nadie votó. 😭", reply_to_message_id=poll.message_id
        )

    meal_date = (
        poll.chat.config.next_default_day()
        if poll.chat.configs.get_or_none()
        else date.today()
    )

    meal = Meal.create(
        chat=poll.chat,
        host=host,
        place=poll.elected_option().text,
        date=meal_date,
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "Si 😬", callback_data=f"confirm_participation:{meal.id}:1"
            ),
            InlineKeyboardButton(
                "No 😞", callback_data=f"confirm_participation:{meal.id}:0"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await bot.send_message(
        poll.chat.chat_id,
        f"Nos vemos en {meal.place} el {meal.date}! Puedes ir?",
        reply_markup=reply_markup,
    )


async def confirm_participation(update, context):
    query = update.callback_query
    _, meal_id, answer = update.callback_query.data.split(":")

    await query.answer()

    user = User.get_or_create_and_add_to_chat(
        update.callback_query.from_user.id,
        update.callback_query.message.chat.id,
        defaults={
            "username": update.callback_query.message.from_user.username,
            "bot": update.callback_query.message.from_user.is_bot,
        },
    )
    meal = Meal.get(id=meal_id)
    meal_member = MealMember.get_or_none(meal=meal, user=user)

    if meal_member and int(answer) == 0:
        meal_member.delete_instance()
    if meal_member is None and int(answer) == 1:
        MealMember.create(meal_id=meal_id, user=user)


async def new_chat_members(update, context):
    chat, _ = Chat.get_or_create(chat_id=update.message.chat.id)
    for new_member in update.message.new_chat_members:
        user, _ = User.get_or_create(
            user_id=new_member.id,
            defaults={
                "username": new_member.username,
                "bot": new_member.is_bot,
            },
        )

        chat.add_member(user)


async def left_chat_member(update, context):
    chat, _ = Chat.get_or_create(chat_id=update.message.chat.id)
    user, _ = User.get_or_create(
        user_id=update.message.left_chat_member.id,
        defaults={
            "username": update.message.left_chat_member.username,
            "bot": update.message.left_chat_member.is_bot,
        },
    )

    chat.remove_member(user)
