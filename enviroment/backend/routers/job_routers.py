# backend/routes/job_router.py
from fastapi import APIRouter, Query
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# Elasticsearch 클라이언트 설정
es_client = Elasticsearch(
    os.getenv("ELASTICSEARCH_HOST_PORT"),
    basic_auth=(
        os.getenv("USER"),
        os.getenv("PASSWORD")
    )
)

@router.get("/all_jobs")
def get_all_jobs(page: int = 1, page_size: int = 10):
    from_ = (page - 1) * page_size
    res = es_client.search(
        index="job_position",
        body={
            "query": {"match_all": {}},
            "from": from_,
            "size": page_size
        }
    )

    # 필요한 메타데이터 필드를 꺼내서 클린한 형태로 반환
    jobs = []
    for hit in res["hits"]["hits"]:
        source = hit["_source"]
        job_data = {
            "공고명": source.get("metadata", {}).get("공고명", "N/A"),
            "기업명": source.get("metadata", {}).get("기업명", "N/A"),
            "지역": source.get("metadata", {}).get("지역", "N/A"),
            "경력": source.get("metadata", {}).get("경력", "N/A"),
            "학력": source.get("metadata", {}).get("학력", "N/A")
        }
        jobs.append(job_data)

    return jobs
