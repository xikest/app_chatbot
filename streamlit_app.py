import streamlit as st
from audiorecorder import audiorecorder
import openai
from datetime import datetime
import numpy as np
import os
from gtts import gTTS
import base64


def speech2text(audio):
    # 파일 저장
    filename = 'input.mp3'
    wav_file = open(filename, "wb")
    wav_file.write(audio.tobytes())
    wav_file.close()

    # open voice
    audio_file = open(filename, "rb")
    # get text by Whisper
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    audio_file.close()
    # del file
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


def main():
    # 기본 설정
    st.set_page_config(
        page_title="Voice man",
        layout="wide")

    flag_start = False
    query_trx = "\n Please translate it into Korean"
    # session state initialize
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system",
                                         "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = []

    # if "check_audio_uploaded" not in st.session_state:
    #     st.session_state["check_audio_uploaded"] = []

    # upload voice file
    # uploaded_audio = st.file_uploader("Upload an audio file (MP3 or WAV)", type=["mp3", "wav"])

    # title
    st.header("Your Voice App")
    # segment
    st.markdown("---")

    # basic descr
    with st.expander("APP environment description", expanded=True):
        st.write(
            """     
            - STT(Speech-To-Text): OpenAI - Whisper AI 
            - TTS(Text-To-Speech): Google - Translate TTS
            - Engine: OpenAI - GPT 
            """
        )

        st.markdown("")



    # side bar
    with st.sidebar:
        openai.api_key = st.text_input(label="OPENAI API Key", placeholder="Enter Your API Key", type="password")
        model = st.radio(label="GPT Model", options=["gpt-3.5-turbo", "gpt-4"])
        mode = st.radio(label="Mode", options=["Translate", "Ask a Question"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Question")

        audio = audiorecorder("Click to record", "Recording...")

        if len(audio) > 0 and not np.array_equal(audio, st.session_state["check_audio"]):
            st.audio(audio.tobytes())
            question = speech2text(audio)
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            if mode == "Translate":
                question += query_trx
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]
            st.session_state["check_audio"] = audio
            flag_start = True

    with col2:

        st.subheader("Answer")
        if flag_start:
            response = ask_gpt(st.session_state["messages"], model)
            response -= query_trx
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]

            # ready to chat
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            # show chat
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(
                        f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                        unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(
                        f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                        unsafe_allow_html=True)
                    st.write("")

            # speak
            # text2speech(response)


if __name__ == "__main__":
    main()