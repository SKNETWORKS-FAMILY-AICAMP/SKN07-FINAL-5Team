import sys
import requests
import os
import fitz  # PyMuPDF
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
from typing import Dict

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.8)

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
es_store = ElasticSearchBM25Retriever(client=es_client, index_name="job_position", k=30)

chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": 30})
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

hybrid_chain = (
    {"context": hybrid_retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def recommend_jobs(text: str) -> str:
    return hybrid_chain.invoke(text)

