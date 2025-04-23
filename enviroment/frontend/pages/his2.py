import streamlit as st
from sidebar import show_sidebar

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

st.title("히스토리 - 종합 레포트")

if st.button("⬅ 면접 히스토리로 돌아가기"):
    st.switch_page("pages/his1.py")

# 데이터 불러오기
if "selected_interview" not in st.session_state:
    st.session_state["selected_interview"] = {
        "title": "데이터 없음", "date": "N/A", "company": "N/A", "role": "N/A", "level": "N/A"
    }

interview = st.session_state["selected_interview"]

st.write(f"###  {interview['company']} - {interview['role']} ({interview['level']})")
st.write(f"면접 날짜: {interview['date']}")

# 탭 구성
tab1, tab2 = st.tabs(["종합 레포트", "상세 레포트"])

with tab1:
    col1, col2 = st.columns([1, 1])

    # 고정된 영역별 점수 데이터
    scores = {"논리성": 4, "질문 이해도": 3, "직무 전문성": 5}

    with col1:
        st.write("**영역별 점수**")
        for category, score in scores.items():
            st.write(f"{category}: {'★'*score}/ ({score}/5)")

    with col2:
        st.write("**총평 (한줄 요약 피드백)**")
        st.write("논리적으로 설명이 잘 되었으나, 질문 의도를 조금 더 고려하면 좋겠습니다.")

    st.markdown("---")


with tab2:
    # 두 개의 컬럼 생성 (70% : 30% 비율)
    col1, col2 = st.columns([2, 1])

    # 왼쪽 컬럼: 피드백 리스트
    with col1:
        feedback_data = [
            {"question": "공백기가 왜 이리 긴가?", "user_answer": "적절한 설명", "recommended_answer": "경험을 중심으로 설명", "feedback": "답변을 더 구체적으로 하면 좋습니다."},
            {"question": "이전 직장에서 어떤 역할을 했나요?", "user_answer": "데이터 분석 담당", "recommended_answer": "주요 프로젝트와 성과 포함", "feedback": "성과를 강조하면 좋습니다."},
            {"question": "공백기가 왜 이리 긴가?", "user_answer": "적절한 설명", "recommended_answer": "경험을 중심으로 설명", "feedback": "답변을 더 구체적으로 하면 좋습니다."},
            {"question": "공백기가 왜 이리 긴가?", "user_answer": "적절한 설명", "recommended_answer": "경험을 중심으로 설명", "feedback": "답변을 더 구체적으로 하면 좋습니다."},
            {"question": "공백기가 왜 이리 긴가?", "user_answer": "적절한 설명", "recommended_answer": "경험을 중심으로 설명", "feedback": "답변을 더 구체적으로 하면 좋습니다."},
            {"question": "공백기가 왜 이리 긴가?", "user_answer": "적절한 설명", "recommended_answer": "경험을 중심으로 설명", "feedback": "답변을 더 구체적으로 하면 좋습니다."},
        ]

        for idx, feedback in enumerate(feedback_data, 1):
            st.write(f"### {idx}번 질문 피드백")
            st.write(f"**질문:** {feedback['question']}")
            st.write(f"**사용자 답변:** {feedback['user_answer']}")
            st.write(f"**권장 답변:** {feedback['recommended_answer']}")
            st.write(f" {feedback['feedback']}")
            st.markdown("---")

    # 오른쪽 컬럼: 메모 입력
    with col2:
        memo = st.text_area("✍️ 면접 메모")


