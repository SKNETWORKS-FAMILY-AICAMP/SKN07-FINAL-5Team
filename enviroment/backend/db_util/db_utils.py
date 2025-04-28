from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv() # dotenv_path='../.env'

class post_db_connect():
    def __init__(self):
        db_host = os.environ.get('POST_DB_HOST')
        db_name = os.environ.get('POST_DB_NAME')
        db_user = os.environ.get('POST_DB_USER')
        db_passwd = os.environ.get('POST_DB_PASSWD')
        db_port = os.environ.get('POST_DB_PORT')

        self.db = psycopg2.connect(host=db_host, dbname=db_name,user=db_user,password=db_passwd,port=db_port, cursor_factory=RealDictCursor)
        self.cursor = self.db.cursor()

    def select_one(self, query: str):
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def select_many(self, query: str, num: int):
        self.cursor.execute(query)
        return self.cursor.fetchmany(num)

    def select_all(self, query: str):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def select_all_vars(self, query:str, conditions):
        # conditions에 int형 변수가 올 때, tuple로 변경
        # psycopg2의 cursor.execute(query, params)에서 params는 반드시 시퀀스 타입 (list, tuple) 이어야 함
        if not isinstance(conditions, (tuple, list)):
            conditions = (conditions,)
        self.cursor.execute(query, conditions)
        return self.cursor.fetchall()
    
    def select_many_vars(self, query:str, conditions, num: int):
        self.cursor.execute(query, conditions)
        return self.cursor.fetchmany(num)

    def insert_many_vars(self, query: str, conditions):
        self.cursor.execute(query, conditions)
        return self.db.commit()
    
    def excute_crud(self, query: str, conditions):
        result = None
        if conditions:
            result = self.cursor.execute(query, conditions)
        else:
            result = self.cursor.execute(query)
        
        self.db.commit()
        return result
    
    def close(self):
        self.cursor.close()
        self.db.close()