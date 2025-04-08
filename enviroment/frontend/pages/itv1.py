# 7페이지: 모의면접 - 시작 화면
import streamlit as st
import time
from sidebar import show_sidebar

st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")

# 페이지 상단 공백 제거 markdown
# 페이지 전체에 회색 투명 배경과 중앙 정렬 CSS 적용
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
            /* 중앙에 배치할 컨테이너 스타일 */
            .centered-content {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 50vh;
            }

            .wrapper {
                display: grid;
                place-items: center;
                min-height: 100dvh;
            }

            .content {
                padding: 3rem;
                font-size: 2rem;
                border-radius: 1rem;
            }
        </style>
        """,
    unsafe_allow_html=True,
)

col_left, col_center, col_right = st.columns([0.2, 1, 0.2])

# 중앙 컨테이너 시작
# st.markdown("""
#             <div class="wrapper">
#                 <div class="content">
#                     <h2 style='text-align: center;'>면접 준비가 되었으면 아래 버튼을 눌러 면접을 시작해주십시오.</h1>
#             """, unsafe_allow_html=True)

# # 안내 문구
# # st.markdown("<h2 style='text-align: center;'>면접 준비가 되었으면 아래 버튼을 눌러 면접을 시작해주십시오.</h1>", unsafe_allow_html=True)

# # 면접 시작 버튼
# # if st.button("면접 시작"):
# #     st.switch_page("pages/itv2.py")

# # 중앙 컨테이너 종료
# st.markdown("""</div>
#             </div>""", unsafe_allow_html=True)
with col_left:
    pass
with col_center:
    st.markdown("""
            <div class="centered-content">
                <h2 style='text-align: center;'>면접 준비가 되었으면 아래 버튼을 눌러 면접을 시작해주십시오.</h1>
            </div>
            """, unsafe_allow_html=True)
    center_col_left, center_col_center, center_col_right = st.columns([1, 1, 1])
    with center_col_left:
        pass
    with center_col_center:
        if st.button("면접 시작"):
            st.switch_page("pages/itv2.py")
    with center_col_right:
        pass
with col_right:
    pass
show_sidebar()