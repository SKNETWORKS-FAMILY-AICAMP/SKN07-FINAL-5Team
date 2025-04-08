import streamlit as st
import time
import os
from sidebar import show_sidebar

st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")

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
            /* Streamlit 앱 전체 배경 설정 */
            .stApp {
                background: rgba(128, 128, 128, 0.5);
            }
        </style>
        """,
    unsafe_allow_html=True,
)
# 페이지 제목 설정
#st.title("로딩중입니다 기다려!")


def countdown_timer(seconds):
    while seconds > 0:
        time.sleep(1)
        seconds -= 1
        time_placeholder.markdown('<h2 style="text-align: center">' + str(seconds) +  "</h2>", unsafe_allow_html=True)
    
    time_placeholder.markdown("""<h2 style="text-align: center">START!</h2>""", unsafe_allow_html=True)

time_placeholder = None
empty1, con1_1, con1_2, con1_3,  empty2 = st.columns([0.3, 0.3 , 0.3 ,0.3 , 0.3])
empty1, con2_1, con2_2, con2_3,  empty2 = st.columns([0.3, 0.3 , 0.3 ,0.3 , 0.3])

with empty1:
    pass

with con1_1:
    pass

with con1_2:
    st.markdown("![Alt Text](https://blog.kakaocdn.net/dn/tToNP/btsvPnc77bN/0P5cqJMFM8hpaQcrIbK6v1/img.gif)")

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

show_sidebar()
countdown_timer(4)

# 로딩이 끝난 후 화면 전환
time.sleep(1)
st.switch_page("pages/itv3.py")
