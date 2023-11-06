from function_ai import AIManager
from function_telegram import TelegramBot, BotManager
import os

BOT_TOKEN = os.environ.get("telegram_bot_token")
API_KEY = os.environ.get("openai_api_key")

async def chatBot(telegramrequest):
    result = telegramrequest
    if not result['message']['from']['is_bot']:
        chat_id = str(result['message']['chat']['id'])
        msg_id = str(int(result['message']['message_id']))
        user_message = result['message']['text']
        bot_manager = BotManager()
        BOT_MODE, user_message = bot_manager.set_bot_mode(user_message)
        print(f"{BOT_MODE}, {user_message}")
        if user_message is not None:
            bot = TelegramBot(BOT_TOKEN)
            aim = AIManager(API_KEY)
            if BOT_MODE == 'img':
                bot_response = aim.get_image_url_from_dalle(user_message)
                await bot.send_photo(chat_id, bot_response, msg_id)
            else:
                bot_response = aim.get_text_from_gpt(user_message)
                await bot.send_message(chat_id, bot_response, msg_id)
        else:
            pass
    return None


