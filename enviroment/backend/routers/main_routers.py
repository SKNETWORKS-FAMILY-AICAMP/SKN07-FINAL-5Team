# 메인 Routers
from fastapi import APIRouter
from routers.his_routers import router as his_routers
from routers.itv_routers import router as itv_routers
from routers.mng_routers import router as mng_routers
#from routers.rec_routers import router as rec_routers
from routers.common_routers import router as common_routers

api_router = APIRouter(prefix="/mock")
api_router.include_router(his_routers)
api_router.include_router(itv_routers)
api_router.include_router(mng_routers)
#api_router.include_router(rec_routers)
api_router.include_router(common_routers)