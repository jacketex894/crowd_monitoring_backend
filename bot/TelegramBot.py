#官方函式庫
import sys
import asyncio

#第三方函式庫
import telegram

class TelegramBOT:
    def __init__(self,bot_token,chat_id):
        bot_token = bot_token
        chat_id = chat_id
        bot = telegram.Bot(bot_token)