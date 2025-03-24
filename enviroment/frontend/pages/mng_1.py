import streamlit as st
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
#   st.title("이력서 / 자소서 / 포트폴리오 \n업로드")
st.markdown("""
<h1 style='text-align: center; font-size: 36px; color: #000000; line-height: 1.2;'>이력서 / 자소서 / 포트폴리오</h1>
<h2 style='text-align: center; font-size: 30px; color: #000000;'>업로드</h2>
""", unsafe_allow_html=True)

# 이력서 업로드
st.markdown("""
    <h4 style='color: #333; font-size: 18px;'>이력서</h4>
""", unsafe_allow_html=True)
resume_file = st.file_uploader("이력서를 업로드하세요 (PDF)", type=["pdf"])

# 자소서 업로드
st.markdown("""
    <h4 style='color: #333; font-size: 18px;'>자소서</h4>
""", unsafe_allow_html=True)
cover_letter_file = st.file_uploader("자소서를 업로드하세요 (PDF)", type=["pdf"])

# 포트폴리오 업로드
st.markdown("""
    <h4 style='color: #333; font-size: 18px;'>포트폴리오</h4>
""", unsafe_allow_html=True)
portfolio_file = st.file_uploader("포트폴리오를 업로드하세요 (PDF)", type=["pdf"])

# 입력 완료 
if st.button("입력 완료"):
    st.switch_page("pages/equipment_test.py")