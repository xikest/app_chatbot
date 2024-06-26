import logging
import time
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from functions.aimanager import AIManager
from functions.logmanager import LogManager
import os

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self, token, api_key):
        self.token = token
        self.api_key = api_key
        self.app = Application.builder().token(self.token).build()
        self.aim = None
        self.log_manager = None
        self.bot_log = None

    def run(self):
        self.add_handlers()
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    def add_handlers(self):
        self.app.add_handler(CommandHandler("hey", self.newbot_command))
        self.app.add_handler(CommandHandler("img", self.img_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chatgpt))

    async def chatgpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        user_message = update.message.text

        try:
            if self.bot_log:
                self.log_manager.add_message("user", user_message)
                prompt_first= self.log_manager.messages_prompt[0]
                prompt_recent = self.log_manager.messages_prompt[1:][-10:]  # 최근 5개만
                prompt = [prompt_first] + prompt_recent
                print(f"prompt: {prompt}")
                print(f"user: {prompt[-1].get('content')}")
                start_time = time.time()  # 함수 시작 시간 기록
                bot_response = self.aim.get_text_from_gpt(prompt)
                end_time = time.time()  # 함수 종료 시간 기록
                execution_time = end_time - start_time  # 실행 시간 계산
                print(f"bot: {bot_response}|({round(execution_time,1)}s)")
                self.log_manager.add_message("assistant", bot_response)
                self.log_manager.save_log(self.bot_log)
            else:
                bot_response = user_message
            await update.message.reply_text(bot_response)

        except Exception as e:
            user_id = update.message.chat_id
            await self.newbot(user_id)
            await self.handle_error(e, type='normal', update=update)
            sleeptime = 10
            await update.message.reply_text(f"{sleeptime}초만 기다려 주세요.")
            await asyncio.sleep(sleeptime)
            await update.message.reply_text(f"다시 이야기를 이어가죠.")
            pass

    async def img_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_message = update.message.text
        user_message = user_message.replace("/img", "")
        bot_response = self.aim.getImageURLFromDALLE(user_message)
        await update.message.reply_text(f"[{user_message}]에 대해 그려봤습니다.")
        await update.message.reply_photo(bot_response)


    async def newbot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.chat_id
        await self.newbot(user_id)

    async def newbot(self, user_id) -> None:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        self.bot_log =  f"log_{user_id}_{current_time}"
        self.log_manager = LogManager()
        self.log_manager.load_log(self.bot_log)
        self.aim = AIManager(self.api_key)
        return None

    async def handle_error(self, error, type, update) -> None:
        error_message = f"{type} error: {error}"
        print(error_message)
        dir_err = "error"
        os.makedirs(dir_err, exist_ok=True)
        with open(f"{dir_err}/{type}_error.txt", "w") as error_file:
            error_file.write(error_message)
        await update.message.reply_text(error_message)
        return None

