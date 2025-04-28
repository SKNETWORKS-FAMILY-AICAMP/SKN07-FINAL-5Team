import os
import sys
import streamlit as st
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

def get_history_detail():
    req_data = { "interview_id" : st.session_state['history_interview_id'] }

    headers = {'accept': 'application/json',
               'Content-Type':'application/json; charset=utf-8'}

    return hs.get_history_report(req_data, headers)


def memo_save(memo):
    req_data = {"memo" : memo,
                "interview_id" : st.session_state['history_interview_id']
                }

    headers = {'accept': 'application/json',
               'Content-Type':'application/json; charset=utf-8'}

    hs.update_history_memo(req_data, headers)

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
            .section-title{
                font-size: 1rem;
                font-weight: bold;
            }
            .col{
                height: 200px;
            }
            .col-medium{
                height: 150px;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .score-section{
                display: flex;
                flex-direction: row;
            }
            .score-container{
                display: flex;
                flex-direction:column;
                justify-content: center;
            }
            .review-container{
                background-color: #dfedfe;
                padding: 1rem 0.8rem;
                border-radius: 8px;
            }
            label{
                text-align: center;
                font-size: 0.9rem !important;

            }
            .score{
                font-size: 2.5rem !important;
                font-weight: bold;
                text-align: center;
            }
            .criteria{
                font-size: 1.2rem !important;
                font-weight: bold;
            }
            .review{
                font-size: 1rem;
            }
        </style>
        """,
    unsafe_allow_html=True,
)

st.title("히스토리 - 종합 레포트")

if st.button("⬅ 면접 히스토리로 돌아가기"):
    st.switch_page("pages/his1.py")

history_info = get_history_list()

interviews = history_info['history_data']

print(interviews)

# interview_id = st.session_state["history_interview_id"]

interview = next(item for item in interviews)

print(interview)

# 데이터 불러오기
# if "selected_interview" not in st.session_state:
#     st.session_state["selected_interview"] = {
#         "title": "데이터 없음", "date": "N/A", "company": "N/A", "role": "N/A", "level": "N/A"
#     }

# interview = st.session_state["selected_interview"]

# if "interview_data" not in st.session_state:
#     st.session_state["interview_data"] = {
#         "question_text": "데이터가 존재하지 않습니다.",
#         "answer_all_review": "데이터가 존재하지 않습니다."
#     }

# evaluations = st.session_state["evaluations"]

# if "evaluations" not in st.session_state:
#     st.session_state["evaluations"] = {
#         "answer_example_text": "데이터가 존재하지 않습니다.",
#         "answer_all_review": "데이터가 존재하지 않습니다."
#     }

# evaluations = st.session_state["evaluations"]

# if "total_evaluations" not in st.session_state:
#     st.session_state["total_evaluations"] = {
#         "answer_all_review": "데이터가 존재하지 않습니다.",
#         "score": {
#             "qs_relevance": "N/A",
#             "clarity": "N/A",
#             "job_relevance": "N/A"
#         },
#         "answer_logic": "...",
#         "q_comp": "...",
#         "job_exp": "...",
#         "hab_chk": "...",
#         "time_mgmt": "..."
#     }

# total_evaluations = st.session_state["total_evaluations"]

st.write(f"### {interview['company_name']} - {interview['job_name']} ({interview['person_exp']})")
st.write(f"면접 날짜: {interview['insert_date']}")

history_detail = get_history_detail()


# 탭 구성
tab1, tab2 = st.tabs(["종합 레포트", "상세 레포트"])
report_data = history_detail['report_data']

with tab1:
    col1, col2 = st.columns([1, 1])
    row1 = st.columns([1, 2])

    # 영역별 점수
    scores = {
            "질문 적합성": report_data['area_score_one'],
            "논리성과 구체성": report_data['area_score_two'],
            "직무 연관성": report_data['area_score_three']}

    answer_all_review = "..."

    with col1:
        st.write("<p class='section-title'>영역별 점수</p>", unsafe_allow_html=True)

        cols = st.columns(len(scores))
        for col, (category, score) in zip(cols, scores.items()):
            with col:
                st.write(f"<div class='score-container col'><p class='score'>{score}</p><label>{category}</label></div>", unsafe_allow_html=True)
    overall_review = report_data['overall_review']
    with col2:
        st.write("<p class='section-title'>총평</p>", unsafe_allow_html=True)
        st.write(f"<div class='review-container col'>{overall_review}</div>", unsafe_allow_html=True)

    # ----------- 구분선
    st.divider()

    # 평가기준별 총평
    reviews = {
        "논리성": report_data['answer_logic'],
        "질문 이해도": report_data['q_comp'],
        "직무 전문성": report_data['job_exp'],
        "습관 체크": report_data['hab_chk'],
        "시간 활용도": report_data['time_mgmt']
    }

    col1, col2 = st.columns([1, 2])
    for criteria, review in reviews.items():
        with col1:
                st.write(f"<div class='criteria col-medium'>{criteria}</div>", unsafe_allow_html=True)

        with col2:
                st.write(f"<div class='review col-medium'>{review}</div>", unsafe_allow_html=True)



    st.markdown("---")





with tab2:
    # 두 개의 컬럼 생성 (70% : 30% 비율)
    col1, col2 = st.columns([2, 1])

    # 왼쪽 컬럼: 피드백 리스트
    with col1:
        feedback_data = history_detail['result_data']

        for idx, feedback in enumerate(feedback_data, 1):
            st.write(f"### {idx}번 질문 피드백")
            st.write(f"**질문:** {feedback['question']}")
            st.write(f"**사용자 답변:** {feedback['user_answer']}")
            st.write(f"**권장 답변:** {feedback['recommended_answer']}")
            st.write(f"{feedback['feedback']}")
            st.markdown("---")

    # 오른쪽 컬럼: 메모 입력
    with col2:
        memo = st.text_area("✍️ 면접 메모", value=report_data['memo'])
        _ , col2 = st.columns([6.5,1])
        with _:
            pass
        with col2:
            if st.button('저장'):
                memo_save(memo)