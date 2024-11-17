from datetime import datetime
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from functions.aimanager import AIManager
from functions.logmanager import LogManager
import os

class BotManager:
    OPEARTING = False
    def __init__(self, token, api_key, firestore_auth='web-driver.json'):
        self.app = Application.builder().token(token).build()
        self.aim = AIManager(api_key, gpt_model= 'gpt-4o-mini')
        self.log = LogManager(json_path=firestore_auth)
        

    async def run(self, data):
        update = Update.de_json(data, self.app.bot)
        if not self.app.handlers:
            self.add_handlers()  # 핸들러 추가
        await self.app.initialize()
        await self.app.process_update(update)
    
    def add_handlers(self):
        self.app.add_handler(CommandHandler("hey", self.start_command))
        self.app.add_handler(CommandHandler("bye", self.close_command))
        self.app.add_handler(CommandHandler("new", self.newbot_command))
        self.app.add_handler(CommandHandler("img", self.img_command))
        # self.app.add_handler(MessageHandler(filters.Document.ALL, self.save_file))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chatgpt))


    async def chatgpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global OPEARTING
        if OPEARTING:
            """Echo the user message."""
            user_message = update.message.text
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            user_id = update.message.chat_id
            try:
                previous_chats = await self.log.get_previous_chats(user_id)
                
                prompt = {"role": "user", "content": user_message}
                bot_response = self.aim.get_text_from_gpt(prompt, previous_chats)
                await self.log.save_chat_log(user_id, user_message, bot_response, current_time)
                await update.message.reply_text(bot_response)
            except Exception as e:
                print(e)
                await update.message.reply_text(f"잠시만 기다려 주세요.")
                pass

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global OPEARTING  # 전역 변수 사용
        OPEARTING = True
        user_id = update.message.chat_id
        await self.app.bot.send_message(chat_id=user_id, text="I'm here for you")
        
    async def close_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global OPEARTING  # 전역 변수 사용
        OPEARTING = False
        user_id = update.message.chat_id
        await self.app.bot.send_message(chat_id=user_id, text="good bye~")
        
    async def newbot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.chat_id
        await self.log.reset_chat_log(user_id)
        await self.app.bot.send_message(chat_id=user_id, text="new bot start")

    async def img_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global OPEARTING
        if OPEARTING:
            user_message = update.message.text
            user_message = user_message.replace("/img", "")
            bot_response = self.aim.getImageURLFromDALLE(user_message)
            await update.message.reply_text(f"[{user_message}]에 대해 그려봤습니다.")
            await update.message.reply_photo(bot_response)
            
            
    async def save_file(self, update: Update, context):
        UPLOAD_DIR = "uploaded_files"
        if update.message.document:
            file_id = update.message.document.file_id
            file_name = update.message.document.file_name
            file = await context.bot.get_file(file_id) 
            
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(UPLOAD_DIR, file_name)
            
            await file.download_to_drive(file_path)
            await update.message.reply_text(f"파일이 저장되었습니다: {file_path}")
