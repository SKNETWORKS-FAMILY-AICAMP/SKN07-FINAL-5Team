from fastapi import APIRouter, Query, HTTPException
import boto3, os, json, fitz, re
from backend.RAG import recommend_jobs
 
router = APIRouter()
s3 = boto3.client("s3")
BUCKET = os.getenv("S3_BUCKET_NAME")
 
@router.get("/recommend")
def recommend(session_id: str = Query(...)):
    try:
        text = ""
 
        for name in ["resume", "coverletter", "portfolio"]:
            try:
                obj = s3.get_object(Bucket=BUCKET, Key=f"user_uploads/{session_id}/{name}.pdf")
                content = obj['Body'].read()

                if not isinstance(content, (bytes, bytearray)):
                    raise TypeError(f"{name} PDF content is not bytes")

                with fitz.open(stream=content, filetype="pdf") as doc:
                    extracted = "\n".join(page.get_text() for page in doc)
                    text += f"# --- {name.upper()} ---\n{extracted}\n\n"
            except s3.exceptions.NoSuchKey:
                print(f"⚠️ {name}.pdf not found in S3")
            except Exception as file_err:
                print(f"❌ PDF 파싱 실패 ({name}): {file_err}")
                continue
 
        print("📄 최종 텍스트 길이:", len(text))

        result = recommend_jobs(text)

        if not isinstance(result, str):
            raise ValueError(f"recommend_jobs() 결과가 문자열이 아님: {type(result)}")

        clean_json = re.sub(r"//.*", "", result)
        return json.loads(clean_json)
 
    except Exception as e:
        print("🔥 추천 처리 실패:", e)
        raise HTTPException(status_code=500, detail=f"추천 중 오류 발생: {e}")
     
