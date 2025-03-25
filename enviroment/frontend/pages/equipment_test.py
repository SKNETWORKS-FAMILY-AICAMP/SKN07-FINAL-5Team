import streamlit as st
from sidebar import show_sidebar
import time
import cv2

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

enable = st.checkbox("카메라 체크")
#picture = st.camera_input("Take a picture", disabled=not enable)

webcam = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not webcam.isOpened():
    print("Could not open .webcam")
    exit()



frame_window = None

if enable:

    while enable:
        frame_window = st.image([])

        #cap = cv2.VideoCapture(0)
        webcam.set(cv2.CAP_PROP_FPS, 10)  # FPS 속성 설정 (지원하는 경우)

        frame_count = 0
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

        st.write("스트리밍 중지")
        webcam.release()


        # while webcam.isOpened():
        #     status, frame = webcam.read()

        #     if status:
        #         cv2.imshow("test", frame)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break


        # webcam.release()
        # cv2.destroyAllWindows()
elif frame_window != None and not enable:
    # webcam.release()
    # cv2.destroyAllWindows()
    frame_window.empty()

# if picture:
#     st.image(picture)


audio_value = st.audio_input("마이크 체크")
if audio_value:
    st.audio(audio_value)


if st.checkbox("2가지 모두 정상"):
    time.sleep(1)
    st.switch_page("pages/itv1.py")





    