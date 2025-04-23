import os
import fitz
import boto3
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
ACCESS_ID = os.getenv('S3_ACCESS_ID')
ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')

app = FastAPI()

# AWS S3 설정
AWS_ACCESS_KEY = "YOUR_ACCESS_KEY"
AWS_SECRET_KEY = "YOUR_SECRET_KEY"
BUCKET_NAME = "your-bucket-name"
REGION = "ap-northeast-2"

# S3 클라이언트 생성
s3 = boto3.client('s3',
                    aws_access_key_id=ACCESS_ID,
                    aws_secret_access_key=ACCESS_KEY)

bucket = BUCKET_NAME

# 파일 업로드
def upload_to_s3(file, filename):
    s3.upload_file(file, bucket, filename)
    return filename

# 가장 최근 파일 key 반환
def get_latest_file_key():
    response = s3.list_objects_v2(bucket)
    if "Contents" not in response:
        return None
    files = response["Contents"]
    latest = max(files, key=lambda x: x["LastModified"])
    return latest["Key"]

# 파일 다운로드
def download_file_from_s3(key, local_path):
    with open(local_path, "wb") as f:
        s3.download_file(bucket, key, f)
    return local_path

# pdf 파일 byte로 읽기기
def download_pdf_as_bytes(key):
    import io
    buffer = io.BytesIO()
    s3.download_file(bucket, key, buffer)
    buffer.seek(0)
    return buffer