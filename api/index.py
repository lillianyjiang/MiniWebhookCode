# File: api/index.py
from pydantic import BaseModel
from typing import List, Final, Optional
from fastapi import FastAPI
from telegram import Update, Bot, InlineQueryResultCachedSticker
from telegram.ext import Dispatcher, CommandHandler, InlineQueryHandler
import pathlib, random, os

from helpers import load_mappings


# ----- config ------------------------------------------------------

from utils.load_env import load_env
load_env()                       # silently does nothing on Vercel
TOKEN: Final = os.environ["BOT_TOKEN"]
BOT_USERNAME: Final = "@MiniDogStickerBot"
STICKER_SET_NAME = "Mini3554"
STICKERS = pathlib.Path(__file__).with_name("stickers.json")


# ----- load mapping ------------------------------------------------
emoji_to_file_ids, keyword_to_file_ids = load_mappings()
all_keywords_readable = ", ".join(sorted(keyword_to_file_ids))  # for /seeDictionary

# ----- FastAPI skeleton -------------------------------------------
app = FastAPI()

class TelegramWebhook(BaseModel):
    '''
    Telegram Webhook Model using Pydantic for request body validation
    '''
    update_id: int
    message: Optional[dict]
    edited_message: Optional[dict]
    channel_post: Optional[dict]
    edited_channel_post: Optional[dict]
    inline_query: Optional[dict]
    chosen_inline_result: Optional[dict]
    callback_query: Optional[dict]
    shipping_query: Optional[dict]
    pre_checkout_query: Optional[dict]
    poll: Optional[dict]
    poll_answer: Optional[dict]

# ----- command handlers -------------------------------------------
def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text="Woof! I am mini. Feel free to express yourself with my stickers")

def help(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text="Woof! I am mini. Please type @MiniDogStickerBot followed by keywords or emoji to find my relevant stickers to send")

def seeDictionary(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text=f"Woof! Here are all the keywords you can call to get my stickers {all_keywords_readable}")

def handle_inline_query(update, context):
    q = update.inline_query.query.strip().lower()
    results: List[InlineQueryResultCachedSticker] = []

    # 1️⃣ exact emoji
    if q in emoji_to_file_ids:
        for fid in emoji_to_file_ids[q]:
            results.append(
                InlineQueryResultCachedSticker(id=fid[-10:], sticker_file_id=fid)
            )

    # 2️⃣ substring keyword (find emoji based on a keyword)
    if q:
        for kw, fids in keyword_to_file_ids.items():
            if q in kw:
                for fid in fids:
                    results.append(
                        InlineQueryResultCachedSticker(
                            id=f"{fid[-10:]}:{kw}", sticker_file_id=fid
                        )
                    )
    # 3️⃣ empty query → show random 5 stickers
    else:
        sample = random.sample(sum(emoji_to_file_ids.values(), []), k=min(5, len(emoji_to_file_ids)))
        for fid in sample:
            results.append(InlineQueryResultCachedSticker(id=f"default:{fid[-10:]}", sticker_file_id=fid))

    context.bot.answer_inline_query(
        inline_query_id=update.inline_query.id,
        results=results[:10],
        cache_time=60,
    )


# ----- dispatcher factory (one per webhook call) ------------------
def register_handlers(dispatcher):
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    seeDictionary_handler = CommandHandler('seeDictionary', seeDictionary)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(seeDictionary_handler)
    dispatcher.add_handler(InlineQueryHandler(handle_inline_query))

# ----- FastAPI endpoints ------------------------------------------
@app.post("/webhook")
def webhook(webhook_data: TelegramWebhook):
    bot = Bot(token = TOKEN)
    update = Update.de_json(webhook_data.__dict__, bot)
    dispatcher = Dispatcher(bot, None, workers = 1, use_context = True)
    register_handlers(dispatcher)
    dispatcher.process_update(update)
    return {"message": "ok"}
    
@app.get("/")
def index():
    return {"message": "MiniDogSticker webhook is alive!"}

# --- Vercel entry point ---
handler = app
