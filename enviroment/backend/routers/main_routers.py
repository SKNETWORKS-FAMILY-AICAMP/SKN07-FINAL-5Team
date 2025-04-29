# 메인 Routers
from fastapi import APIRouter
from .his_routers import router as his_routers
from .itv_routers import router as itv_routers
from .mng_routers import router as mng_routers
from .rec_routers import router as rec_routers
from .common_routers import router as common_routers
from .job_routers import router as job_routers
from .pdf_upload_routers import router as pdf_upload_routers 

api_router = APIRouter(prefix="/mock")
api_router.include_router(his_routers)
api_router.include_router(itv_routers)
api_router.include_router(mng_routers)
api_router.include_router(rec_routers)
api_router.include_router(common_routers)
api_router.include_router(job_routers)
api_router.include_router(pdf_upload_routers)
