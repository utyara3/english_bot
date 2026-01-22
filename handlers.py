from random import choice, shuffle

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot_logging import get_logger
from words import vocabulary

class Words(StatesGroup):
    wait_user_input = State()
    correct_word = State()




logger = get_logger(__name__)
router = Router()


def get_random_word_pair() -> list:
    return list(choice(list(vocabulary.items())))


@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext) -> None:
    user = message.from_user
    logger.info(f"{user.id} {user.username} {user.full_name} START_CMD\n")

    await message.answer(f"Всего слов: {len(vocabulary)}")

    await send_words(message, state)


async def send_words(message: Message, state: FSMContext) -> None:
    rand_pair = get_random_word_pair()
    shuffle(rand_pair)

    await state.update_data(correct_word=rand_pair[0])
    await state.set_state(Words.wait_user_input)

    await message.answer(f"<b>{rand_pair[1].capitalize()}</b>")


@router.message(Words.wait_user_input)
async def check_user_answer(message: Message, state: FSMContext) -> None:
    user_answer = message.text.strip().lower()
    user = message.from_user


    user_data = await state.get_data()
    correct_word = user_data['correct_word']

    if user_answer == correct_word:
        text = "Правильно!"

    else:
        text = f"Неверно! Правильно: <code>{correct_word}</code>"

    await message.answer(text)
    
    logger.info(f"{user.id} {user.username} {user.full_name} input: {user_answer} correct: {correct_word}")

    await send_words(message, state)


@router.message(Command('stop'))
async def stop_cmd(message: Message) -> None:
    await message.answer("приостановлено. напиши /start чтобы продолжить...")




