import streamlit as st
from audiorecorder import audiorecorder
import openai
from datetime import datetime
import numpy as np
from function import speech2text, text2speech, ask_gpt

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

    # 기능 구현 공간
    col1, col2 = st.columns(2)
    with col1:
        # 왼쪽 영역 작성
        st.subheader("질문하기")
        # 음성 녹음 아이콘 추가
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
        # 오른쪽 영역 작성
        st.subheader("질문/답변")
        if flag_start:
            # ChatGPT에게 답변 얻기
            response = ask_gpt(st.session_state["messages"], model)

            # GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
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