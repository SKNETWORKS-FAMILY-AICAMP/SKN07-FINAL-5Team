import streamlit as st 
from sidebar import show_sidebar
import sys
import requests
import os
import fitz  # PyMuPDF
import streamlit as st
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from elasticsearch import Elasticsearch
from langchain.vectorstores import Chroma, ElasticsearchStore
from langchain_community.retrievers import ElasticSearchBM25Retriever
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers import EnsembleRetriever
import json
import re
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

# 카드 스타일 정의
card_style = """
<style>
.card {
    background-color: #f9f9f9;
    padding: 20px;
    margin-bottom: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
.card h4 {
    margin-bottom: 10px;
}
.badge {
    display: inline-block;
    background: #007ACC;
    color: white;
    padding: 3px 8px;
    border-radius: 10px;
    font-size: 12px;
    margin-right: 5px;
}
</style>
"""

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

# 임베딩 및 LLM 설정
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.8, )

# 벡터 DB 설정
chroma_client = chromadb.HttpClient(
    host="43.202.186.183",
    port=8000,
    settings=Settings(allow_reset=True, anonymized_telemetry=False)
)
chroma_db = Chroma(
    collection_name="job_position",
    embedding_function=embeddings,
    client=chroma_client
)

es_client = Elasticsearch("http://43.202.186.183:9200", basic_auth=('elastic', 'ElastiC7276'))
es_store = ElasticSearchBM25Retriever(
    client=es_client,
    index_name="job_position",
    k=5
)

# 리트리버 설정
chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": 5})
#es_retriever = es_store.as_retriever(search_kwargs={"k": 5})
hybrid_retriever = EnsembleRetriever(
    retrievers=[chroma_retriever, es_store],
    weights=[0.7, 0.3],
)

# 프롬프트 템플릿
prompt = PromptTemplate.from_template("""
You are a talent matching AI assistant. Please recommend 5 job openings based on the applicant information provided (resume, cover letter, portfolio).

- Make sure to make a judgment based on the full contents of the applicant information provided (resume, cover letter, portfolio).
- Explain the reasons for recommending job openings in one line. Explain in detail what part of your resume, cover letter, and portfolio you recommended and why you recommended them.
- If the same announcement number is duplicated, only one is recommended.
- Analysis based on the entire job posting. Don't judge based on the title alone.
- Judging based on the full text of page_content.


# Be sure to follow the following rules.
[Rules]
- Be sure to respond with JSON in the following format.
- Be sure to print only JSON arrays.
- Be sure not to use code block markdowns such as ```json or ```.
- Be sure to output JSON purely without explanation or comment.
- Never // put the same comment
                                      
                                      
# output example                                      
{{
    "공고명" : "정책팀 PR 인턴 채용(정규직 전환 가능)",
    "기업명" : "(주)코딧",
    "직무" : ['PM(프로젝트매니저)', 'PMO', '개발PM'],
    "지역" : "경기 성남시 분당구",
    "경력" : "2-5년차",
    "학력" : "학사 이상(4년대졸)",
    "추천 이유" : "Python을 사용한 대규모 데이터 핸들링 및 AI 시스템 개발 경험이 요구되어 이력서의 기술 스택과 잘 맞습니다."                                                                                                                                                                                   
}}

answer in korean

# 지원자 정보:
{question}
# 채용공고:
{context}                                       
""")

# 체인 구성
hybrid_chain = (
    {"context": hybrid_retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Streamlit UI
st.title("📄 이력서 기반 채용 공고 추천")
# 파일 업로더 추가
uploaded_resume = st.file_uploader("이력서를 PDF로 업로드하세요", type=["pdf"])
uploaded_coverletter = st.file_uploader("자기소개서를 PDF로 업로드하세요", type=["pdf"])
uploaded_portfolio = st.file_uploader("포트폴리오를 PDF로 업로드하세요", type=["pdf"])

# 업로드된 파일들로부터 텍스트 추출 및 결합
combined_text = ""

if uploaded_resume is not None:
    with st.spinner("이력서 파싱 중..."):
        try:
            with fitz.open(stream=uploaded_resume.read(), filetype="pdf") as doc:
                resume_text = ""
                for page in doc:
                    resume_text += page.get_text()
                combined_text += "# --- 이력서 내용 --- \n" + resume_text + "\n\n"
                st.success("이력서 파싱 완료.")
        except Exception as e:
             st.error(f"이력서 파싱 오류: {e}")


if uploaded_coverletter is not None:
    with st.spinner("자기소개서 파싱 중..."):
        try:
            with fitz.open(stream=uploaded_coverletter.read(), filetype="pdf") as doc:
                coverletter_text = ""
                for page in doc:
                    coverletter_text += page.get_text()
                combined_text += "# --- 자기소개서 내용 --- \n" + coverletter_text + "\n\n"
                st.success("자기소개서 파싱 완료.")
        except Exception as e:
             st.error(f"자기소개서 파싱 오류: {e}")


if uploaded_portfolio is not None:
    with st.spinner("포트폴리오 파싱 중..."):
        try:
            with fitz.open(stream=uploaded_portfolio.read(), filetype="pdf") as doc:
                portfolio_text = ""
                for page in doc:
                    portfolio_text += page.get_text()
                combined_text += "# --- 포트폴리오 내용 --- \n" + portfolio_text + "\n\n"
                st.success("포트폴리오 파싱 완료.")
        except Exception as e:
             st.error(f"포트폴리오 파싱 오류: {e}")



# 결합된 텍스트를 RAG 체인의 입력으로 사용
result = hybrid_chain.invoke(combined_text)

if result:
    st.button("추천 공고")
    clean_json = re.sub(r"//.*", "", result)
    response = json.loads(clean_json)

if response:
    st.subheader("추천 공고") # 버튼 대신 부제목으로 변경 (필요시 버튼 유지 가능)

    # 한 줄에 몇 개의 컨테이너를 표시할지 설정
    num_columns = 2
    # 데이터를 기준으로 몇 줄을 만들지 계산
    num_rows = (len(response) + num_columns - 1) // num_columns

    # 여러 줄에 걸쳐 컨테이너 생성
    item_index = 0 # 전체 데이터 인덱스
    for i in range(num_rows):
        cols = st.columns(num_columns)
        # 현재 줄에 표시될 데이터만 처리
        for j in range(num_columns):
            if item_index < len(response): # 표시할 데이터가 남아있는 경우
                job = response[item_index]
                with cols[j]:
                    # 각 컬럼 내에 컨테이너 생성 및 테두리 추가
                    with st.container(border=True):
                        st.subheader(job.get("공고명", "N/A")) # .get()으로 키 존재 여부 확인
                        st.write(f"**기업명:** {job.get('기업명', 'N/A')}")
                        st.write(f"**지역:** {job.get('지역', 'N/A')} | **경력:** {job.get('경력', 'N/A')} | **학력:** {job.get('학력', 'N/A')}")

                        # 직무는 Markdown을 사용하여 뱃지처럼 표시 (선택 사항)
                        job_roles = job.get("직무", [])
                        if job_roles:
                            # 각 직무를 감싸는 스타일 (둥근 모서리, 배경색 등) - Markdown 활용
                            badge_style = "display: inline-block; background-color: #e9ecef; color: #495057; padding: 0.2em 0.6em; margin: 0.2em; border-radius: 0.8rem; font-size: 0.9em;"
                            badges_html = "".join([f"<span style='{badge_style}'>{role}</span>" for role in job_roles])
                            st.markdown(f"**직무:** {badges_html}", unsafe_allow_html=True)
                        else:
                             st.write("**직무:** 정보 없음")

                        # 추천 이유 (존재하는 경우에만 표시)
                        if "추천 이유" in job and job["추천 이유"]:
                             # 약간의 여백과 함께 추천 이유 강조
                             st.markdown("---") # 구분선
                             st.markdown(f"**추천 이유:** _{job['추천 이유']}_") # 이탤릭체로 강조

                        # 필요하다면 여기에 지원하기 버튼 추가
                        # st.button("지원하기", key=f"apply_{item_index}")
                item_index += 1 # 다음 데이터로 인덱스 증가
            else:
                # 데이터가 더 없으면 빈 컨테이너 대신 아무것도 하지 않음
                pass
else:
    st.write("추천할 공고를 찾지 못했습니다.")

