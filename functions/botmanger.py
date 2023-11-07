import logging
import time
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
        print(f"token: {token}")
        print(f"api_key: {api_key}")
        self.token = token
        self.api_key = api_key
        self.app = Application.builder().token(self.token).build()
        self.aim = AIManager(self.api_key)
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
                prompt_first= self.log_manager.messages_prompt.pop(0)
                prompt_recent = self.log_manager.messages_prompt[-5:]  # 최근 5개만
                prompt = [prompt_first] + prompt_recent
                # print(f"prompt: {prompt}")
                print(f"user: {prompt[-1].get('content')}")
                start_time = time.time()  # 함수 시작 시간 기록
                bot_response = self.aim.get_text_from_gpt(prompt)
                end_time = time.time()  # 함수 종료 시간 기록
                execution_time = end_time - start_time  # 실행 시간 계산
                bot_response = f"{bot_response}|({round(execution_time,1)}s)"
                print(f"bot: {bot_response}")
                self.log_manager.add_message("assistant", bot_response)
                self.log_manager.save_log(self.bot_log)
            else:
                bot_response = user_message
            await update.message.reply_text(bot_response)

        except TimeoutError as e:
            await self.handle_error(e, type='time out', update=update)

            user_id = update.message.chat_id
            await self.newbot(user_id)
            pass

        except Exception as e:
            await self.handle_error(e, type='normal', update=update)



    async def img_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_message = update.message.text
        aim = AIManager(self.api_key)
        bot_response = aim.getImageURLFromDALLE(user_message)
        await update.message.reply_photo(bot_response)

    async def newbot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.chat_id
        await self.newbot(user_id)

    async def newbot(self, user_id) -> None:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        self.bot_log =  f"log_{user_id}_{current_time}"
        self.log_manager = LogManager()
        self.log_manager.load_log(self.bot_log)
        return None

    async def handle_error(self, error, type, update) -> None:
        error_message = f"{type} error: {error}"
        print(error_message)
        os.makedirs("err", exist_ok=True)
        with open(f"err/{type} error.txt", "w") as error_file:
            error_file.write(error_message)
        await update.message.reply_text(error_message)
        return None

