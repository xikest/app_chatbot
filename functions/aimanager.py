from openai import OpenAI

class AIManager:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.messages_prompt = []

    def add_message_to_prompt(self, role, content):
        self.messages_prompt.append({"role": role, "content": content})

    def get_text_from_gpt(self, prompt):
        response = self.client.chat.completions.create(model="gpt-3.5-turbo", messages=prompt, timeout=30)
        answer = response.choices[0].message.content
        return answer
    def getImageURLFromDALLE(self, user_input):
        response = self.client.images.generate(prompt=user_input,n=1,size="512x512")
        image_url = response.data[0].url
        return image_url

