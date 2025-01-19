from fastapi import FastAPI, Request
from functions import BotManager
import os
import subprocess
import uvicorn


app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    
    BOT_TOKEN = os.environ.get("CHATBOT_TOKEN")
    API_KEY = os.environ.get("GPT_API_KEY")
    bot = BotManager(BOT_TOKEN, API_KEY)
    data = await request.json()
    await bot.run(data)
    return {"status": "ok"}


@app.post("/stream")
async def stream(request: Request):
    # Streamlit 실행
    streamlit_port = 8501
    # streamlit_process = subprocess.Popen(
    #     ["streamlit", "run", "app_streamlit.py", "--server.port", str(streamlit_port)],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )

    # 실행된 Streamlit 페이지 URL 반환
    streamlit_url = f"http://localhost:{streamlit_port}"
    return {"status": "ok", "streamlit_url": streamlit_url}
    
    
if __name__ == "__main__":
    uvicorn.run("app_chatbot:app", host="0.0.0.0", port=8888)
    