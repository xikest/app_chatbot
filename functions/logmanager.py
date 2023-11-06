import os

class LogManager:
    def __init__(self):
        self.messages_prompt = []
        self.log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.log_dir, exist_ok=True)

    def add_message(self, role, content):
        self.messages_prompt.append({"role": role, "content": content})

    def save_log(self, log_file):
        log_path = os.path.join(self.log_dir, log_file)
        with open(log_path, "w") as file:
            for message in self.messages_prompt:
                file.write(f"{message['role']}: {message['content']}\n")

    def load_log(self, log_file):
        log_path = os.path.join(self.log_dir, log_file)
        try:
            self.messages_prompt = []
            with open(log_path, "r") as file:
                for line in file:
                    parts = line.strip().split(": ")
                    if len(parts) == 2:
                        role, content = parts
                        self.add_message(role, content)
        except FileNotFoundError:
            self.add_message("assistant", "You are a thoughtful assistant. Respond to all input in 20 words and answer in korea")
            self.save_log(log_file)