from datetime import datetime
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from functions.aimanager import AIManager
from functions.logmanager import LogManager
from functions.yt_downloader import YTDownloader
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import ContextTypes


class BotManager:
    OPEARTING = False
    YT_TYPE='mp3'
    def __init__(self, token, api_key, firestore_auth='web-driver.json'):
        self.app = Application.builder().token(token).build()
        self.aim = AIManager(api_key, gpt_model= "gemini-2.0-flash-exp")
        self.log = LogManager(json_path=firestore_auth)
        self.ytd = YTDownloader
        

    async def run(self, data):
        update = Update.de_json(data, self.app.bot)
        if not self.app.handlers:
            self.add_handlers()  # 핸들러 추가
        await self.app.initialize()
        await self.app.process_update(update)
    
    def add_handlers(self):
        
        self.app.add_handler(CommandHandler("new", self.newbot_command))
        # self.app.add_handler(CommandHandler("img", self.img_command))
        # self.app.add_handler(MessageHandler(filters.Document.ALL, self.save_file))
        self.app.add_handler(CommandHandler("mp3", self.yt_switch_mp3_command))
        self.app.add_handler(CommandHandler("mp4", self.yt_switch_mp4_command))
        # yt_pattern = r'https?://(?:www\.)?(?:youtu\.be|youtube\.com)/[\w\-?&=]+'
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND), self.chatgpt)
        # self.app.add_handler(MessageHandler(filters.TEXT & filters.Regex(yt_pattern), self.yt_download_command))


    async def chatgpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            await update.message.reply_text(f"Please wait a moment.")
            pass

        
    async def newbot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.chat_id
        await self.log.reset_chat_log(user_id)
        await self.app.bot.send_message(chat_id=user_id, text="new bot start")
        
        
    async def img_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

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
            await update.message.reply_text(f"The file has been saved.: {file_path}")
            
    async def yt_switch_mp3_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data['YT_TYPE'] = 'mp3'
        await update.message.reply_text("File type switched to MP3.")
        
    async def yt_switch_mp4_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data['YT_TYPE'] = 'mp4'
        await update.message.reply_text("File type switched to MP4.")

    # async def yt_download_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #     try:
    #         YT_TYPE = context.user_data.get('YT_TYPE', 'mp3')  # 기본값은 'mp3'
    #         file_type = f".{YT_TYPE}"

    #         user_message = update.message.text
    #         url = user_message.strip()  # URL 앞뒤 공백 제거
    #         if 'youtu.be' not in url and 'youtube.com' not in url:
    #             await update.message.reply_text("Invalid YouTube URL. Please provide a valid YouTube link.")
    #             return
            
    #         await update.message.reply_text(f"Downloading {file_type[1:].upper()} from: {url}. This might take some time...")

    #         asyncio.create_task(self.handle_download_task(update, context, url, file_type))
    #     except Exception as e:
    #         await update.message.reply_text(f"An error occurred: {e}")


    # async def handle_download_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, file_type: str):
    #     """실제 다운로드 및 전송 작업을 처리하는 함수"""
    #     try:
    #         file_name = self.ytd.download_video(url, file_type)
            
    #         if file_name:
    #             with open(file_name, "rb") as file:
    #                 await context.bot.send_document(chat_id=update.message.chat_id, document=file)
    #             os.remove(file_name)
    #         else:
    #             await update.message.reply_text("Download failed. Please check the URL.")
    #     except Exception as e:
    #         await update.message.reply_text(f"An error occurred during the download: {e}")

            
    # async def mp4_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    #     try:
    #         # 사용자 입력으로부터 URL 가져오기
    #         url = " ".join(context.args)
    #         if not url:
    #             await update.message.reply_text("Please enter the YouTube URL! Usage: /mp4 ")
    #             return

    #         # 다운로드 시작
    #         # await update.message.reply_text("MP4 다운로드 중입니다. 잠시만 기다려주세요...")
    #         file_name = self.ytd.download_video(url, self.ytd.video_options())
    #         file_name = file_name.replace(".webm", ".mp4")
    #         # 파일 전송
    #         if file_name:
    #             await context.bot.send_document(chat_id=update.message.chat_id, document=open(file_name, "rb"))
    #             os.remove(file_name) # 파일 삭제
    #         else:
    #             await update.message.reply_text("Download failed. Please check the URL.")

    #     except Exception as e:
    #         await update.message.reply_text(f"An error occurred {e}")



