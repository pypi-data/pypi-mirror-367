import sys
sys.path.append('../mattlib')
from mattlib.BaseAPI import BaseAPI
import requests
import os
import json
import pathlib
import time

class BaseMicrosoftAPI(BaseAPI):
    required_info = [
        ("tenant_ID", "str"),
        ("app_ID", "str"),
        ("secret_key", "str")
    ]
    def connect(self, tenant_ID, app_ID, secret_key, scope):
        self.tenant_ID = tenant_ID.rstrip()
        self.app_ID = app_ID.rstrip()
        self.secret_key = secret_key.rstrip()
        self.scope = scope
        self.headers = self.get_auth()

    def get_auth(self):
        token_url = f'https://login.microsoftonline.com/'\
                    f'{self.tenant_ID}/oauth2/v2.0/token'
        auth = {
            'grant_type': 'client_credentials',
            'client_id': self.app_ID,
            'client_secret': self.secret_key,
            'scope': self.scope,
        }
        response = requests.post(token_url, data=auth)
        token = response.json().get('access_token')
        if token != None:
            headers = {'Authorization': f'Bearer {token}'}
            return headers
        else:
            raise Exception(f' BaseMicrosoftAPI authentication failed.\n'\
                            f'Response: {response.json()}')

    def call_api_stream(self, url):
        response = requests.get(url, headers=self.headers)
        return response.text

    # def call_api(self, url, params=None, ignore=None):
    #     values = []
    #     max_retrive=5
    #     while url != None:
    #         retrive=0
    #         response = requests.get(url, headers=self.headers, params=params if params is not None else {})
    #         status = response.status_code
    #         if status == 429:
    #             if 'Retry-After' in response.headers.keys():
    #                 retry_time = response.headers.get('Retry-After')
    #                 time.sleep(int(retry_time))
    #             else:
    #                 while retrive<max_retrive and status==429:
    #                     time.sleep(30*(retrive+1))
    #                     response = requests.get(url, headers=self.headers, params=params if params is not None else {})
    #                     status = response.status_code
    #                     retrive = retrive+1
    #         if status != 200:
    #             return {'error':response.text}
    #         response = json.loads(response.text)
    #         values += response['value']
    #         if ignore == True:
    #             return values
    #         else:
    #             if 'nextLink' in response.keys():
    #                 params = {}
    #                 url = response['nextLink']
    #             if '@odata.nextLink' in response.keys():
    #                 params = {}
    #                 url = response['@odata.nextLink']
    #             else :
    #                 url = None
    #     return values

    def call_api(self, url, params=None, ignore=None):
        values = []
        max_retries = 5  
        base_retry_delay = 5  
        
        while url is not None:  
            retry_count = 0  
            last_error = None
            
            while retry_count < max_retries:
                try:
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params=params if params is not None else {}
                    )
                    status = response.status_code

                    if status == 429:
                        retry_after = response.headers.get('Retry-After', base_retry_delay * (retry_count + 1))
                        wait_time = int(retry_after) if str(retry_after).isdigit() else base_retry_delay * (retry_count + 1)
                        print(f"Rate limited. Waiting {wait_time} seconds (attempt {retry_count + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        retry_count += 1
                        continue

                    if status != 200:
                        try:
                            error_data = response.json()
                            last_error = {'error': error_data}
                        except ValueError:
                            last_error = {'error': response.text}
                        break

                    try:
                        response_data = response.json()  
                        values.extend(response_data.get('value', []))  

                        if ignore:
                            return values

                        next_url = None
                        for link_key in ['nextLink', '@odata.nextLink']:
                            if link_key in response_data:
                                params = {}  
                                next_url = response_data[link_key]
                                break
                        
                        url = next_url
                        break 

                    except ValueError as e:
                        last_error = {'error': f'Invalid JSON response: {str(e)}'}
                        retry_count += 1
                        continue

                except requests.RequestException as e:
                    last_error = {'error': f'Request failed: {str(e)}'}
                    retry_count += 1
                    time.sleep(base_retry_delay * retry_count)
                    continue

            if retry_count >= max_retries and last_error is not None:
                return last_error

        return values
