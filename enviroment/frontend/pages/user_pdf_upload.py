import streamlit as st 
from sidebar import show_sidebar
import sys
import requests
import os
import fitz  # PyMuPDF
import boto3
import uuid
from dotenv import load_dotenv
load_dotenv()

BACKEND_URL = "http://localhost:9999"

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

# Streamlit UI ---------------------------------------------
st.title("📄 사용자 ")
st.subheader(f"**pdf** 파일로 업로드 해주셔야 합니다!")
# 파일 업로더 추가
uploaded_resume = st.file_uploader("이력서 업로드", type=["pdf"])
uploaded_coverletter = st.file_uploader("자기소개서 업로드", type=["pdf"])
uploaded_portfolio = st.file_uploader("포트폴리오 업로드", type=["pdf"])



if uploaded_resume or uploaded_coverletter or uploaded_portfolio:
    session_id = st.session_state['session_id']
    files = {}
    if uploaded_resume:
        files['resume'] = uploaded_resume
    if uploaded_coverletter:
        files["coverletter"] = uploaded_coverletter
    if uploaded_portfolio:
        files["portfolio"] = uploaded_portfolio

    try:
        with st.spinner("파일들을 분석하여 채용 공고를 추천 준비 중입니다..."):
            response = requests.post(f"{BACKEND_URL}/process_user_files", files=files, data={"session_id": session_id})
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                st.success("파일들이 성공적으로 업로드 되었습니다.")
                st.session_state["recommendation_ready"] = True
            else:
                st.error(f"파일 처리 실패: {result.get('error', '알 수 없는 오류')}")
    except requests.exceptions.RequestException as e:
        st.error(f"백엔드 연결 오류: {e}")

if st.session_state.get("recommendation_ready"):
    st.info("채용 공고 추천을 보려면 왼쪽 사이드바의 '채용 공고 추천' 메뉴를 클릭하세요.")
