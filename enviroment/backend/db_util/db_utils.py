#from dotenv import load_dotenv
#import os
#import psycopg2
#
#load_dotenv() # dotenv_path='../.env'
#
#class post_db_connect():
#    def __init__(self):
#        db_host = os.environ.get('POST_DB_HOST')
#        db_name = os.environ.get('POST_DB_NAME')
#        db_user = os.environ.get('POST_DB_USER')
#        db_passwd = os.environ.get('POST_DB_PASSWD')
#        db_port = os.environ.get('POST_DB_PORT')
#
#        self.db = psycopg2.connect(host=db_host, dbname=db_name,user=db_user,password=db_passwd,port=db_port)
#        self.cursor = self.db.cursor()
#
#    def select_one(self, query: str):
#        self.cursor.execute(query)
#        return self.cursor.fetchone()
#
#    def select_many(self, query: str, num: int):
#        self.cursor.execute(query)
#        return self.cursor.fetchmany(num)
#
#    def select_all(self, query: str):
#        self.cursor.execute(query)
#        return self.cursor.fetchmall()
#    
#    def excute_crud(self, query: str):
#        result = self.cursor.execute(query)
#        self.db.commit()
#        return result
#    
#    def close(self):
#        self.cursor.close()
#        self.db.close()