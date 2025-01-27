from datetime import datetime
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from functions.aimanager import AIManager
from functions.logmanager import LogManager
import requests
import urllib.parse
import os
import re
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import ContextTypes


class BotManager:
    OPEARTING = False
    
    
    def __init__(self, token, api_key, firestore_auth='web-driver.json'):
        self.app = Application.builder().token(token).build()
        self.aim = AIManager(api_key, gpt_model= "gemini-2.0-flash-exp")
        self.log = LogManager(json_path=firestore_auth)
        self.ydown_apiurl=os.getenv("ydown_url")

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
        # self.app.add_handler(CommandHandler("mp3", self.yt_switch_mp3_command))
        yt_pattern = r'https?://(?:www\.)?(?:youtu\.be|youtube\.com)/[\w\-?&=]+'
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex(yt_pattern), self.chatgpt))
        self.app.add_handler(MessageHandler(filters.TEXT & filters.Regex(yt_pattern), self.yt_download_command))


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
            

    async def yt_download_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        def extract_title_from_url(url):
            # URL에서 파일 이름만 추출
            file_name = url.split('/')[-1]  # 마지막 부분을 추출
            # 퍼센트 인코딩된 부분을 디코딩
            decoded_name = urllib.parse.unquote(file_name)
            # 파일 이름에서 확장자 제거
            title = decoded_name.rsplit('.', 1)[0]
            return title
        
        try:
            # URL과 파일 타입 처리
            url = update.message.text.strip()
            
            # yt_type = context.user_data.get('yt_type', 'mp3')
            yt_type = 'mp3'
            data = {
                "url": f"{url}",  
                "file_type": f"{yt_type}"  
            }
            response = requests.post(self.ydown_apiurl, json=data)
            if response.status_code == 200:
                url = response.json()['file_name']
                special_chars = r'[\[\]()_`*~>#+\-.!]'
                url = re.sub(special_chars, lambda match: f'\\{match.group(0)}', url)
                title = extract_title_from_url(url)
                await update.message.reply_text(
                    f"[{title}|{yt_type}]({url})",
                    parse_mode="MarkdownV2")
            else:
                await update.message.reply_text(f"파일 다운로드 실패: {response.status_code}, {response.json()['detail']}")
                
        except Exception as e:
                    await update.message.reply_text(f"파일 다운로드 중 오류가 발생했습니다. 나중에 다시 시도해주세요.{e}")

    # async def yt_switch_mp3_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #     context.user_data['yt_type'] = 'mp3'
    #     await update.message.reply_text("File type switched to MP3.")
        
    # async def yt_switch_mp4_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #     context.user_data['yt_type'] = 'mp4'
        # await update.message.reply_text(f"File type switched to MP4.")
