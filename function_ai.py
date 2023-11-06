from chat_kakao import *

# OpenAI API KEY

API_KEY = os.environ.get("openai_api_key")
openai.api_key = API_KEY

def getTextFromGPT(prompt):
    messages_prompt = [{"role": "system", "content": 'You are a thoughtful assistant. Respond to all input in 25 words and answer in korea'}]
    messages_prompt += [{"role": "system", "content": prompt}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_prompt)
    message = response["choices"][0]["message"]["content"]
    return message

def getImageURLFromDALLE(prompt):
    response = openai.Image.create(prompt=prompt,n=1,size="512x512")
    image_url = response['data'][0]['url']
    return image_url

def responseOpenAI(request, response_queue, filename):
    if '다 했어?' in request["userRequest"]["utterance"]:
        # 텍스트 파일 열기
        with open(filename) as f:
            last_update = f.read()
        # 텍스트 파일 내 저장된 정보가 있을 경우
        if len(last_update.split()) > 1:
            kind, bot_res, prompt = last_update.split()[0], last_update.split()[1], last_update.split()[2]
            if kind == "img":
                response_queue.put(imageResponseFormat(bot_res, prompt))
            else:
                response_queue.put(textResponseFormat(bot_res))
            dbReset(filename)

    # 이미지 생성을 요청한 경우
    elif '/img' in request["userRequest"]["utterance"]:
        dbReset(filename)
        prompt = request["userRequest"]["utterance"].replace("/img", "")
        bot_res = getImageURLFromDALLE(prompt)
        response_queue.put(imageResponseFormat(bot_res, prompt))
        save_log = "img" + " " + str(bot_res) + " " + str(prompt)
        with open(filename, 'w') as f:
            f.write(save_log)

    # ChatGPT 답변을 요청한 경우
    elif '/ask' in request["userRequest"]["utterance"]:
        dbReset(filename)
        prompt = request["userRequest"]["utterance"].replace("/ask", "")
        bot_res = getTextFromGPT(prompt)
        response_queue.put(textResponseFormat(bot_res))

        save_log = "ask" + " " + str(bot_res) + " " + str(prompt)
        with open(filename, 'w') as f:
            f.write(save_log)

    # 아무 답변 요청이 없는 채팅일 경우
    else:
        # 기본 response 값
        base_response = {'version': '2.0', 'template': {'outputs': [], 'quickReplies': []}}
        response_queue.put(base_response)