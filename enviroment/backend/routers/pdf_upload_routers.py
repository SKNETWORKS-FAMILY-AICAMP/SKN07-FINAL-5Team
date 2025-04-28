# backend/routes/pdf_upload_router.py

import os
import boto3
from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
BUCKET = os.getenv("S3_BUCKET_NAME")

@router.post("/process_user_files")
async def process_user_files(
    resume: UploadFile = None,
    coverletter: UploadFile = None,
    portfolio: UploadFile = None,
    session_id: str = Form(...)
):
    try:
        files = {
            "resume": resume,
            "coverletter": coverletter,
            "portfolio": portfolio
        }

        for key, file in files.items():
            if file:
                print(f"📝 processing: {key}, filename={file.filename}")

                # ✅ read() 후 타입 체크
                content = await file.read()
                if not isinstance(content, (bytes, bytearray)):
                    raise TypeError(f"{key}의 파일 내용이 bytes가 아님. 실제 타입: {type(content)}")

                if len(content) == 0:
                    raise ValueError(f"{key} 내용이 비어있음")

                s3_key = f"user_uploads/{session_id}/{key}.pdf"
                s3.put_object(
                    Bucket=BUCKET,
                    Key=s3_key,
                    Body=content,
                    ContentType="application/pdf"
                )
                print(f"✅ S3 업로드 완료: {s3_key} ({len(content)} bytes)")

        return JSONResponse({"success": True})
    except Exception as e:
        print("🔥 예외 발생:", e)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
