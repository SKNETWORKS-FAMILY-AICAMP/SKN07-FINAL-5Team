import streamlit as st
from sidebar import show_sidebar
import os
import sys

# # 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

main_dir = os.path.abspath(os.path.join(current_dir, ".."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from utils.mock_interview import Mock_interview


interview = Mock_interview()

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

# session에 기업명, 직무, 경력 여부, 연차 저장
def set_company_job_info():
    st.session_state['company_name'] = company_name
    st.session_state['job_name'] = job_title
    st.session_state['experience'] = experience_years
    if experience_years == '경력':
        st.session_state['experience_year'] = experience_placeholder

st.title("기업 / 직무 / 경력 입력")

common_select_text = "선택해주세요"

# 기업 리스트 조회
# 첫번째 문구는 "선택해주세요" 로 나오게 추가
company_info = interview.get_company_list()
company_list = company_info['company_list']
# 직무 리스트 조회
# 첫번째 문구는 "선택해주세요" 로 나오게 추가
job_info = interview.get_job_list()
job_list = job_info['job_list']


# 기업 입력
company_name = st.selectbox("기업 선택", company_info['labels']) 
# 비어 있는 컨테이너 생성
company_placeholder = st.empty()

# 직무 입력 
job_title = st.selectbox("지원 직무 선택", job_info['labels']) 
# 비어 있는 컨테이너 생성
job_placeholder = st.empty()

# 경력 입력
experience_years = st.selectbox("경력", ["신입", "경력"])
# 비어 있는 컨테이너 생성
experience_placeholder = st.empty()

# 버튼을 거의 붙여서 정렬
col1, col2 = st.columns([5, 5])

# 이전, 다음 페이지 이동
# with col1:
#     if st.button("이전"):
#         st.session_state["page"] = "mng_1" # 포트폴리오 업로드 페이지 이동
#         st.rerun()

if experience_years == '경력':
    experience_placeholder.number_input('연차를 입력하세요', value=1, step=1, min_value=1, max_value=50, format="%d")
else:
    experience_placeholder.empty()

with col2:
    if st.button("입력 완료"):
        # 기업 확인
        if company_name == common_select_text:
            company_placeholder.warning('기업을 선택해주세요!' , icon="⚠️")
        # 직무 확인
        if job_title == common_select_text:
            job_placeholder.warning('직무를 선택해주세요!' , icon="⚠️")
        # 기업, 직무 골랐을 시 장비테스트 페이지 이동
        if company_name != common_select_text and \
           job_title != common_select_text:
            set_company_job_info()
            st.switch_page("pages/equipment_test.py")