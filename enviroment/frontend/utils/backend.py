import requests
from dotenv import load_dotenv
import os

class Backend:
    def __init__(self):
        load_dotenv()
        self.API_URL = os.environ.get('API_URL')
        
    def req_get(self, URL,**headers):
        try:
            res = None
            if headers:
                res = requests.get(url=self.API_URL+URL, headers=headers)
            else:
                res = requests.get(url=self.API_URL+URL)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            return {'message': str(e), 'status_code': getattr(e.response, 'status_code', 'unknown')}
        
    
    def req_post(self, URL:str, data:dict, headers:dict):
        try:
            res = None
            if headers:
                res = requests.post(url=self.API_URL+URL, json=data,headers=headers)
            else:
                res = requests.post(url=self.API_URL+URL, data=data)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            return {'message': str(e), 'status_code': getattr(e.response, 'status_code', 'unknown')}


    def req_put(self, URL:str, data:dict, headers:dict):
        try:
            res = None
            if headers:
                res = requests.put(url=self.API_URL+URL, json=data,headers=headers)
            else:
                res = requests.put(url=self.API_URL+URL, data=data)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            return {'message': str(e), 'status_code': getattr(e.response, 'status_code', 'unknown')}
