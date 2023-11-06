import openai
import os






def textResponseFormat(bot_response):
    response = {'version': '2.0', 'template':{
        'output':[{"simpleText": {"text": bot_response}}], 'quickReplies':[]}}
    return response

def imageResponseFormat(bot_response, prompt):
    output_text = prompt + "이미지"
    response = {'version':'2.0', 'template':{
    'outputs':[{'simpleImage': {'imageUrl': bot_response, "altText": output_text}}], 'quickReplies':[]}}
    return  response


def timeover():
    response = {"version":"2.0", "template":{
        "outputs":[
            {
                "simpleText":{
                    "text":"오래 걸릴 것 같습니다. 잠시 후에 다시 불러주세요"
                }
            }
        ],
        "quickReplies":[
            {
                "action":"message",
                "label":"다 했어?",
                "messageText":"다 했어?"
            }
        ]
    }}
    return response



def dbReset(filename):
    with open(filename, 'w') as f:
        f.write("")


