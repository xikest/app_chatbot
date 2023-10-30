import streamlit as st
import openai
import os
from gtts import gTTS
import base64
from audiorecorder import AudioSegment

def speech2text(audio):
    # 파일 저장
    filename = 'input.mp3'
    wav_file = open(filename, "wb")
    wav_file.write(audio.tobytes())
    wav_file.close()

    # 음원 파일 열기
    audio_file = open(filename, "rb")
    # Whisper 모델을 활용해 텍스트 얻기
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    audio_file.close()
    # 파일 삭제
    os.remove(filename)
    return transcript["text"]


def ask_gpt(prompt, model):
    response = openai.ChatCompletion.create(model=model,
                                            messages=prompt)
    system_message = response["choices"][0]["message"]
    return system_message["content"]


def text2speech(response):
    # gTTS 를 활용하여 음성 파일 생성
    filename = "output.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)

    # 음원 파일 자동 재성
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True, )
    # 파일 삭제
    os.remove(filename)
