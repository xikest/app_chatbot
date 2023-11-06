from functions.botmanger import BotManager
import os


BOT_TOKEN = os.environ.get("telegram_bot_token")
API_KEY = os.environ.get("openai_api_key")



if __name__ == "__main__":
    bot_manager = BotManager(BOT_TOKEN, API_KEY)
    bot_manager.run()
