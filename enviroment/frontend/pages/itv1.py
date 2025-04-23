import streamlit as st
import time
from sidebar import show_sidebar

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
# 7페이지: 모의면접 - 시작 화면

st.title("모의면접 - 기업/직무")

# 안내 문구
st.write("면접 준비가 되었으면 아래 버튼을 눌러 면접을 시작해주십시오.")

# 면접 시작 버튼
if st.button("면접 시작"):
    st.switch_page("pages/itv2.py")