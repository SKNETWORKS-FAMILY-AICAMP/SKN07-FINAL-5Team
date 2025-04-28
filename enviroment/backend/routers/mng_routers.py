# 면접관리 Routers
from fastapi import APIRouter
from schemas.mng_q_schemas import MngQuestionSchema as MngQschema
from generate_question import GenerateQuestion

router = APIRouter(prefix="/mng")

@router.post("/get_question_list")
def get_question(data:MngQschema):
    question = GenerateQuestion()

    user_queries = [data.company_nm, data.job_nm, data.experience]
    applications = question.get_application_mats_from_db(user_id='interview')
    prev_questions = question.get_prev_questions_from_db(data.company_nm, data.job_nm, data.experience)

    # 질문 생성 후 session에 저장
    return question.generate_question(prev_questions, applications, user_queries)