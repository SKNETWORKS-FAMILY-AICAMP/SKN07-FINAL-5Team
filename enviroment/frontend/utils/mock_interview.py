from .backend import Backend


class Mock_interview(Backend):
    def __init__(self):
        super().__init__()
    
    def get_company_list(self):
        URL = '/mock/itv/get_company_list'
        result = self.req_get(URL)
        return result
    
    def get_job_list(self):
        URL = '/mock/itv/get_job_list'
        result = self.req_get(URL)
        return result
    
    def get_question_list(self, data:dict, headers):
        URL = '/mock/mng/get_question_list'
        result = self.req_post(URL, data, headers)
        return result

    def interview_start(self, data:dict , headers):
        URL = '/mock/itv/interview_start'
        result = self.req_post(URL, data, headers)
        return result

    def interview_result_process(self, data:dict, headers):
        URL = '/mock/itv/interview_result_process'
        result = self.req_post(URL, data, headers)
        return result
