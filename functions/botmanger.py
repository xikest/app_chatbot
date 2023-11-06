import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from functions.aimanager import AIManager
from functions.logmanager import LogManager

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class BotManager:

    def __init__(self, token, api_key):
        self.token = token
        self.api_key = api_key
        self.app = Application.builder().token(self.token).build()
        self.log_manager = None
        self.logfile:str = ""

    def run(self):
        self.add_handlers()
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    def add_handlers(self):
        self.app.add_handler(CommandHandler("new", self.newbot_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chatgpt))

    async def chatgpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        user_message = update.message.text
        user_id = update.message.chat_id
        if not self.log_manager:
            self.logfile = await self.newbot(user_id)
            self.log_manager = LogManager()
        self.log_manager.load_log(self.logfile)
        self.log_manager.add_message("user", user_message)
        prompt = self.log_manager.messages_prompt
        aim = AIManager(self.api_key)
        bot_response = aim.get_text_from_gpt(prompt)
        # print(f"bot_response, {bot_response}")
        self.log_manager.add_message("assistant", bot_response)
        self.log_manager.save_log(self.logfile)
        await update.message.reply_text(bot_response)

    async def newbot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.chat_id
        self.logfile = await self.newbot(user_id)
        # print(f"new:{self.logfile}")

    async def newbot(self, user_id) -> str:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"conversation_{user_id}_{current_time}.log"