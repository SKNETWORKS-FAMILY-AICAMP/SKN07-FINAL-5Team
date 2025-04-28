import streamlit as st 
from sidebar import show_sidebar
import requests
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

# Docker 환경에서는 container name 사용
BACKEND_URL = "http://backend:9999"
st.set_page_config(layout="wide")
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

show_sidebar()

st.title("📄 지원 서류 제출")
st.markdown("**PDF** 파일로 업로드 해주셔야 합니다!")

# 세션 ID 생성 (업로드 + 추천 연동용)
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

# 파일 업로드
uploaded_resume = st.file_uploader(f"**이력서 업로드**", type=["pdf"])
uploaded_coverletter = st.file_uploader(f"**자기소개서 업로드**", type=["pdf"])
uploaded_portfolio = st.file_uploader(f"**포트폴리오 업로드**", type=["pdf"])

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
            # requests에 넘길 files 구조: (filename, fileobj, content_type)
            formatted_files = {
                k: (v.name, v, v.type or "application/pdf")
                for k, v in files.items()
            }

            response = requests.post(
                f"{BACKEND_URL}/process_user_files",
                files=formatted_files,
                data={"session_id": session_id}
            )

            result = response.json()
            if result.get("success"):
                st.success("파일들이 성공적으로 업로드 되었습니다.")
                st.session_state["recommendation_ready"] = True
            else:
                st.error(f"파일 처리 실패: {result.get('error', '알 수 없는 오류')}")
    except Exception as e:
        st.error(f"백엔드 연결 오류: {e}")

# 업로드 성공 시 안내 메시지 표시
if st.session_state.get("recommendation_ready"):
    st.info("지원자님의 서류를 바탕으로 추천 드릴만한 공고가 있어요!")
