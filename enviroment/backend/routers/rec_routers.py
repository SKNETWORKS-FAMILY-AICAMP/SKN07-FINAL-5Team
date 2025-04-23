## 추천공고 Routers  
#from fastapi import APIRouter
#import os
#from dotenv import load_dotenv
#import chromadb
#from elasticsearch import Elasticsearch
#from elasticsearch.helpers import bulk
#from chromadb.config import Settings
#from langchain.vectorstores import Chroma
#from langchain.embeddings import OpenAIEmbeddings
#from langchain.schema import Document
#from langchain.chat_models import ChatOpenAI
#from langchain.prompts import PromptTemplate
#from langchain_core.runnables import RunnableLambda, RunnablePassthrough
#from langchain_core.output_parsers import StrOutputParser
#from langchain_core.prompts import PromptTemplate
#from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnableMap
#from langchain_core.output_parsers import StrOutputParser
#router = APIRouter(prefix="/rec")
#
#
#
#
## 환경변수 설정
#load_dotenv()
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#CHROMA_HOST = os.getenv("CHROMA_HOST")
#CHROMA_PORT = os.getenv("CHROMA_PORT")
#USER = os.getenv("USER")
#PASSWORD = os.getenv("PASSWORD")
#
## ---------------------------- 데이터 베이스 설정 -------------------------------
#chroma_client = chromadb.HttpClient(
#    host=CHROMA_HOST,
#    port=CHROMA_PORT,
#    settings=Settings(allow_reset=True, anonymized_telemetry=False)
#)
#collection = chroma_client.get_collection(name="job_position")
#
#chroma_db = Chroma(
#    collection_name="job_position",
#    embedding_function=embeddings,
#    client=chroma_client
#)
#
#es_client = Elasticsearch(ELASTICSEARCH_HOST_PORT, basic_auth=(USER, PASSWORD))
#elasticsearch_store = ElasticsearchStore(
#    es_connection=es_client,
#    index_name="job_position",
#    embedding=embeddings,
#)
##-------------------------------- 리트리버 만들기 --------------------------------------
#chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": 20})
#es_retriever = elasticsearch_store.as_retriever(search_kwargs={"k": 20})
#
#from langchain.retrievers import EnsembleRetriever
#
#hybrid_retriever = EnsembleRetriever(
#    retrievers=[chroma_retriever, es_retriever],
#    weights=[0.7, 0.3],
#)
#
##--------------------------------- app? -----------------------------------------------
#
#
#from prompts import rag_prompt
#
#llm = ChatOpenAI(model_name="gpt-4o", temperature=1)
#
#hybrid_chain = (
#    {"context": hybrid_retriever, "question": RunnablePassthrough()}
#    | rag_prompt
#    | llm
#    | StrOutputParser()
#)
#
#def recommed_generate(resume_text):
#    response = hybrid_chain.invoke(resume_text)
#    return response
#
#@router.post("/recommend")
#def get_recommendation(resume_text: dict):
#    text = resume_text["resume_text"]
#    result = hybrid_chain.invoke(text)
#    return {"recommendations": result}
#
