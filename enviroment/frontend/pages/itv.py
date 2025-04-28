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

def page1():
    def get_audio_time(audio_path:str, process_id:str):
        if os.path.exists(audio_path):
            join_path = os.path.join(get_parent_path(), audio_path)
            for audio_file in glob.glob(f'{join_path}/{process_id}_?.mp3'):
                mp3_file = MP3(audio_file)
                audio_time_list.append(mp3_file.info.length) 
        else:
            pass

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
                /* Streamlit 앱 전체 배경 설정 */
                .stApp {
                    background: rgba(128, 128, 128, 0.5);
                }
                /* 중앙에 배치할 컨테이너 스타일 */
                .centered-content {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 50vh;
                }

                .wrapper {
                    display: grid;
                    place-items: center;
                    min-height: 100dvh;
                }

                .content {
                    padding: 3rem;
                    font-size: 2rem;
                    border-radius: 1rem;
                }

                div.stButton {
                    text-align:center;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
    start_placeholder = st.empty()
    start_button_placeholder = st.empty()
    start_placeholder.markdown("""
                <div class="centered-content">
                    <h2 style='text-align: center;'>면접 준비가 되었으면 아래 버튼을 눌러 면접을 시작해주십시오.</h1>
                </div>
                """, unsafe_allow_html=True)

    if start_button_placeholder.button("면접 시작", key="interview_start"  ):
        audio_html = """
                    <audio id="start_audio" src="" style="display:none;"></audio>
                    <script>
                       audio = document.getElementById('start_audio');
                       audio.play();
                    </script>
                     """ 
        st.components.v1.html(audio_html, height=0, width=0)
        
        req_data = { "user_id" : 'interview',
                     "question_list" : st.session_state['new_questions'],
                     "company_cd": str(st.session_state['company_cd']),
                     "job_cd" : st.session_state['job_cd'],
                     "experience" : st.session_state['experience'] }
                 
        headers = {'accept': 'application/json',
                   'Content-Type':'application/json; charset=utf-8'}

        result = interview.interview_start(req_data, headers)
        st.session_state['q_list'] = result['q_list']
        st.session_state['process_id'] = result['process_id']
       
        get_audio_time(result['audio_path'], result['process_id'])
        
        
        start_placeholder.empty()
        start_button_placeholder.empty()
        page2()


def page2():
    def countdown_timer(seconds):
        while seconds > 0:
            time.sleep(1)
            seconds -= 1
            time_placeholder.markdown('<h2 style="text-align: center">' + str(seconds) +  "</h2>", unsafe_allow_html=True)
    
        time_placeholder.markdown("""<h2 style="text-align: center">START!</h2>""", unsafe_allow_html=True)
    
    
    time_placeholder = None

    empty_container = st.empty()
    
    with empty_container.container():
        empty1, con1_1, con1_2, con1_3,  empty2 = st.columns([0.3, 0.3 , 0.3 ,0.3 , 0.3])
        empty1, con2_1, con2_2, con2_3,  empty2 = st.columns([0.3, 0.3 , 0.3 ,0.3 , 0.3])

        with empty1:
            pass

        with con1_1:
            pass

        with con1_2:
            current_dir = os.path.dirname(__file__) 
            st.image(f"{current_dir}/loading.gif")

        with con1_3:
            pass

        with con2_1:
            pass

        with con2_2:
            time_placeholder = st.empty()

        with con2_3:
            pass


        with empty2:
            pass


    countdown_timer(4)
    # 로딩이 끝난 후 화면 전환
    time.sleep(1)
    empty_container.empty()
    page3()


def page3():
    root_path = os.path.dirname(os.path.abspath(__file__))
    onecycle_second = 10
    CAM_FPS = 5 # 10
    CAM_FRAME_SIZE = (400,250)
    process_id = st.session_state['process_id']
    
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


    def get_data_path(data_path):
        parent_path = get_parent_path()
        now_time = datetime.now()
        join_path = f'{data_path}{now_time.year}/{now_time.strftime("%m%d")}/'
        root_path = os.path.join(parent_path, join_path)

        return root_path

    def create_folder(path:str):
        if os.path.exists(path) == False:
            os.makedirs(path)
    
    def countdown_timer():
        st.session_state.timer_running = True
        q_count = 10

        def read_mp3(audio_file_path):
            audio_data_url = ''
            try :
                file = open(audio_file_path, "rb")
                audio_bytes = file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()
                audio_data_url = f"data:audio/mp3;base64,{audio_base64}"
            except FileNotFoundError as e:
                print(e)

            return audio_data_url
        
        def q_convert_text(text):
            q_list = []
            
            for t in text.split('\n'):
                q_list.append(re.sub(' +', ' ', t))

            return '\n'.join(q_list)

        audio_path = get_data_path('data/audio/tts/')
        q_list = st.session_state['q_list']
        try: 
            for i in range(q_count):
                audio_file_path = f'{audio_path}{process_id}_{i}.mp3'
                audio_file = MP3(audio_file_path)
                data_url = read_mp3(audio_file_path)
                            
                # process = psutil.Process(os.getpid())

                # print("Memory usage (MB):", process.memory_info().rss / 1024 / 1024)
                script_code = f""" <audio id="test" src="{data_url}" style="display:none;"> </audio>
         
                                    <script>
                                        audio = document.getElementById('test')
                                        audio.play()
                                    </script>
                                 """
                st.components.v1.html(script_code, height=0, width=0) # height 값을 적절히 조정
                #qa_placeholder.write(q_convert_text(q_list[i]))
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

    def video_merge(video_output_path:str, audio_output_path:str, merge_output_path:str):
        try:
            video_file = VideoFileClip(video_output_path)
            audio_file = AudioFileClip(audio_output_path)

            video = video_file.with_audio(audio_file)

            video.write_videofile(merge_output_path,codec="libx264", audio_codec="aac")
        except Exception as e:
            print(f'[merge file] {e}')

    def audio_record_process():
        def audio_callback(in_data, frame_count, time_info, status):
            audio_frames.append(in_data)
            return (None, pyaudio.paContinue)
        # st.write('쓰레드 안에 들어왔습니다')
        total_time = 0
        for audio_time in audio_time_list:
            total_time += audio_time

        total_time  = (total_time + (onecycle_second * 10)) 
        # st.write(f'쓰레드 시간 {total_time}')
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=AUDIO_FORMAT,
            channels=AUDIO_CHANNELS,
            rate=AUDIO_RATE,
            input=True,
            frames_per_buffer=AUDIO_CHUNK,
            stream_callback=audio_callback
        )
        # st.write('스트림 시작 전')
        stream.start_stream()
        # st.write('녹음 시작')
        # 60초 동안 백그라운드 녹음
        time.sleep(total_time)
        # st.error('녹음 끝')
        stream.stop_stream()
        stream.close()
        pa.terminate()

        write_path = get_data_path('data/user_video/')
        create_folder(write_path)
        file_path = f"{write_path}{process_id}_audio.wav"
        if "audio_file_path" not in st.session_state:
            st.session_state['audio_file_path'] = file_path
        # WAV 파일로 저장
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(AUDIO_CHANNELS)
        wf.setsampwidth(pa.get_sample_size(AUDIO_FORMAT))
        wf.setframerate(AUDIO_RATE)
        wf.writeframes(b''.join(audio_frames))
        wf.close()
        original_audio_path = f"{write_path}{process_id}_audio_original.wav"
        shutil.copyfile(file_path, original_audio_path)
        audio_file_list = audio_split()
        result = question_result_process(audio_file_list)
        video_merge(f"{write_path}{process_id}_video.mp4", original_audio_path, f"{write_path}{process_id}_merge_viedo.mp4")
        if result['status'] == 'ok':
            def itv_done():
                st.switch_page('pages/main_page.py')
            itv_done_btn_placeholder.button('면접 종료', on_click=itv_done) 
            
    # 타이머, 오디오 쓰레드 생성
    timer_thread = threading.Thread(target=countdown_timer, daemon=True)
    audio_thread = threading.Thread(target=audio_record_process, daemon=True)
    # 쓰레드" 컨텍스트 추가
    add_script_run_ctx(timer_thread)
    add_script_run_ctx(audio_thread)

    def audio_split():
        audio_file_path = st.session_state.audio_file_path
        audio_file = AudioSegment.from_wav(audio_file_path)
        # 0 > 68
        # 68 > 136
        # 136 > 21
        temp_file_list = []
        start_time, end_time = 0, 0
        write_path = get_data_path('data/user_video/')
        for idx in range(10):
            if idx > 0:
                end_time = (start_time + onecycle_second + audio_time_list[idx])
            else:
                end_time = (onecycle_second + audio_time_list[idx]) 

            
            #st.write(f'idx : {idx} , start_time : {start_time}, end_time : {end_time}, onecycle_second : {onecycle_second}, audio_time_list : {audio_time_list[idx]}')
            segment = audio_file[(start_time * 1000):(end_time * 1000)]
            temp_file_path = f"{write_path}{process_id}_audio_{idx}.wav"
            temp_file_list.append(temp_file_path)
            segment.export(temp_file_path,format="wav") 
                
            
            start_time = end_time
        

        return temp_file_list


    def question_result_process(answer_file_list):
        question_list = st.session_state['new_questions']
        answer_list = []
        interview_id = process_id.split('_')[-1]
        
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        client = openai.OpenAI()
         
        for idx, answer_file in enumerate(answer_file_list):
            #st.write(answer_file)
            with open(answer_file, 'rb') as f:
                transpiction =  client.audio.transcriptions.create(
                                        model="whisper-1",
                                        file=f,
                                        language="ko",
                                        response_format="text",
                                        temperature=0.0
                                )
          



            answer_list.append(transpiction)

        result_dict = {"interview_id" : interview_id,
                       "question_list" : question_list,
                       "answer_list" : answer_list,
                       "video_path" : ""}
        # st.write(answer_list)
        headers = {'accept': 'application/json',
                               'Content-Type':'application/json; charset=utf-8'}
        result = interview.interview_result_process(result_dict, headers)        
        return result
         

    async def webcam_start(frame_placeholder):
        background_image = Image.open(root_path+"/background_interviewer1.png")

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
                # writer 설정
                write_path = get_data_path('data/user_video/')
                create_folder(write_path)
                file_path = f'{write_path}{process_id}_video.mp4'
                # 웹캠 설정
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FPS, CAM_FPS)  # FPS 속성 설정 (지원하는 경우)

                # 웹캠 크기 설정
                cam_width, cam_height = 200, 150  # 웹캠 크기 조정
                margin_x, margin_y = 30, 30  # 오른쪽 상단 여백
                
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
                # 프레임 크기 및 FPS 설정 (웹캠의 값을 가져오거나, 직접 지정)
                _frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                _frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                _fps = cap.get(cv2.CAP_PROP_FPS)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(file_path, fourcc, _fps, (_frame_width, _frame_height))
    
                while st.session_state.streaming_running:
                    ret, frame = cap.read()
                    if not ret:
                        st.error("웹캠을 불러올 수 없습니다.")
                        break
                    

                    video_writer.write(frame)
                    # 웹캠 크기 조정
                    # frame = cv2.resize(frame, (cam_width, cam_height))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR → RGB 변환
                    # 배경 이미지에 웹캠 영상 오버레이
                    #overlay_image = bg_image.copy()  # 원본 이미지 복사
                    #h, w, _ = overlay_image.shape  # 배경 이미지 크기

                    # 웹캠을 오른쪽 상단에 위치
                    #y1, y2 = margin_y, margin_y + cam_height
                    #x1, x2 = w - margin_x - cam_width, w - margin_x

                    # 웹캠 프레임을 배경 위에 배치
                    #overlay_image[y1:y2, x1:x2] = frame  
                    # qa_placeholder.write(st.session_state.qa_text) 
                    # 이미지 업데이트
                    frame_placeholder.image(frame, use_container_width =True)
                    #await time.sleep(0.1)  # 루프 지연 추가
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
        </style>
    """
    st.markdown(hide_sidebar, unsafe_allow_html=True)

    time_placeholder = None
    empty1, con1_1, con1_2 ,empty2 = st.columns([0.3,1.5, 1.5, 0.3])
    empty1, con2_1, empty2 = st.columns([0.3,1, 0.3])
    empty1, con3_1 ,empty2 = st.columns([0.3,1.5, 0.3])
    empty1, con4_1 ,empty2 = st.columns([0.3,1 ,0.3])
    frame_placeholder = None 
    audio_placeholder = None
    qa_placeholder = None
    itv_done_btn_placeholder = None
    with empty1:
        pass

    with con1_1:
        st.markdown(""" <div>
                            <h2> 실전면접 </h2>
                        </div>""", unsafe_allow_html=True)
    
    with con1_2:
        time_placeholder = st.empty()
        audio_placeholder = st.empty()

    with con2_1:
        with st.container(border=True):
            qa_placeholder = st.empty()

    with con3_1:
        frame_placeholder = st.empty()

    with con4_1:
        itv_done_btn_placeholder = st.empty()
        #if st.button('면접종료'):
        #    st.switch_page('pages/main_page.py') 

    with empty2:
        pass

    asyncio.run(main_loop(frame_placeholder))



if __name__ == "__main__":
    page1()


