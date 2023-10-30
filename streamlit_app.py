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

##### 메인 함수 #####
def main():
    # 기본 설정
    st.set_page_config(
        page_title="Your Voice",
        layout="wide")

    flag_start = False

    # session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system",
                                         "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = []

    # 제목
    st.header("Your Voice App")
    # 구분선
    st.markdown("---")

    # 기본 설명
    with st.expander("What is this APP", expanded=True):
        st.write(
            """     
            - STT(Speech-To-Text): OpenAI의 Whisper AI 
            - TTS(Text-To-Speech):Google Translate TTS
            - Engine: OpenAI의 GPT 모델. 
            """
        )

        st.markdown("")

    # 사이드바 생성
    with st.sidebar:

        # Open AI API 키 입력받기
        openai.api_key = st.text_input(label="OPENAI API Key", placeholder="Enter Your API Key", value="",
                                       type="password")

        st.markdown("---")

        # GPT 모델을 선택하기 위한 라디오 버튼 생성
        model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        mode = st.radio(label="Mode", options=["질문하기", "번역하기"])

        st.markdown("---")
        # 리셋 버튼 생성
        if st.button(label="초기화"):
            # 리셋 코드
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system",
                                             "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")
        # 음성 녹음 아이콘
        # if 오디오 파일을 불러온다면
        # audio = open("output.mp3", "rb")
        audio = audiorecorder("click to record", "recording...")
        if len(audio) > 0 and not np.array_equal(audio, st.session_state["check_audio"]):
            # 음성 재생
            st.audio(audio.tobytes())
            # 음원 파일에서 텍스트 추출
            question = speech2text(audio)

            # 채팅을 시각화하기 위해 질문 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
            if mode == "번역하기":
                question =  question +  "\n Please translate it into Korean"
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]
            # audio 버퍼 확인을 위해 현 시점 오디오 정보 저장
            st.session_state["check_audio"] = audio
            flag_start = True

    with col2:

        st.subheader("질문/답변")
        if flag_start:
            response = ask_gpt(st.session_state["messages"], model)

            st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]

            # 채팅 시각화를 위한 답변 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            # 채팅 형식으로 시각화 하기
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

            # gTTS 를 활용하여 음성 파일 생성 및 재생
            text2speech(response)


if __name__ == "__main__":
    main()