import re

from random import choice, shuffle

from aiogram import Router, F
from aiogram.types import (Message, CallbackQuery, 
    InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from Levenshtein import ratio

from bot_logging import get_logger
from words import vocabulary


class Words(StatesGroup):
    wait_user_input = State()
    correct_word = State()


logger = get_logger(__name__)
router = Router()


def get_random_word_pair() -> list:
    return list(choice(list(vocabulary.items())))


def normalize_word(word: str) -> str:
    word = word.strip().lower()

    word = re.sub(r'^to\s+', '', word)
    word = re.sub(r'^(a|an)\s+', '', word)
    word = re.sub(r'\s+', ' ', word)

    return word


def get_ratio(first_word: str, second_word: str) -> float:
    first_word = normalize_word(first_word)
    second_word = normalize_word(second_word)

    similarity_score = ratio(first_word, second_word)
    
    return round(similarity_score, 2)


async def get_correct_word(state: FSMContext) -> str:
    user_data = await state.get_data()
    correct_word = user_data['correct_word']

    return correct_word


@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext) -> None:
    user = message.from_user
    logger.info(f"{user.id} {user.username} {user.full_name} START_CMD\n")

    await message.answer(f"Бот чтобы выучить слова от Светланы Вениаминовны =)." \
            f"\n\nВсего слов: {len(vocabulary)}")

    await state.update_data(used_words=set()) 

    await send_words(message, state)


@router.message(Command('skip'))
async def skip_cmd(message: Message, state: FSMContext) -> None:
    user = message.from_user
    logger.info(f"{user.id} {user.username} {user.full_name} skip")

    await send_words(message, state)


async def send_words(message: Message, state: FSMContext) -> None:
    rand_pair = get_random_word_pair()

    skip_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Пропустить →", callback_data="skip")]]
)
    shuffle(rand_pair)

    await state.update_data(correct_word=rand_pair[0])
    await state.set_state(Words.wait_user_input)

    await message.answer(f"<b>{rand_pair[1].capitalize()}</b>", reply_markup=skip_kb)


@router.message(Words.wait_user_input)
async def check_user_answer(message: Message, state: FSMContext) -> None:
    user_answer = message.text.strip().lower()
    user = message.from_user

    correct_word = await get_correct_word(state)

    normalized_user_answer = normalize_word(user_answer)
    normalized_correct_word = normalize_word(correct_word)

    ratio = get_ratio(normalized_user_answer, normalized_correct_word)
    threshold = 0.8

    if int(ratio) == 1:
        text = "✅ <b>Правильно!</b>"
    elif ratio >= threshold:
        text = f"☑️ <b>Правильно!</b> <i>Возможно, в слове есть опечатка.</i>" \
               f"\nДолжно быть: <code>{correct_word}</code>"
    else:
        text = f"❌ <b>Неверно!</b> Правильно: <code>{correct_word}</code>"

    await message.answer(text)
    
    logger.info(f"{user.id} {user.username} {user.full_name} input: {user_answer} correct: {correct_word}")

    await send_words(message, state)


@router.callback_query(F.data == "skip")
async def stop_cmd(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    message = callback.message
    correct_word = await get_correct_word(state)

    await message.answer(f"<b>Ответ:</b> <code>{correct_word}</code>")
    await send_words(message, state)



