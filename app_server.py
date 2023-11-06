from fastapi import Request, FastAPI
import openai
import asyncio
import time
import queue as q
import os
from function_chat import mainChat

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "kakaoTest"}

@app.post("/chat/")
async def chat(request: Request):
    kakaorequest = await request.json()
    return mainChat(kakaorequest)

