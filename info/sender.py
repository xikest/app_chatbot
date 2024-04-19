import os

class Sender:
    def __init__(self):
        self.bot_token = os.environ.get("CHAT_BOT_TOKEN")
        self.gpt_key = os.environ.get("GPT_KEY")

    def get_token(self)->str:
        return self.bot_token

    def get_gpt_key(self)->str:
        return self.gpt_key