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
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import ContextTypes


class BotManager:
    OPEARTING = False
    
    
    def __init__(self, token, api_key, firestore_auth='web-driver.json'):
        self.ydown_url=os.getenv("ydown_url")
        self.ymp3_url=os.getenv("ymp3_url")
        self.storage_name = os.getenv("chat_bot_storage_name")
        gpt_model= os.getenv("GPT_MODEL")
        self.app = Application.builder().token(token).build()
        self.aim = AIManager(api_key, gpt_model= gpt_model)
        self.log = LogManager(json_path=firestore_auth)
        
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
        self.app.add_handler(CommandHandler("mp3", self.get_mp3_list_command))
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
            
    async def get_mp3_list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        

        url = self.ymp3_url  
        params = {"storage_name": self.storage_name}
        response = requests.post(url, params=params)
        if response.status_code == 200:
            response_json = response.json()
            link_dict = response_json['mp3list']
            for title, link in link_dict.items():
                title = title.rsplit('.', 1)[0]
                title = self.escape_markdown(title)
                link = self.escape_markdown(link)
                await update.message.reply_text(
                                    f"\\#mp3\n[{title}]({link})",
                                    parse_mode="MarkdownV2"
                                )
            
        else:
             await update.message.reply_text(f"response fail, status code: {response.status_code}, error message: {response.text}")

    
    async def yt_download_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            # URL과 파일 타입 처리
            url = update.message.text.strip()
            data = {
                "url": f"{url}",  
                "file_type": "mp3",
                "storage_name": self.storage_name
            }

            # 비동기로 POST 요청 전송 (타임아웃 무제한)
            timeout = aiohttp.ClientTimeout(total=None)  # 타임아웃 해제
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.ydown_url, json=data) as response:
                    if response.status == 200:
                        response_json = await response.json()  # JSON 응답 비동기로 처리
                        url = self.escape_markdown(response_json['url'])
                        label = response_json['label']
                        label = label.rsplit('.', 1)[0]
                        label = self.escape_markdown(label)
                        await update.message.reply_text(
                            f"\\#mp3\n[{label}]({url})",
                            parse_mode="MarkdownV2"
                        )
                    else:
                        error_detail = await response.json()
                        await update.message.reply_text(
                            f"파일 다운로드 실패: {response.status}, {error_detail.get('detail', '알 수 없는 오류')}"
                        )

        except Exception as e:
            await update.message.reply_text(
                f"파일 다운로드 중 오류가 발생했습니다. 나중에 다시 시도해주세요.\n오류 내용: {e}"
            )
    
    
    def escape_markdown(self, text: str) -> str:
        special_chars = r'([_*\[\]()~`>#+\-=|{}.!\\])'
        """MarkdownV2에서 특수 문자를 escape"""
        return re.sub(special_chars, r'\\\1', text)
    