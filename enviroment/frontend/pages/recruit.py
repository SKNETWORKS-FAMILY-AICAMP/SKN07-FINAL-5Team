import streamlit as st
import fitz
import requests
import random
from sidebar import show_sidebar


st.set_page_config(layout="wide")
show_sidebar()

BACKEND_URL = "http://backend:9999"

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
             .card {
            background-color: #f9f9f9;
            padding: 1.2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }
        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        .card-meta {
            font-size: 0.9rem;
            color: #555;
        }
        .card-badge {
            display: inline-block;
            background-color: #007acc;
            color: white;
            padding: 0.3em 0.8em;
            margin: 0.2em 0.2em 0 0;
            border-radius: 0.6em;
            font-size: 0.85em;
        }
        .card-reason {
            font-style: italic;
            color: #0066cc;
            border-top: 1px solid #eee;
            margin-top: 1rem;
            padding-top: 0.5rem;
        }
                </style>

                """,
            unsafe_allow_html=True
        )

st.title("📄 채용 공고")

if "session_id" not in st.session_state:
    st.info("지원 서류를 업로드 해보세요! 구직자에게 맞는 채용공고를 추천 드릴게요 😀.")
    st.stop()

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

page_size = 10
current_page = st.session_state.current_page

session_id = st.session_state["session_id"]
response = []
recommended = False
if st.button("채용 공고 추천 받기"):
    try:
        res = requests.get(f"{BACKEND_URL}/api/recommend", params={"session_id": session_id})
        res.raise_for_status()
        response = res.json()
        recommended = True
    except Exception as e:
        st.error(f"추천 요청 실패: {e}")

# 추천 결과 출력 (2열 카드)
if response:
    st.subheader("추천 공고")

    num_columns = 2
    num_rows = (len(response) + num_columns - 1) // num_columns

    item_index = 0
    for i in range(num_rows):
        cols = st.columns(num_columns)
        for j in range(num_columns):
            if item_index < len(response):
                job = response[item_index]
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"<div style='padding: 7px;'>", unsafe_allow_html=True)
                        st.markdown(f"### {job.get('기업명', 'N/A')}")
                        st.markdown(f"**공고명:** {job.get('공고명', 'N/A')}")
                        st.markdown(f"**지역:** {job.get('지역', 'N/A')} | **경력:** {job.get('경력', 'N/A')} | **학력:** {job.get('학력', 'N/A')}")

                        job_roles = job.get("직무", [])
                        if job_roles:
                            badges = " ".join([
                                f"<span style='background:#007acc; color:white; padding:4px 8px; border-radius:8px; margin-right:4px;'>{role}</span>"
                                for role in job_roles
                            ])
                            st.markdown(badges, unsafe_allow_html=True)

                        st.markdown("---")
                        st.markdown(f"**추천 이유:** _{job.get('추천 이유', '')}_")
                        st.markdown(f"</div>", unsafe_allow_html=True)

                item_index += 1
# 전체 공고 가져오기
try:
    res = requests.get(f"{BACKEND_URL}/api/all_jobs", params={"page": current_page, "page_size": page_size})
    res.raise_for_status()
    all_jobs = res.json()
except Exception as e:
    all_jobs = []

# 전체 공고 먼저 보여주기
if all_jobs:
    st.subheader("채용 공고")

    recommended_titles = {job.get("공고명") for job in response}
    filtered_jobs = [job for job in all_jobs if job.get("공고명") and job.get("기업명") not in recommended_titles]

    for job in filtered_jobs:
        with st.container(border=True):
            st.markdown(f"<div style='padding: 8px;'>", unsafe_allow_html=True)
            st.markdown(f"### {job.get('기업명', 'N/A')}")
            st.markdown(f"**공고명:** {job.get('공고명', 'N/A')}")
            st.markdown(f"**지역:** {job.get('지역', 'N/A')} | **경력:** {job.get('경력', 'N/A')} | **학력:** {job.get('학력', 'N/A')}")

            job_roles = job.get("직무", [])
            if job_roles:
                badges = " ".join([
                    f"<span style='background:#c0c0c0; color:white; padding:4px 8px; border-radius:8px; margin-right:4px;'>{role}</span>"
                    for role in job_roles
                ])
                st.markdown(badges, unsafe_allow_html=True)

            st.markdown(f"</div>", unsafe_allow_html=True)

# 페이지네이션 버튼
st.markdown("---")
page_numbers = list(range(1, 21))  # 예시: 1~20페이지
page_cols = st.columns(20)

for idx, page_number in enumerate(page_numbers):
    with page_cols[idx]:
        if st.button(str(page_number), key=f"page_{page_number}"):
            st.session_state.current_page = page_number
            st.rerun()
