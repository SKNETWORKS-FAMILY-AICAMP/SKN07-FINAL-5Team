import os
import fitz  # PyMuPDF
import streamlit as st
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from elasticsearch import Elasticsearch
from langchain.vectorstores import Chroma, ElasticsearchStore
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers import EnsembleRetriever

load_dotenv()


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
es_store = ElasticsearchStore(
    es_connection=es_client,
    index_name="job_position",
    embedding=embeddings,
)

# 리트리버 설정
chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": 5})
es_retriever = es_store.as_retriever(search_kwargs={"k": 5})
hybrid_retriever = EnsembleRetriever(
    retrievers=[chroma_retriever, es_retriever],
    weights=[0.7, 0.3],
)

# 프롬프트 템플릿
prompt = PromptTemplate.from_template("""
당신은 인재매칭 AI 어시스턴트입니다. 사용자 이력서에 기반하여 채용공고를 5개 추천해주세요.

- 반드시 이력서에 기반할 것.
- 출력 시 채용공고의 양식을 사용할 것.
- 출력 시 지역은 상세하게 출력 할 것.
- 채용공고 추천 이유를 한줄로 설명할 것.
- 같은 공고 번호가 중복될 경우 단 1개만 추천할 것.
- 채용공고 전체 내용을 기반하여 분석할 것. 제목만 보고 판단하지 말 것.
- page_content의 전체 텍스트를 기준으로 판단할 것.

#이력서:
{question}
#채용공고:
{context}

#출력형태
- 기업명, 공고명, [경력]
- 직무, 지역
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
uploaded_file = st.file_uploader("이력서를 PDF로 업로드하세요", type=["pdf"])

if uploaded_file is not None:
    resume_text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            resume_text += page.get_text()

    if st.button("추천 시작 🚀"):
        with st.spinner("채용 공고 분석 중..."):
            result = hybrid_chain.invoke(resume_text)
            st.subheader("🔍 추천된 채용 공고")
            st.markdown(result)
