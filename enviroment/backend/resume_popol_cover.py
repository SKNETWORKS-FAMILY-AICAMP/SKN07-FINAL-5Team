import os
import langchain_chroma
import openai
import chromadb
import fitz  # PDF에서 텍스트 추출
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import psycopg2
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# .env 파일 로드
load_dotenv()
# FastAPI 앱 초기화
app = FastAPI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POST_DB_HOST = os.getenv("POST_DB_HOST")
POST_DB_NAME = os.getenv("POST_DB_NAME")
POST_DB_USER = os.getenv("POST_DB_USER")
POST_DB_PASSWD = os.getenv("POST_DB_PASSWD")
POST_DB_PORT = os.getenv("POST_DB_PORT")

db = psycopg2.connect(host=POST_DB_HOST, dbname=POST_DB_NAME,user=POST_DB_USER,password=POST_DB_PASSWD,port=POST_DB_PORT)
cursor = db.cursor()
db.autocommit = False # 자동 커밋 False

user_id = 'interview' 

# read pdf & pdf to text
def read_pdf():
    path = "pdf 파일 경로"
    doc = fitz.open(path, filetype="pdf")
    resume_text = "\n".join([page.get_text("text") for page in doc])
    return resume_text



# 데이터 삽입 함수
def insert_data():
    sql = """
    INSERT INTO resume_popol_history (user_id, resume_text, cover_letter_text, popol_text)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(sql, (user_id, resume_text, cover_letter_text, popol_text))
    db.commit()
    cursor.close()
    db.close()

# 마지막 삽입 데이터 삭제 함수 / 왜쓰는지 알아보자
def del_last_data():
    sql = """
    delete from resume_popol_history 
        where user_id = %s
        and insert_date = ( select insert_date
                                from resume_popol_history rph
                                order by insert_date desc
                                limit 1
                                    );
    """
    cursor.execute(sql,(user_id))
    db.commit()
    cursor.close()
    db.close()

# text 임베딩 함수 
def get_embedding(text, model="text-embedding-3-large"):
    response = openai.embeddings.create(
        model=model,
        input=text.replace("\n", "").strip()
    )
    return response.data[0].embedding
# 사용 예시 embedding = get_embedding(text)


