import streamlit as st
import random
import string


# 페이지 제목
st.markdown("""
    <h1 style='text-align: center;'>이력서 / 자소서 / 포트폴리오</h1>
    <h1 style='text-align: center;'>업로드</h1>
""", unsafe_allow_html=True)

    # 이력서, 자소서, 포트폴리오 업로드 섹션
st.header("이력서")
resume_file = st.file_uploader("이력서를 업로드하세요 (PDF) ", type=["pdf"])

st.header("자소서")
cover_letter_file = st.file_uploader("자소서를 업로드하세요 (PDF) ", type=["pdf"])

st.header("포트폴리오")
portfolio_file = st.file_uploader("포트폴리오를 업로드하세요 (PDF) ", type=["pdf"])

# 이력서 업로드 버튼 (우측 하단 배치)
st.markdown("""
    <div style='position: fixed; bottom: 20px; right: 20px;'>
        <button style='padding: 10px 20px; font-size: 16px;'>이력서 업로드</button>
    </div>
""", unsafe_allow_html=True)

