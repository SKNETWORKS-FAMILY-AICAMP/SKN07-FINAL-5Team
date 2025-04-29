# 통합
import streamlit as st
import time
from sidebar import show_sidebar
# 모의 면접 URL class import
from utils.mock_interview import Mock_interview
import cv2
import numpy as np
from PIL import Image
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
import asyncio
import os
import uuid
from datetime import datetime
import base64
import re
from mutagen.mp3 import MP3
# import psutil
import glob
from dotenv import load_dotenv
import pyaudio, wave
from pydub import AudioSegment
import openai
from pathlib import Path
import shutil
from moviepy import VideoFileClip, AudioFileClip
import traceback


interview = Mock_interview()
st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")

audio_time_list = []

load_dotenv()


def get_parent_path():
    parent_path = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
    return parent_path


def page3():
    root_path = os.path.dirname(os.path.abspath(__file__))
    onecycle_second = 10
    CAM_FPS = 5 # 10
    CAM_FRAME_SIZE = (400,250)
    
    AUDIO_FORMAT = pyaudio.paInt16
    AUDIO_CHANNELS = 1
    AUDIO_RATE = 44100
    AUDIO_CHUNK = 1024

    audio_frames = []

    # 타이머 상태 저장
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False

    # 스트리밍 상태 저장
    if "streaming_running" not in st.session_state:
        st.session_state.streaming_running = False

    # 질문 상태 저장 
    if "qa_text" not in st.session_state:
        st.session_state.qa_text = ""

    # 오디오 레코딩 상태 저장
    if "recording" not in st.session_state:
        st.session_state.recording = False
    
    def time_format(seconds):
        return (str(seconds // 60) + ':'  if seconds >= 60 else '' )  + str(seconds % 60)

    def create_folder(path:str):
        if os.path.exists(path) == False:
            os.makedirs(path)
    
    def countdown_timer():
        st.session_state.timer_running = True
        q_count = 10

        audio_path = get_data_path('data/audio/tts/')
        q_list = ['1','2','3','4','5','6', '7', '8', '9', '10']
        try: 
            for i in range(q_count):
                qa_placeholder.write(re.sub(r"\s+"," ", q_list[i]))
                clock_count = 0 
                timer_stop_chk = True
                for seconds in range(onecycle_second, -1, -1):
                    clock_count += 1
                    time_placeholder.title(f':clock{clock_count}: {time_format(seconds)}')
                    if timer_stop_chk:
                        time.sleep(audio_file.info.length)
                        timer_stop_chk = False
                    else:
                        time.sleep(1)
                    if clock_count == 12:
                        clock_count = 0
        except Exception as e:
            st.error(f'audio and question Error : {e}')
        finally:
            time_placeholder.markdown("""<h2 style="text-align: center">종료</h2>""", unsafe_allow_html=True)
            st.session_state.timer_running = False  # 타이머 종료
            st.session_state.streaming_running = False # 웹캠 종료

    def itv_done():
        st.switch_page('pages/main_page.py')
    
    # 타이머, 오디오 쓰레드 생성
    timer_thread = threading.Thread(target=countdown_timer, daemon=True)
    # 쓰레드" 컨텍스트 추가
    add_script_run_ctx(timer_thread)

    async def webcam_start(frame_placeholder):
        background_image = Image.open(root_path+"/background_interviewer3.png")

        if background_image is not None:
            # 배경 이미지 로드 및 변환
            # bg_image = Image.open("images/background_interviewer1.png")
            bg_image = np.array(background_image)
            
            if st.session_state.timer_running == False:
                timer_thread.start()

            if st.session_state.recording == False:
                audio_thread.start()
                st.session_state.recording = True
            if st.session_state.streaming_running == False:
                st.session_state.streaming_running = True
            

            
            try:
                while st.session_state.streaming_running:
                    frame_placeholder.image(background_image, user_container_width=True)
                    await asyncio.sleep(0.1)
            except Exception as e:
                st.error(f'Webcam Error : {e}')
            finally:
                # 웹캠 종료
                st.session_state['streaming_running'] = False
                video_writer.release()
                cap.release()
                cv2.destroyAllWindows()
                
    async def main_loop(frame_placeholder):
        await asyncio.gather(webcam_start(frame_placeholder))
    

    hide_sidebar = """
        <style>
            .stAppHeader {
                background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
                visibility: visible;  /* Ensure the header is visible */
            }
            
            .stApp {
                background : white;
            }

            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
            [data-testid="stSidebar"] {
                display: none;
            }
            .st-emotion-cache-l1ktzw e486ovb18 {
                display: none;
            }
            .qa_wrap {
                width: 100%;
                height: 80px;
                border: 1px solid black;
            }
             div[data-testid="stColumn"]:nth-of-type(1)
            {
                border:1px solid yellow;
            } 

            div[data-testid="stColumn"]:nth-of-type(2)
            {
                border:1px solid blue;
                text-align: left;

            }

            div[data-testid="stColumn"]:nth-child(3) {
                text-align:right;
                border: 1px solid red;
            }
            div.st-key-webcam_container img {
                height:545px;
            }
        </style>
    """
    st.markdown(hide_sidebar, unsafe_allow_html=True)

    time_placeholder = None
    con1_0, con1_1 ,con1_2 = st.columns([0.3,1.7, 0.3])
    empty1, con2_1, empty2 = st.columns([0.3,1.7, 0.3])
    empty1, con3_1 ,empty2 = st.columns([0.3,1.7, 0.3])
    empty1, con4_1 ,empty2 = st.columns([0.3,1.7 ,0.3])
    frame_placeholder = None 
    audio_placeholder = None
    qa_placeholder = None
    itv_done_btn_placeholder = None

    with con1_0:
        st.markdown(""" <div>
                            <h2> 실전면접 </h2>
                        </div>""", unsafe_allow_html=True)

    with con1_1:
        pass
    
    with con1_2:
        time_placeholder = st.empty()
        audio_placeholder = st.empty()

    with con2_1:
        with st.container(border=True):
            qa_placeholder = st.empty()

    with con3_1:
        with st.container(key="webcam_container"):
            frame_placeholder = st.empty()

    with con4_1:
        itv_done_btn_placeholder = st.empty()
        #if st.button('면접종료'):
        #    st.switch_page('pages/main_page.py') 

    with empty2:
        pass
    asyncio.run(main_loop(frame_placeholder))



if __name__ == "__main__":
    page3()



