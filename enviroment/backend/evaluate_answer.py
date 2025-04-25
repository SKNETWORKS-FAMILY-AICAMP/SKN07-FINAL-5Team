import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from prompt.prompts import ev_hum_prompt, ev_eng_prompt, ev_arts_prompt, ev_list
from generate_question import GenerateQuestion


load_dotenv()

# --------- DIRECTORY PATH SETTING ----------
# # 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/backend)
main_dir = os.path.abspath(os.path.join(current_dir, "."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from db_util.db_utils import post_db_connect


# ------- 지원자료 데이터 로드 (이력서, 자기소개서, 포트폴리오) -------
def get_application_mats(user_id):
    """
    지원자료 데이터 로드 - 이력서, 자기소개서, 포트폴리오

    :param user_id: 면접자 ID
    """
    question = GenerateQuestion()

    appli_mats = question.get_application_mats_from_db(user_id)

    return appli_mats    

# ------- 면접 데이터 로드 (질문, 답변, 권장답변, 답변시간) -------
def get_interview_data(user_id):
    """
    면접 데이터 로드

    :param user_id: 면접자 ID
    """
    pdb = post_db_connect()

    # interview_process 테이블에서 가장 최신 날짜의 interview id 가져오기
    select_latest_query = f"""
    SELECT interview_id
    FROM interview_process
    WHERE user_id = '{user_id}'
    ORDER BY insert_date DESC
    LIMIT 1;
    """

    latest_itv = pdb.select_one(select_latest_query)
    interview_id = latest_itv['interview_id']

    # interview_id 로 면접 데이터 가져오기
    select_answer_query = """
    SELECT ques_text, answer_user_text, answer_end_time
    FROM interview_result
    WHERE interview_id = %s and answer_user_text is not null;
    """

    answer = pdb.select_all_vars(select_answer_query, interview_id)

    return answer

# ------- 평가지표 세팅 -------
def evaluate_answers(interview_data, application_mats, user_query):
    """
    답변 평가 생성 Agent

    :param interview_data: 면접 데이터 (질문, 유저답변, 권장답변, 답변시간)
    :param appli_mats: 지원자료 데이터
    :param user_query: streamlit session에서 받아올 정보 (회사명, 직무, 경력)
    """
    # 모델 정의
    llm = ChatOpenAI(
        model='gpt-4o-2024-08-06'
    )

    # 지원자료 분리
    if application_mats:
        resume = application_mats['resume_text']
        cover_letter = application_mats['cover_letter_text']
        portfolio = application_mats['popol_text']

    else:
        return "지원 자료 데이터가 존재하지 않습니다."


    # 면접 데이터 분리
    if interview_data:
        formatted_data = []
        for idx, entry in enumerate(interview_data):
            formatted_data.append(f"질문 {idx+1}: {entry['ques_text']}\n사용자 답변: {entry['answer_user_text']}\n답변 시간: {entry['answer_end_time']}")

        dataset = '\n\n'.join(formatted_data)
    else:
        return "면접 데이터가 존재하지 않습니다."

    user_query = '\n'.join(user_query)

    # 프롬프트
    prompt = ChatPromptTemplate.from_template(
        """
        당신은 AI 면접 평가자입니다.

        순서대로 면접 평가를 진행하세요.
        각 질문에 대한 권장답변을 생성하고, 각 답변에 대한 평가를 진행하세요.
        질문이 10개라면, 10개의 평가가 생성되어야 합니다.

        ** 권장답변 생성**:
        1. 아래의 [면접 데이터]에서 질문과 사용자 답변을 참고하여 [권장답변 생성규칙]에 따라 먼저 **권장 답변**을 생성하세요.  
        2. 사용자 답변과 권장 답변을 비교하여 각 항목에 대해 자연스러운 문장형 피드백을 작성해주세요.  
        3. 점수는 매기지 말고, 실제 면접관이 해주는 것처럼 진정성 있고 친절하게 작성해주세요.
        
        **면접 답변 평가**:
        1. 아래의 [면접 데이터]에서 질문을 읽고, 질문의 **의도**를 파악한 뒤
        2. [평가 항목] 중에서 질문의 의도에 **적합한 항목을 찾아** 사용자 답변을 평가해주세요.
        3. 사용자 답변에서 사용자의 강약점을 파악하여 평가하세요.
        4. 최종적으로 아래 형식을 참고하여, 각 항목별로 평가를 작성해주세요.
        5. 평가는 [면접 데이터]의 각 사용자 답변에 대해 진행하세요.

        면접자의 [지원정보]를 분석하여 **지원 직무** 및 **지원 계열**을 판단한 뒤, 해당 계열에 해당하는 규칙을 적용해야 합니다.

        ---
        [지원정보]
        {user_query}

        계열 구분은 다음과 같습니다:
        - 인문 계열: {ev_hum_prompt}
        - 공학 계열: {ev_eng_prompt}
        - 예체능 계열: {ev_arts_prompt}

        면접자의 [지원자료]를 분석해 사용자 직무, 기술/역량, 프로젝트를 파악하고, 권장답변 생성 및 답변평가 시 참고하세요.
        지원자료에서 이름을 찾고, 답변 생성시 사용자를 이름으로 지칭하세요.

        [지원자료]
        - **이력서**  
        {resume}

        - **자기소개서**  
        {cover_letter}

        - **포트폴리오**  
        {portfolio}
        ---

        [면접 데이터]
        각 면접 질문에 대한 사용자 답변을 평가해 주세요.:\n\n
        {dataset}
        ---

        [권장답변 생성규칙]
        1. <지원정보>에서 면접자의 희망 기업, 직무, 경력을 파악해 권장답변 생성에 참고하세요.
        2. 질문에서 의도를 파악해 의도에 부합하는 답변을 생성하세요.
        3. 답변은 <지원정보>와 관련이 있어야 하고, 문장이 논리적이어야 합니다.
        4.(상황 → 행동 → 결과)로 답변 흐름이 자연스럽게 작성하세요.
        5. 직업명은 보편적으로 사용하는 명칭을 사용하세요.

        ---
        [평가 항목]
        {ev_list}

        [평가 방식]  
        - 각 답변에 대한 평가 진행
        - 각 항목에 대해 200자 이하의 간결한 문장으로 피드백 작성
        - 면접자의 성향, 강약점을 판단해 면접자가 인식할 수 있도록 작성
        ---

        [출력 형식 예시]
        다음 형식의 JSON으로 응답해주세요:
        용어의 의미를 참고해서 알맞게 출력해주세요.
        - answer_example_text: 권장답변
        - feedback: 피드백
        - answer_logic : 논리성
        - q_comp : 질문 이해도
        - job_exp : 직무 전문성
        - hab_chk : 표현 습관
        - time_mgmt : 시간 활용력
        - answer_all_review : 총평

        {{
        "1": {{
            "answer_example_text": "...",
            "feedback": {{
                "answer_logic": "...",
                "q_comp": "...",
                "job_exp": "...",
                "hab_chk": "...",
                "time_mgmt": "..."
            }},
            "answer_all_review": "..."
            }},
        "2:" {{
            "answer_example_text": "...",
            "feedback": {{
                "answer_logic": "...",
                "q_comp": "...",
                "job_exp": "...",
                "hab_chk": "...",
                "time_mgmt": "..."
            }},
            "answer_all_review": "..."
            }},
        ...
        }}
        ※ 전체 구조가 JSON으로 유효하게 닫히도록 작성해주세요.

        """
    )

    # output parser
    output_parser = JsonOutputParser()

    # 체인 생성
    chain = prompt | llm | output_parser

    # 요청
    response = chain.invoke({
        'user_query': user_query,
        'ev_hum_prompt': ev_hum_prompt,
        'ev_eng_prompt': ev_eng_prompt,
        'ev_arts_prompt': ev_arts_prompt,
        'resume': resume,
        'cover_letter': cover_letter,
        'portfolio': portfolio,
        'dataset': dataset,
        'ev_list': ev_list
    })

    return response

# 생성된 평가 및 권장답변 RDB 저장
def save_generated_evals(response):
    # 권장 답변 저장

    # 피드백 저장

    # 총평 저장
    pass


# if __name__ == '__main__':
#     appli_mats = get_application_mats('interview')
#     interview_data = get_interview_data('interview')

#     company_name = '네이버'
#     job_name = 'IT/개발/데이터'
#     experience = '신입'

#     user_queries = [company_name, job_name, experience]

#     results = evaluate_answers(interview_data, appli_mats, user_queries)

#     print(interview_data)
