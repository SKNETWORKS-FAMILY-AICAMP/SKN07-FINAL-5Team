from pydantic import BaseModel

class HisBoardSchema(BaseModel):
    user_id:str 
    page_num:int

class HisReportSchema(BaseModel):
    interview_id:int

class HisMemoSchema(BaseModel):
    interview_id:int
    memo:str

