from openai import OpenAI

class AIManager:
    def __init__(self, api_key, gpt_model='gemini-2.0-flash-exp'):
        self.client = OpenAI(api_key=api_key,
                             base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        self.messages_prompt = []
        self.gpt_model=gpt_model

    def add_message_to_prompt(self, role, content):
        self.messages_prompt.append({"role": role, "content": content})

    def get_text_from_gpt(self, prompt, previous_chats=None):
        
        self.add_message_to_prompt("assistant", "Answer in Korean. Do not use any markdown syntax.")
        if previous_chats is not None:
            self.messages_prompt.extend(previous_chats)
            
        self.messages_prompt.append(prompt)
        # print(self.messages_prompt)
        response = self.client.chat.completions.create(model=self.gpt_model, messages=self.messages_prompt, timeout=60)
        answer = response.choices[0].message.content
        return answer

    def getImageURLFromDALLE(self, user_input):
        response = self.client.images.generate(model="gemini-2.0-flash-exp", prompt=user_input,n=1, size="1024x1024", quality="standard")
        image_url = response.data[0].url
        return image_url
