import streamlit as st
import time
import os
from sidebar import show_sidebar

st.set_page_config(layout="wide")
show_sidebar()

# 페이지 상단 공백 제거 및 중앙 정렬 적용
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

        [data-testid="stSidebarNav"] {
            display: none;
        }

        /* 중앙 정렬 */
        .center-text {
            text-align: center;
        }

        .center-image {
            display: flex;
            justify-content: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 중앙 정렬된 제목
st.markdown('<h1 class="center-text">로딩중입니다 기다려!</h1>', unsafe_allow_html=True)

# 중앙 정렬된 GIF
st.markdown(
    """
    <div class="center-image">
        <img src="https://blog.kakaocdn.net/dn/tToNP/btsvPnc77bN/0P5cqJMFM8hpaQcrIbK6v1/img.gif" width="300">
    </div>
    """,
    unsafe_allow_html=True,
)

# 2초 후 페이지 이동
time.sleep(2)
st.switch_page("pages/itv3.py")
