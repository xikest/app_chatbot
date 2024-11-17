from google.cloud import firestore
from google.oauth2 import service_account
import logging

class LogManager:
    def __init__(self, json_path='web-driver.json'):
        credentials = service_account.Credentials.from_service_account_file(json_path)
        logging.info("Credentials loaded successfully.")
        self.db = firestore.Client(credentials=credentials)
        pass
    
    async def get_previous_chats(self, user_id):
        chat_ref = self.db.collection("chat_logs").document(str(user_id)).collection("messages")
        logs = chat_ref.order_by("timestamp").stream()
        chat_history = []
        for log in logs:
            chat_history.append({
                "role": "user",
                "content": log.to_dict()["user_message"]})
            chat_history.append({
                "role": "assistant",
                "content": log.to_dict()["bot_response"] })
        return chat_history


    async def save_chat_log(self, user_id, user_message, bot_response, timestamp):
        chat_ref = self.db.collection("chat_logs").document(str(user_id)).collection("messages")
        chat_ref.add({
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": timestamp})

    async def reset_chat_log(self, user_id):
        chat_ref = self.db.collection("chat_logs").document(str(user_id)).collection("messages")
        logs = chat_ref.stream()
        for log in logs:
            log.reference.delete()
        logging.info(f"User {user_id}'s chat log has been reset.")
