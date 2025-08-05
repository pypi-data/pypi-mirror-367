from urllib.parse import urlencode,quote
import sys
sys.path.append('../mattlib')
from mattlib.BaseAPI import BaseAPI
import requests
import json
import base64
import time
import jwt

class AdobeAPI(BaseAPI):
    required_info = [
        ("client_ID", "str"),
        ("client_secret", "str"),
        ("organization_ID", "str"),
        ("tech_acc_id","str"),
        ("key","str")

    ]

    def connect(self, client_ID, client_secret, key, organization_ID, tech_acc_id):
        self.organization_ID = organization_ID.rstrip()
        self.client_ID = client_ID.rstrip()
        self.client_secret = client_secret.rstrip()
        self.key = key.rstrip()
        self.tech_acc_id = tech_acc_id.rstrip()
        self.jwt_token = self.create_jwt()
        self.headers = self.__get_auth_user()
    
    def create_jwt(self):
        current_sec_time = int(round(time.time()))
        expiry_time = current_sec_time + (60*60*24)
        ims_server = "ims-na1.adobelogin.com"
        payload = {
            "exp" : expiry_time,
            "iss" : self.organization_ID,
            "sub" : self.tech_acc_id,
            "aud" : "https://" + ims_server + "/c/" + self.client_ID    ,
            "https://" + ims_server + "/s/ent_user_sdk" : True
        }
        self.jwt_token = jwt.encode(payload, self.key, algorithm="RS256")
        return self.jwt_token

    def __get_auth_user(self):   
        ims_server = "ims-na1.adobelogin.com" 
        url = f'https://{ims_server}/ims/exchange/jwt/'

        payload = {
            'client_id': self.client_ID,
            'client_secret': self.client_secret,
            'jwt_token': self.jwt_token
        }

        response = requests.post(url, data=payload)
        token = response.json().get('access_token')
        if token != None:
            headers = {
                'Authorization': 'Bearer ' + token,
                'X-Api-Key': self.client_ID,
                "x-gw-ims-org-id": self.organization_ID,
                "Content-Type": "application/json"  
            }
            return headers
        else:
            raise Exception(f'Adobe authentication failed.\n'\
                            f'Response: {response}')
    def list_users(self):
        url = f'https://usermanagement.adobe.io/v2/usermanagement/users/' + self.organization_ID
        response = self.call_api(url)
        response = [item for sublist in (d['users'] for d in response) for item in sublist]

        return response

    def list_groups(self):
        url = f'https://usermanagement.adobe.io/v2/usermanagement/groups/' + self.organization_ID 
        response = self.call_api(url)
        response = [item for sublist in (d['groups'] for d in response) for item in sublist]
        return response
    
    def call_api(self, url):
        page = 0
        max_retrive=5
        value = []
        next=True

        while next:
            retrive=0
            response = requests.get(url+'/'+str(page), headers=self.headers)
            status = response.status_code
            if status == 429:
                if 'Retry-After' in response.headers.keys():
                    retry_time = response.headers.get('Retry-After')
                    time.sleep(int(retry_time))
                else:
                    while retrive<max_retrive and status==429:
                        time.sleep(30*(retrive+1))
                        response = requests.get(url+'/'+page, headers=self.headers)
                        status = response.status_code
                        retrive = retrive+1
            if status != 200:
                return {'error':response.text}

            response = json.loads(response.text)
            if response['lastPage']:
                next=False

            page = page+1
            value.append(response)
        return value

    def methods(self):
        methods = [
            {
                'method_name': 'list_users',
                'method': self.list_users,
                'format': 'json'
            },
            {
                'method_name': 'list_groups',
                'method': self.list_groups,
                'format': 'json'
            },
        ]
        return methods
