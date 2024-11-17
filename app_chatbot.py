from fastapi import FastAPI, Request
from functions import BotManager
import os


app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    
    BOT_TOKEN = os.environ.get("CHATBOT_TOKEN")
    API_KEY = os.environ.get("GPT_API_KEY")
    bot = BotManager(BOT_TOKEN, API_KEY)
    data = await request.json()
    await bot.run(data)
    return {"status": "ok"}
