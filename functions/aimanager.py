import openai

class AIManager:
    def __init__(self, api_key):
        self.API_KEY = api_key
        openai.api_key = self.API_KEY
        self.messages_prompt = []

    def add_message_to_prompt(self, role, content):
        self.messages_prompt.append({"role": role, "content": content})

    def get_text_from_gpt(self, prompt):
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
        system_message = response["choices"][0]["message"]
        answer = system_message["content"]
        return answer
    def getImageURLFromDALLE(self, user_input):
        response = openai.Image.create(prompt=user_input,n=1,size="512x512")
        image_url = response['data'][0]['url']
        return image_url