import telegram

class TelegramBot:
    def __init__(self, bot_token):
        self.BOT_TOKEN = bot_token
        self.bot = telegram.Bot(self.BOT_TOKEN)
    async def send_message(self, chat_id, text, msg_id):
        data = {
            'chat_id': chat_id,
            'text': text,
            'reply_to_message_id': msg_id
        }
        print(f"bot send message: {data.get('text')}")
        await self.bot.send_message(chat_id=data.get("chat_id"), text=data.get("text"))
        return None

    async def send_photo(self, chat_id, image_url, msg_id):
        data = {
            'chat_id': chat_id,
            'photo': image_url,
            'reply_to_message_id': msg_id
        }

        await self.bot.send_photo(chat_id=data.get("chat_id"), photo=data.get("photo"))
        return None

class BotManager:
    def __init__(self):
        self.BOT_MODE = None
        pass

    def set_bot_mode(self, prompt):
        if prompt == "/img":
            self.BOT_MODE = 'img'
            prompt = None
            print(f"mode switch: {self.BOT_MODE}")
            self.save_bot_mode(self.BOT_MODE)
        elif prompt == "/chat":
            self.BOT_MODE = 'chat'
            prompt = None
            print(f"mode switch: {self.BOT_MODE}")
            self.save_bot_mode(self.BOT_MODE)
        else:
            self.BOT_MODE = self.load_bot_mode()
            prompt = prompt

        print(f"current bot mode: {self.BOT_MODE}")
        return self.BOT_MODE, prompt

    @staticmethod
    def save_bot_mode(mode):
        with open('bot_mode.txt', 'w') as file:
            file.write(mode)

    @staticmethod
    def load_bot_mode():
        try:
            with open('bot_mode.txt', 'r') as file:
                return file.read()
        except FileNotFoundError:
            return 'chat'  # Default value if the file doesn't exist
