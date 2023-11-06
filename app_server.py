from fastapi import Request, FastAPI
from function_bot import chatBot

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "TelegramChatbot"}

@app.post("/chat/")
async def chat(request: Request):
    telegramrequest = await request.json()
    await chatBot(telegramrequest)
    return {"message": "TelegramChatbot/chat"}