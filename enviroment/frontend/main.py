import streamlit as st
import requests
from dotenv import load_dotenv
import os
from sidebar import show_sidebar

st.set_page_config(layout="wide")

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

# 환경파일 로드
load_dotenv()
show_sidebar()

# 백엔드 연동 테스트
try:
    test_req = requests.get(os.environ.get('API_URL'))
    user_info = requests.get(os.environ.get('API_URL') + "/get_user_info")
except requests.exceptions.RequestException as e:
    test_req, user_info = None, None
    st.error(f"백엔드 연결 실패: {e}")


st.switch_page("pages/main_page.py")
