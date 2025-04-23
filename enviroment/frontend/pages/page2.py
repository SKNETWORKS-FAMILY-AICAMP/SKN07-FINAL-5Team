import streamlit as st
import cv2
import time
import numpy as np
from sidebar import show_sidebar

st.set_page_config(layout="wide")
show_sidebar()

# Remove whitespace from the top of the page and sidebar
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


def app():
    # st.title("Page 1")
    # st.write("This is the content of Page 1.")
    test()


def main():
    #st.set_page_config(page_title="Streamlit WebCam App")
    st.title("Webcam Display Steamlit App")
    st.caption("Powered by OpenCV, Streamlit")
    cap = cv2.VideoCapture(0)
    frame_placeholder = st.empty()
    stop_button_pressed = st.button("Stop")
    while cap.isOpened() and not stop_button_pressed:
        ret, frame = cap.read()
        if not ret:
            st.write("Video Capture Ended")
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame,channels="RGB")
        if cv2.waitKey(1) & 0xFF == ord("q") or stop_button_pressed:
            break
    cap.release()
    cv2.destroyAllWindows()

def webcam():
    # 세션 상태에 스트림 실행 여부 초기화
    if 'run' not in st.session_state:
        st.session_state.run = False

    # 스트림 시작/종료를 위한 함수
    def start():
        st.session_state.run = True

    def stop():
        st.session_state.run = False

    st.title("OpenCV & Streamlit 웹캠 스트리밍")

    # 시작, 종료 버튼 생성 (양쪽 컬럼 활용)
    col1, col2 = st.columns(2)
    col1.button("시작", on_click=start)
    col2.button("종료", on_click=stop)

    # 영상 프레임을 표시할 자리
    FRAME_WINDOW = st.empty()

    # 웹캠 열기 (기본 웹캠은 인덱스 0)
    cap = cv2.VideoCapture(0)

    # 웹캠 스트림 실행
    while st.session_state.run:
        ret, frame = cap.read()
        if not ret:
            st.error("웹캠 영상을 가져올 수 없습니다.")
            break

        # OpenCV는 BGR 형식이므로 RGB로 변환 (Streamlit은 RGB를 사용)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 영상 프레임을 업데이트하여 표시
        FRAME_WINDOW.image(frame)
        
        # 부드러운 스트리밍을 위한 딜레이
        time.sleep(0.03)

    # 웹캠 리소스 해제
    cap.release()


def test():
    webcam = cv2.VideoCapture(0)

    if not webcam.isOpened():
        print("Could not open webcam")
        exit()

    test = False
    while webcam.isOpened():
        status, frame = webcam.read()
        if status:
            cv2.imshow("test", frame)
            # time.sleep(3)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    webcam.release()
    cv2.destroyAllWindows()


def test2():
    st.title("OpenCV Filters on Video Stream")

    filter = "none"


    def transform(frame: av.VideoFrame):
        img = frame.to_ndarray(format="bgr24")

        if filter == "blur":
            img = cv2.GaussianBlur(img, (21, 21), 0)
        elif filter == "canny":
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)
        elif filter == "grayscale":
            # We convert the image twice because the first conversion returns a 2D array.
            # the second conversion turns it back to a 3D array.
            img = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        elif filter == "sepia":
            kernel = np.array(
                [[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]]
            )
            img = cv2.transform(img, kernel)
        elif filter == "invert":
            img = cv2.bitwise_not(img)
        elif filter == "none":
            pass

        return av.VideoFrame.from_ndarray(img, format="bgr24")


    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

    with col1:
        if st.button("None"):
            filter = "none"
    with col2:
        if st.button("Blur"):
            filter = "blur"
    with col3:
        if st.button("Grayscale"):
            filter = "grayscale"
    with col4:
        if st.button("Sepia"):
            filter = "sepia"
    with col5:
        if st.button("Canny"):
            filter = "canny"
    with col6:
        if st.button("Invert"):
            filter = "invert"


    webrtc_streamer(
        key="streamer",
        video_frame_callback=transform,
        sendback_audio=False
        )