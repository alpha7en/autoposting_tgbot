import asyncio
from bot import Bot
from database import Database
import os

with open("tokens_gpt.txt", "r") as file:
    txt = file.read().split("\n")
    TOKENS_gpt=[]
for i in range(0,len(txt)):
    if txt[i]!="":TOKENS_gpt.append(txt[i])
print(TOKENS_gpt)
TOKEN = '5750793100:AAHv42lbgLHVy2QuMV-K-_ow9DBanPOot0Q' #tg_token
DB_NAME = 'your_database.db'


def main():
    db = Database(DB_NAME)
    bot = Bot(TOKEN, db, TOKENS_gpt=TOKENS_gpt)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.dp.start_polling())
    finally:
        loop.run_until_complete(bot.dp.bot.session.close())
        db.close()
        loop.close()


if __name__ == '__main__':
    main()
