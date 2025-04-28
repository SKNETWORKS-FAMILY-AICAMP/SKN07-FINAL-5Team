import streamlit as st
from sidebar import show_sidebar
import time
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

# 세션 상태 초기화
for key in ["webcam_bool", "audio_bool", "speaker_bool", "test_count", "ready_for_next"]:
    if key not in st.session_state:
        if "bool" in key or key == "ready_for_next":
            st.session_state[key] = False
        else:
            st.session_state[key] = 0

# 이미지 경로 자동 설정
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # pages 상위 폴더 기준
img_webcam = os.path.join(BASE_DIR, "images", "webcam.png")
img_mic = os.path.join(BASE_DIR, "images", "mic.png")
img_speaker = os.path.join(BASE_DIR, "images", "speaker.png")

# 완료 카드에 이미지만 출력하는 함수
def show_done_image(image_path):
    st.image(image_path, width=200)

# 웹캠 테스트 (완료 여부는 무시)
def webcam_test():
    webcam_status = st.empty()
    video_placeholder = st.empty()

    webcam = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not webcam.isOpened():
        webcam_status.error('❌ 웹캠이 감지되지 않습니다! ')
    else:
        webcam_status.write('1. 웹캠 테스트 :white_check_mark:')

        if not st.session_state.webcam_bool:
            frame_window = video_placeholder.image([])
            webcam.set(cv2.CAP_PROP_FPS, 10)
            webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
            webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)

            frame_count = 0
            stop_button_pressed = st.button("웹캠 영상 종료")
            while webcam.isOpened():
                ret, frame = webcam.read()
                if not ret:
                    st.error("카메라에서 영상을 읽어올 수 없습니다.")
                    break
                frame_count += 1
                if frame_count % 3 != 0:
                    continue
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_window.image(frame)
                time.sleep(0.1)
                if stop_button_pressed:
                    webcam.release()
                    video_placeholder.empty()
                    st.session_state.webcam_bool = True
                    break

# 마이크 테스트
def audio():
    audio_placeholder = st.empty()
    audio_input_box = st.empty()

    if not st.session_state.audio_bool:
        audio_placeholder.write("2. 마이크 테스트")

    audio_value = audio_input_box.audio_input("")

    if audio_value:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_value.getbuffer())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko",
                response_format="text",
                temperature=0.0
            )
        st.write(transcript)

        if len(transcript) > 0:
            audio_placeholder.empty()
            audio_input_box.empty()
            st.session_state.audio_bool = True
            show_done_image(img_mic)
            speak_test()

# 스피커 테스트
def speak_test():
    speaker_placeholder = st.empty()
    button_box = st.empty()
    audio_box = st.empty()

    if not st.session_state.speaker_bool:
        speaker_placeholder.write("3. 스피커 테스트")

    response = client.audio.speech.create(
        model="tts-1",
        input="스피커 테스트입니다. 스피커가 켜져있으면 확인 버튼을 눌러주세요.",
        voice="alloy",
        response_format="mp3",
        speed=1.1,
    )
    audio_box.audio(response.content)

    if button_box.button('스피커 확인'):
        speaker_placeholder.empty()
        button_box.empty()
        audio_box.empty()
        st.session_state.speaker_bool = True
        show_done_image(img_speaker)

        # 마이크 + 스피커 완료되면 "테스트 완료 버튼" 활성화
        if st.session_state.audio_bool and st.session_state.speaker_bool:
            st.session_state.ready_for_next = True

# 메인 함수
def main():
    st.set_page_config(layout="wide")
    show_sidebar()

    # 페이지 상단 공백 제거 스타일
    st.markdown("""
        <style>
            .stAppHeader { background-color: rgba(255, 255, 255, 0.0); visibility: visible; }
            .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 5rem; padding-right: 5rem; }
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    st.title("🎧 장비 테스트")

    # 테스트 순차 실행
    webcam_test()
    audio()

    # 마이크 + 스피커 모두 완료 시, 테스트 완료 버튼 표시
    if st.session_state.ready_for_next:
        st.success("✅ 모든 장비 테스트가 완료되었습니다.")
        if st.button('면접 시작'):
            time.sleep(1)
            st.switch_page("pages/itv.py")

# 스크립트 실행
if __name__ == "__main__":
    main()

