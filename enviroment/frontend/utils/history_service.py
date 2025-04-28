from utils.backend import Backend

class History_service(Backend):
    def __init__(self):
        super().__init__()
    
    def get_history_list(self, data:dict, headers):
        URL = '/mock/his/get_history'
        result = self.req_post(URL, data, headers)
        return result


    def get_history_report(self, data:dict, headers):
        URL = '/mock/his/get_report'
        result = self.req_post(URL, data, headers)
        return result

    def update_history_memo(self, data:dict, headers):
        URL = '/mock/his/update_interview_memo'
        self.req_put(URL, data, headers)
