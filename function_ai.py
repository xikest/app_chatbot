import asyncio
import os
import openai

class AIManager:
    def __init__(self, api_key):
        self.API_KEY = api_key
        openai.api_key = self.API_KEY

    def get_text_from_gpt(self, messages):
        messages_prompt = [{"role": "system", "content": 'You are a thoughtful assistant. Respond to all input in 25 words and answer in korea'}]
        messages_prompt += [{"role": "system", "content": messages}]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_prompt)
        system_message = response["choices"][0]["message"]
        return system_message["content"]

    def get_image_url_from_dalle(self, messages):
        messages_prompt = [{"role": "system", "content": 'You are a highly renowned artist. Responding in 25 words, translating all input into English.'}]
        messages_prompt += [{"role": "system", "content": messages}]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_prompt)
        system_message = response["choices"][0]["message"]
        messages = system_message["content"]
        response = openai.Image.create(prompt=messages, n=1, size="512x512")
        image_url = response['data'][0]['url']
        return image_url