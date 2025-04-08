import streamlit as st
from sidebar import show_sidebar
import time
import cv2
import tempfile
import openai
import os
from dotenv import load_dotenv

load_dotenv()
# OpenAI API 키 설정
openai.api_key = os.environ.get('OPENAI_API_KEY')
client = openai.OpenAI()

if "webcam_bool" not in st.session_state:
    st.session_state.webcam_bool = False

if "audio_bool" not in st.session_state:
    st.session_state.audio_bool = False

if "speaker_bool" not in st.session_state:
    st.session_state.speaker_bool = False

if "test_count" not in st.session_state:
    st.session_state.test_count = 0

def main():
    st.set_page_config(layout="wide")
    show_sidebar()
    # 페이지 상단 공백 제거 markdown
    st.markdown(
        """
            <style>
                    .stAppHeader {
                        background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
                        visibility: visible;  /* Ensure the header is visible */
                    }

                .block-container {
                        padding-top: 1rem;
                        padding-bottom: 0rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
                    [data-testid="stSidebarNav"] {display: none;}
            </style>
            """,
        unsafe_allow_html=True,
    )

    st.title("장비 테스트")

    webcam_placeholder = st.empty()
    
    #st.write('1. 웹캠 테스트 :no_entry_sign:')
    
    webcam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    st.write(st.session_state.webcam_bool)
    if not webcam.isOpened() and st.session_state.webcam_bool == False:
        webcam_placeholder.write('1. 웹캠 테스트 :no_entry_sign:')
    else:
        st.session_state.webcam_bool = True
        webcam_placeholder.write('1. 웹캠 테스트 :white_check_mark:')
 
    #container = st.container(border=True)

    # # 컨테이너 생성
    # container = st.container()

    
    
    if st.session_state.test_count == 0:
        # 컨테이너 내부 UI 요소를 비우기 위한 empty() 객체
        content_placeholder = st.empty()
        
        with content_placeholder.container(border=True if webcam.isOpened() else False):
            frame_window = st.image([])

            webcam.set(cv2.CAP_PROP_FPS, 10)  # FPS 속성 설정 (지원하는 경우)
            webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
            webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)

            frame_count = 0
            stop_button_pressed = st.button("종료")
            if stop_button_pressed:
                webcam.release()
                content_placeholder.empty()  # 컨테이너 내부 요소 삭제
                st.session_state.test_count = st.session_state.test_count + 1
                
            #stop_button_pressed = st.button("종료")
            while webcam.isOpened():
                ret, frame = webcam.read()
                if not ret:
                    st.error("카메라에서 영상을 읽어올 수 없습니다.")
                    break

                frame_count += 1
                # 3프레임 중 1프레임만 처리하여 부하 줄이기
                if frame_count % 3 != 0:
                    continue

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_window.image(frame)
                time.sleep(0.1)  # 루프 지연 추가
                if stop_button_pressed:
                    webcam.release()
                    break
        
        #webcam.release()
    audio()

def audio():
    audio_placeholder = st.empty()
    if st.session_state.audio_bool == False:
        audio_placeholder.write("2. 마이크 테스트 :no_entry_sign:")
    else:
        audio_placeholder.write("2. 마이크 테스트 :white_check_mark:")

    audio_value = st.audio_input("")

    if audio_value:
        # 임시 파일에 오디오 저장
        tmp_path = ''
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_value.getbuffer())
            tmp_path = tmp.name
       
        transcript = ''
        # OpenAI Whisper API를 사용하여 전사 수행
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko",
                response_format="text",
                temperature=0.0
            )
                
        st.write(transcript)
        # st.write(audio_value)
        # audio_data = st.audio(audio_value)

        if len(transcript) > 0:
            if st.session_state.audio_bool == False:
                audio_placeholder.write("2. 마이크 테스트 :white_check_mark:")
            st.session_state.audio_bool = True
            speak_test()

def speak_test():
    speaker_placeholder = st.empty()

    if st.session_state.speaker_bool == False:
        speaker_placeholder.write("3. 스피커 테스트 :no_entry_sign:")
    else:
        speaker_placeholder.write("3. 스피커 테스트 :white_check_mark:")

    response = client.audio.speech.create(
        model="tts-1",
        input="스피커 테스트입니다. 스피커가 켜져있으면 확인 버튼을 눌러주세요.",
        voice="alloy",
        response_format="mp3",
        speed=1.1,
    )
    
    st.audio(response.content)

    if st.button('확인'):
        if st.session_state.speaker_bool == False:
            speaker_placeholder.write("3. 스피커 테스트 :white_check_mark:")
        st.session_state.speaker_bool = True



def test_done():
    if st.button('테스트 완료'):
        time.sleep(1)
        st.switch_page("pages/mng_2.py")

if __name__ == "__main__":
    #st.switch_page("pages/mng_2.py")
    main()
    
    
    if st.session_state.webcam_bool == True  \
        and st.session_state.audio_bool == True \
        and st.session_state.speaker_bool == True:
        col1 , col2 = st.columns([1,1])
        with col1:
            st.write("테스트가 완료되었으면 준비완료 버튼을 클릭하세요")
        with col2:
            if st.button('테스트 완료', key="test_done"):
                time.sleep(1)
                st.switch_page("pages/itv1.py")
