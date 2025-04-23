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

enable = st.checkbox("카메라 체크크")
picture = st.camera_input("Take a picture", disabled=not enable)

if picture:
    st.image(picture)


audio_value = st.audio_input("마이크 체크")
if audio_value:
    st.audio(audio_value)


if st.checkbox("2가지 모두 정상"):
    time.sleep(1)
    st.switch_page("pages/itv1.py")





    