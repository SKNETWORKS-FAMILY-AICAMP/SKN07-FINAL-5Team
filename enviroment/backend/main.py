from typing import Union, Optional
from fastapi import APIRouter, FastAPI, status, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.RAG import read_pdf_recommend_recruit
import fitz
import boto3
import os
from pathlib import Path
import uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID'),
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY'),
BUCKET_NAME = os.getenv('BUCKET_NAME')

app = FastAPI(
    title="SKAI Networks7 mock interview",
    version="0.1"
)

# 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# s3 object storage
s3 = boto3.client(
    "s3",
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
    )
bucket_name = os.getenv('BUCKET_NAME')

recommendation_results = {} # 추천된 공고

@app.post("/process_user_files")
async def process_user_files(
    session_id: str = Form(...),
    resume: Optional[UploadFile] = File(None),
    coverletter: Optional[UploadFile] = File(None),
    portfolio: Optional[UploadFile] = File(None),
):
    uploaded_files_content = {}
    has_uploaded = False
    try:
        if resume:
            has_uploaded = True
            resume_content = await resume.read()
            uploaded_files_content["resume"] = resume_content
            filename = resume.filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"user_files/{session_id}/{timestamp}_resume_{filename}"
            try:
                s3.upload_fileobj(resume.file, BUCKET_NAME, s3_key,
                                  ExtraArgs={"Metadata": {"session_id": session_id, "original_filename": filename, "file_type": "resume", "upload_timestamp": datetime.now().isoformat()}})
                print(f"'resume_{filename}'이(가) S3에 업로드되었습니다 (Key: {s3_key})")
            except Exception as e_s3:
                print(f"S3 업로드 오류 (resume): {e_s3}")

        if coverletter:
            has_uploaded = True
            coverletter_content = await coverletter.read()
            uploaded_files_content["coverletter"] = coverletter_content
            filename = coverletter.filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"user_files/{session_id}/{timestamp}_coverletter_{filename}"
            try:
                s3.upload_fileobj(coverletter.file, BUCKET_NAME, s3_key,
                                  ExtraArgs={"Metadata": {"session_id": session_id, "original_filename": filename, "file_type": "coverletter", "upload_timestamp": datetime.now().isoformat()}})
                print(f"'coverletter_{filename}'이(가) S3에 업로드되었습니다 (Key: {s3_key})")
            except Exception as e_s3:
                print(f"S3 업로드 오류 (coverletter): {e_s3}")

        if portfolio:
            has_uploaded = True
            portfolio_content = await portfolio.read()
            uploaded_files_content["portfolio"] = portfolio_content
            filename = portfolio.filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"user_files/{session_id}/{timestamp}_portfolio_{filename}"
            try:
                s3.upload_fileobj(portfolio.file, BUCKET_NAME, s3_key,
                                  ExtraArgs={"Metadata": {"session_id": session_id, "original_filename": filename, "file_type": "portfolio", "upload_timestamp": datetime.now().isoformat()}})
                print(f"'portfolio_{filename}'이(가) S3에 업로드되었습니다 (Key: {s3_key})")
            except Exception as e_s3:
                print(f"S3 업로드 오류 (portfolio): {e_s3}")

        if has_uploaded:
            # PDF 내용들을 RAG 모듈로 처리하고 추천 결과 얻기
            recommendations = read_pdf_recommend_recruit(uploaded_files_content)
            recommendation_results[session_id] = recommendations
            return {"success": True, "message": "파일 처리 및 추천 준비 완료"}
        else:
            return {"success": False, "error": "업로드된 파일이 없습니다."}

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/recommendations/{session_id}")
async def get_recommendations(session_id: str):
    results = recommendation_results.get(session_id)
    if results:
        return {"recommendations": results}
    else:
        return {"recommendations": []}

#app.include_router(api_router)
class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"

@app.get("/")
def read_root():
    return {"Hello": "World123"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get('/get_user_info')
def get_user_info():
    connect = post_db_connect()
    result = connect.select_one("select * from user_info where user_id = 'interview'")
    connect.close()
    return {'user_info' : result}

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")

