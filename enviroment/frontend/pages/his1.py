import os
import sys
import streamlit as st
from datetime import datetime # 나중에 datetime 쓸거 같아서 넣어놓음
from sidebar import show_sidebar

# --------- IMPORT CLASS FROM OTHER DIRS ----------
# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/enviroment/frontend)
main_dir = os.path.abspath(os.path.join(current_dir, ".."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from utils.history_service import History_service

hs = History_service()

if "page_num" not in st.session_state:
    st.session_state.page_num = 1

def get_history_list():
    req_data = { "user_id" : 'interview',
                 "page_num" : st.session_state['page_num'] }

    headers = {'accept': 'application/json',
               'Content-Type':'application/json; charset=utf-8'}

    return hs.get_history_list(req_data, headers)

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

                div.st-key-board_container {
                    display: ruby;
                    text-align: center;
                }
        </style>
        """,
    unsafe_allow_html=True,
)

# 페이지 제목
st.title("면접 히스토리")

# 데이터
history_info = get_history_list()
interviews = history_info['history_data']
# 면접 히스토리 리스트
for interview in interviews:
    with st.expander(f"📄 종합레포트 / 모의면접  ({interview['insert_date']})"):
        st.write(f"**기업:** {interview['company_name']}")
        st.write(f"**직무:** {interview['job_name']}")
        st.write(f"**경력:** {interview['person_exp']}")

        # 페이지 이동을 위한 버튼
        btn_key = f"btn_{interview['interview_id']}"
        if st.button("📊 면접 결과 분석", key=btn_key):
            st.session_state['selected_interview'] = interview
            st.session_state['history_interview_id'] = interview['interview_id']

            st.switch_page("pages/his2.py")   # 페이지 이동

empty1, center, empty2 = st.columns([0.5,2,0.5])

with empty1:
    pass

with center:
    cols = st.columns(history_info['total_page'])
    #for idx, col in enumerate(cols):
    #for idx in range(history_info['total_page']):
    #    with col:
    #        page_num = idx + 1
    #        btn_type = 'secondary'
    #        if page_num == st.session_state['page_num']:
    #            btn_type = 'primary'
#
 #           if st.button(str(page_num), type=btn_type):
  #              st.session_state['page_num'] = page_num
   #             st.switch_page("pages/his1.py")

    with st.container(key="board_container"):
        for idx in range(history_info['total_page']):
            page_num = idx + 1
            btn_type = 'secondary'
            if page_num == st.session_state['page_num']:
                btn_type = 'primary'

            if st.button(str(page_num), type=btn_type, key=str(page_num)):
                st.session_state['page_num'] = page_num
                st.switch_page("pages/his1.py")
with empty2:
    pass