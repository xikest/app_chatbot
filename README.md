# AI Chatbot

This project is an AI-powered chatbot that uses OpenAI's GPT-3.5 Turbo model and DALL·E to provide natural language understanding and image generation capabilities. 
It is designed to respond to text input from users and generate text-based responses as well as create images based on prompts.

## Features
- **AI Chatbot**: The chatbot is powered by OpenAI's GPT-3.5 Turbo model and can engage in natural language conversations with users.
- **Image Generation**: The project also includes a feature that generates images using DALL·E based on user prompts.
- **Logging**: The application logs user interactions and bot responses, allowing users to track and review their conversations.

## Getting Started
To get started with this project, follow these steps:
#### 1. Clone the repository to your local machine:
```bash
git clone https://github.com/your-username/ai-chatbot-image-generator.git
```
#### 2. Install the required dependencies. You can use `pip` to install the necessary libraries:
```bash
pip install -r requirements.txt
```
#### 3. Obtain API keys:
   - Create an OpenAI API key from the OpenAI platform.
   - Create a Telegram bot and obtain the API token from the BotFather on Telegram.
#### 4. Set environment variables for your API keys. You can export them as follows:
  ```bash
  export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
  export OPENAI_API_KEY="your-openai-api-key"
  ```
#### 5. Run the application:
  ```bash
  python app_chatbot.py
  ```
#### 6. You can interact with the AI chatbot on Telegram by sending messages to your bot.

## Usage
  - To start a new conversation with the chatbot, send the `/new` command to the bot. It will create a new conversation log for you.
  - To generate images using DALL·E, send the `/img` command followed by your image prompt.
  - You can engage in natural language conversations by sending text messages to the bot. The chatbot will respond based on the context of the conversation.

## Logs
User interactions and bot responses are logged and stored in the `logs` directory. You can review your conversations by accessing the log files.

## Acknowledgments
This project was built with the help of the following technologies and libraries:
  - OpenAI for the GPT-3.5 Turbo model and DALL·E.
  - Python Telegram Bot for the Telegram bot integration.
