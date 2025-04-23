import streamlit as st
import openai
import os
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

st.title("면접 챗봇")
st.write("면접관의 질문에 답변하고, 다음 질문을 받으세요!")

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TEMPLATE = """
    당신은 AI 면접관입니다. 사용자가 입력하는 [기업], [직무]에 기반하여 면접 질문을 합니다.

"""
def generate_questions(company, role):
    global result, comp
    prompt = TEMPLATE + f"""
    기업: {company}\n
    직무: {role}\n 
    면접 질문을 10개 생성하세요.
    - 했던 질문을 다시 하지 말 것.
    - 질문의 비율은 {company}에 관련 질문 2개, [인성면접]에 관련한 질문 2개, [기술역량]에 관한 질문 6개일 것.
    - 기술역량은 {role}에 관련된 것만 질문할 것.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "system", "content": prompt}]
    )
    res = response.choices[0].message.content.strip().split("\n")
    return response.choices[0].message.content.strip().split("\n")

if "questions" not in st.session_state:
    company = st.text_input("지원하는 기업을 입력하세요:")
    role = st.text_input("지원하는 직무를 입력하세요:")
    
    if st.button("질문 생성") and company and role:
        st.session_state.questions = generate_questions(company, role)
        st.session_state.step = 0
        st.session_state.conversation = []
        st.rerun()

if "questions" in st.session_state and st.session_state.step < len(st.session_state.questions):
    question = st.session_state.questions[st.session_state.step]
    st.write(f"**면접관:** {question}")
    
    user_answer = st.text_area("답변을 입력하세요:", value=st.session_state.get("user_answer", ""))
    
    if st.button("답변 제출") and user_answer.strip():
        st.session_state.conversation.append((question, user_answer.strip()))
        st.session_state.user_answer = ""  # 입력 필드 초기화
        st.session_state.step += 1
        st.rerun()

    global ans 
    ans = user_answer
else:
    st.write("면접이 종료되었습니다. 감사합니다!")
    st.write("### 면접 기록")
    for q, a in st.session_state.conversation:
        st.write(f"**면접관:** {q}")
        st.write(f"**지원자:** {a}")