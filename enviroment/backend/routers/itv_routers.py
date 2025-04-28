# 모의면접 Routers
from fastapi import APIRouter
from db_util.db_utils import post_db_connect

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
def get_company_list():
    connect = post_db_connect()
    result = connect.select_all("""select jcmt.common_id as common_id,
                                          jcmt.common_nm as common_nm
                                   from job_code_master_tbl jcmt;""")
    connect.close()
    return common_select_process(result, 'common_nm', 'common_id', 'job_list')

def common_select_process(select_list:dict, key:str, value: str, list_nm: str):
    select_box = common_select_text.copy()
    sum_dict = {i[key] : i[value] for i in select_list}
    select_box.update(sum_dict)
    del sum_dict
    return {list_nm: select_box, 'labels': list(select_box.keys())}
