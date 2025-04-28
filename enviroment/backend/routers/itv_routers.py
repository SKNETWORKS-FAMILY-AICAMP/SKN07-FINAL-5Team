# 모의면접 Routers
import os
import sys
from fastapi import APIRouter

# --------- DIRECTORY PATH SETTING ----------
# # 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리 (/backend)
main_dir = os.path.abspath(os.path.join(current_dir, ".."))
if main_dir not in sys.path:
    sys.path.append(main_dir)

from db_util.db_utils import post_db_connect
from schemas.itv_process_schemas import ItvProcessSchema, ItvResultProcessSchema 
import re
from dotenv import load_dotenv
import openai
import os
import uuid 
from datetime import datetime
from evaluate_answer import get_application_mats, evaluate_answers 
import psycopg2.extras
from create_total_report import total_report


load_dotenv()
# OpenAI API 키 설정
openai.api_key = os.environ.get('OPENAI_API_KEY')


router = APIRouter(prefix="/itv")
common_select_text = {"선택해주세요":"None"}

@router.get('/get_company_list', status_code=200)
def get_company_list():
    connect = post_db_connect()
    result = connect.select_all("""select ccmt.common_id as common_id, 
                                          ccmt.common_nm as common_nm
                                   from company_code_master_tbl ccmt;""")
    connect.close()
    return common_select_process(result, 'common_nm', 'common_id', 'company_list')


@router.get('/get_job_list', status_code=200)
def get_job_list():
    connect = post_db_connect()
    result = connect.select_all("""select jcmt.common_id as common_id,
                                          jcmt.common_nm as common_nm
                                   from job_code_master_tbl jcmt;""")
    connect.close()
    return common_select_process(result, 'common_nm', 'common_id', 'job_list')


@router.post('/interview_start', status_code=200)
def interview_start(data: ItvProcessSchema):
    user_id = data.user_id
    question_list = data.question_list
    connect = post_db_connect()
    process_insert_query = """ insert into interview_process (user_id, company_nm  , kewdcdno, person_exp)
                       values (%s, %s, %s, %s)
                       returning interview_id;
                   """
    
    connect.cursor.execute(process_insert_query, (data.user_id, data.company_cd, data.job_cd, data.experience))
    
    interview_id = connect.cursor.fetchone()['interview_id']

    connect.db.commit()
    connect.close()

    
    parent_path = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
    now_time = datetime.now()

    
    join_path = f'data/audio/tts/{now_time.year}/{now_time.strftime("%m%d")}/'

    process_id = f'{uuid.uuid1().hex}_{interview_id}'

    root_path = os.path.join(parent_path, join_path)
    create_folder(root_path)
    create_question_tts(question_list, root_path, process_id)

    res_data = {'process_id':process_id,
                'q_list' : question_list,
                'audio_path' : join_path}

    return res_data


@router.post('/interview_result_process', status_code=200)
def interview_result_process(data: ItvResultProcessSchema):
    def null_and_exist_check(feedback_dict:dict, key:str):
        if key in feedback_dict:
            if feedback_dict[key] is None:
                return "null"
            else:
                return feedback_dict[key]
        else:
            return "null"
            
    status = ""        

    try:
        connect = post_db_connect()

        user_id_select_query = f""" select user_id 
                                    from interview_process
                                    where interview_id = '{data.interview_id}'
                                """
        
        user_info = connect.select_one(user_id_select_query)
        user_id = user_info['user_id'] 

        user_info_select_query = f"""with base_data as (
                                        select ip.company_nm ,
                                               ip.kewdcdno,
                                               ip.person_exp
                                        from interview_process ip 
                                        where ip.interview_id = '{data.interview_id}'
                                    ), select_company as (
                                        select bd.person_exp,
                                               bd.kewdcdno,
                                               ccmt.common_nm
                                        from base_data  as bd
                                        join  company_code_master_tbl ccmt  
                                        on cast(bd.company_nm as integer) = ccmt.common_id
                                    ), select_job as (
                                        select sc.common_nm as company_name,
                                                sc.person_exp,
                                                jcmt.common_nm as job_name
                                        from select_company as sc
                                        join job_code_master_tbl jcmt 
                                        on sc.kewdcdno = jcmt.common_id
                                    ) 
                                    select *
                                    from select_job;
                                """
        
        user_query_info = connect.select_one(user_info_select_query)

        mats = get_application_mats(user_id)
        
        question_list = data.question_list
        answer_list = data.answer_list
        user_query = [user_query_info['company_name'], user_query_info['job_name'], user_query_info['person_exp']]

        result_insert_query = f""" INSERT INTO interview_result (interview_id, ques_step, ques_text, answer_user_text, answer_example_text, answer_end_time, answer_all_review, answer_logic, q_comp, job_exp, hab_chk, time_mgmt )
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                               """
        eval_insert_list = []
        report_data = []
        
        eval_input_data = [{'ques_text' : question, 'answer_user_text' : answer_list[idx], 'answer_end_time': 90} for idx, question in enumerate(question_list)]


        eval_list = evaluate_answers(eval_input_data ,mats, user_query)
        

        for eval_num in eval_list.keys():
            idx = (int(eval_num) - 1)
            eval_result = eval_list[eval_num]
            feedback = eval_result['feedback']
            answer_logic = null_and_exist_check(feedback, 'answer_logic')
            q_comp = null_and_exist_check(feedback, 'q_comp')
            job_exp = null_and_exist_check(feedback, 'job_exp')
            hab_chk = null_and_exist_check(feedback, 'hab_chk')
            time_mgmt = null_and_exist_check(feedback, 'time_mgmt')
            answer_all_review = eval_result['answer_all_review']    
        
            eval_data = tuple([data.interview_id, eval_num, question_list[idx], answer_list[idx], eval_result['answer_example_text'], 90, answer_all_review, answer_logic, q_comp, job_exp, hab_chk, time_mgmt])
            
            eval_insert_list.append(eval_data)
            
            review_data = {'answer_logic' : answer_logic,
                           'q_comp' : q_comp,
                           'job_exp' : job_exp,
                           'hab_chk' : hab_chk,
                           'time_mgmt' : time_mgmt,
                           'answer_all_review' : answer_all_review
                          }
            report_data.append(review_data)
            

        for result_data in eval_insert_list:
            connect.cursor.execute(result_insert_query, result_data)
       

        connect.db.commit()

        total_report_data = total_report(report_data)
        
        report_insert_query = f""" INSERT INTO  INTERVIEW_REPORT
                                   VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                               """
        
        report_insert_data = tuple([data.interview_id, total_report_data['answer_all_review'], \
                                   total_report_data['score']['qs_relevance'], total_report_data['score']['clarity'], \
                                   total_report_data['score']['job_relevance'], total_report_data['answer_logic'], \
                                   total_report_data['q_comp'], total_report_data['hab_chk'], total_report_data['job_exp'], \
                                   total_report_data['time_mgmt'], ''])

        connect.cursor.execute(report_insert_query, report_insert_data)

        connect.db.commit()

    except Exception as e:
        print(e)
        status = "error"
    finally:
        connect.close()
        status = "ok"

    res_data = {"status" : status}
    return res_data



def common_select_process(select_list:dict, key:str, value: str, list_nm: str):
    select_box = common_select_text.copy()
    sum_dict = {i[key] : i[value] for i in select_list}
    select_box.update(sum_dict)
    del sum_dict
    return {list_nm: select_box, 'labels': list(select_box.keys())}

def get_question_text_convert(question: str):
    p1 = re.compile('[^0-9\.][0-9a-zA-Z가-힣\.,?]+')
    q_list = question.split('\n\n')
    q_split_list = [''.join(p1.findall(i.split('\n')[0])).lstrip() for i in q_list]
    return { 'q_list' : q_list , 'q_split_list' : q_split_list }


def create_question_tts(q_list: list, root_path:str, file_nm:str):
    client = openai.OpenAI()
   
    for idx, q in enumerate(q_list):
        response = client.audio.speech.create(
            model="tts-1",
            input=q,
            voice="alloy",
            response_format="mp3",
            speed=1.0,
        )

        file_root = f'{root_path}{file_nm}_{idx}.mp3'
        response.write_to_file(file_root)
    

def create_folder(path:str):
    if os.path.exists(path) == False:
        os.makedirs(path)