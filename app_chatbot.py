from functions.botmanger import BotManager
from info.sender import Sender


BOT_TOKEN = Sender().get_token()
API_KEY = Sender().get_gpt_key()


if __name__ == "__main__":
    bot_manager = BotManager(BOT_TOKEN, API_KEY)
    bot_manager.run()
