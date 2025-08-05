import sys
sys.path.append('../mattlib')
from mattlib.BaseAPI import BaseAPI
import requests
import os
import json
import time

# Authorization must contain fields:
#    type
#    domain
#    consumer-key
#    consumer-secret
#    username
#    password

class SalesForceAPI(BaseAPI):
    required_info = [
        ("domain", "str"),
        ("consumer_key", "str"),
        ("consumer_secret", "str"),
    ]
        
    def connect(self, domain, consumer_key, consumer_secret):
        self.domain = domain.rstrip()
        self.consumer_key = consumer_key.rstrip()
        self.consumer_secret = consumer_secret.rstrip()
        self.url = f'https://{self.domain}.my.salesforce.com'
        self.__get_auth_user()

    def __get_auth_user(self):
        auth = {
            'grant_type': 'client_credentials',
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
        }
        url = f'{self.url}/services/oauth2/token'
        response = requests.post(url, data=auth)
        token = response.json().get('access_token')
        if token != None:
            self.headers = {'Authorization': f'Bearer {token}'}
            response = self.methods()[0]['method']()
            if type(response) == dict:
                if 'error' in response.keys():
                    raise Exception(f"SalesForceAPI authentication failed.\n "\
                    f"Response: {response}")
            return 
        else:
            raise Exception(f"SalesForceAPI authentication failed.\n "\
                  f"Response: {response.text}")

    def user(self, fields=None):
        if not fields:
            fields = [
                'Id', 'FirstName', 
                'LastName', 'Username', 'Email',
                'IsActive', 'LastLoginDate',
                'UserType', 'ProfileId'
            ]
        fields = ',+'.join(fields)
        query = f'SELECT+{fields}+from+User'
        request_url = f'{self.url}/services/data/v53.0/query?q={query}'
        response = self.call_api(request_url)
        return response

    def profile(self, fields=None):
        if not fields:
            fields = [
                'Id', 'Name', 'UserLicenseId'
            ]
        fields = ',+'.join(fields)
        query = f'SELECT+{fields}+from+Profile'
        request_url = f'{self.url}/services/data/v53.0/query?q={query}'
        response = self.call_api(request_url)
        return response

    def permission_set_license(self, fields=None):
        if not fields:
            fields = [
                'Id', 'PermissionSetLicenseKey', 'DeveloperName', 'MasterLabel', 'TotalLicenses',
                'UsedLicenses', 'Status'
            ]
        fields = ',+'.join(fields)
        query = f'SELECT+{fields}+from+PermissionSetLicense'
        request_url = f'{self.url}/services/data/v53.0/query?q={query}'
        response = self.call_api(request_url)
        return response

    def tenant_usage_entitlement(self, fields=None):
        if not fields:
            fields = [
                'Setting', 'MasterLabel', 'AmountUsed', 'CurrentAmountAllowed', 'Frequency', 
                'IsPersistentResource', 'UsageDate', 'StartDate','EndDate'
            ]
        fields = ',+'.join(fields)
        query = f'SELECT+{fields}+from+TenantUsageEntitlement'
        request_url = f'{self.url}/services/data/v53.0/query?q={query}'
        response = self.call_api(request_url)
        return response

    def active_feature_license_metric(self, fields=None):
        if not fields:
            fields = [
                'ActiveUserCount', 'AssignedUserCount', 'FeatureType',
                'MetricsDate', 'TotalLicenseCount'
            ]
        fields = ',+'.join(fields)
        query = f'SELECT+{fields}+from+ActiveFeatureLicenseMetric'
        request_url = f'{self.url}/services/data/v53.0/query?q={query}'
        response = self.call_api(request_url)
        return response
    
    def user_license(self, fields=None):
        if not fields:
            fields = [
                'Id', 'LicenseDefinitionKey', 'Name', 'MasterLabel',
                'TotalLicenses', 'UsedLicenses', 'Status', 
            ]
        fields = ',+'.join(fields)
        query = f'SELECT+{fields}+from+UserLicense'
        request_url = f'{self.url}/services/data/v53.0/query?q={query}'
        response = self.call_api(request_url)
        return response

    def login_history(self, fields=None):
        if not fields:
            fields = [
                'Id','LoginTime','Status','Application','LoginType','UserId'
            ]
        fields = ',+'.join(fields)
        query = f'SELECT+{fields}+from+LoginHistory'
        request_url = f'{self.url}/services/data/v53.0/query?q={query}'
        response = self.call_api(request_url)
        return response

    def permission_set_license_assign(self, fields=None):
        if not fields:
            fields = [
                'Id', 'AssigneeId', 'PermissionSetLicenseId', 'IsDeleted', 'CreatedDate', 'CreatedById', 
                'LastModifiedDate', 'LastModifiedById', 'SystemModstamp' 
            ]
        fields = ',+'.join(fields)
        query = f'SELECT+{fields}+from+PermissionSetLicenseAssign'
        request_url = f'{self.url}/services/data/v53.0/query?q={query}'
        response = self.call_api(request_url)
        return response
           

    def call_api(self, url):
        values = []
        i = 0
        max_retrive = 5
        while url != None:
            retrive = 0
            try:
                response = requests.get(url, headers=self.headers)
                status = response.status_code
                response_text = json.loads(response.text)
                if status == 429:
                    retry_time = response.headers.get('Retry-After')
                    if retry_time:
                        time.sleep(int(retry_time))
                    else:
                        while retrive<max_retrive and status==429:
                            time.sleep(30*retry_time)
                            response = requests.get(url, headers=self.headers)
                            status = response.status_code
                            response_text = json.loads(response.text)
                            retrive = retrive+1
                if status != 200:
                    return {'error':response_text}
            except Exception as e:
                return {'error':e}

            values += response_text['records']
            if 'nextRecordsUrl' in response_text.keys():
                url_aux = response_text['nextRecordsUrl']
                url = f'{self.url}{url_aux}'
            else:
                url = None
        return values

    def methods(self):
        methods = [
            {
                'method_name': 'user',
                'method': self.user,
                'format': 'json'
            },
            {
                'method_name': 'profile',
                'method': self.profile,
                'format': 'json'
            },
            {
                'method_name': 'permission_set_license',
                'method': self.permission_set_license,
                'format': 'json'
            },
            {
                'method_name': 'tenant_usage_entitlement',
                'method': self.tenant_usage_entitlement,
                'format': 'json'
            },
            {
                'method_name': 'active_feature_license_metric',
                'method': self.active_feature_license_metric,
                'format': 'json'
            },
            {
                'method_name': 'user_license',
                'method': self.user_license,
                'format': 'json'
            },
            {
                'method_name': 'login_history',
                'method': self.login_history,
                'format': 'json'
            },
            {
                'method_name': 'permission_set_license_assign',
                'method': self.permission_set_license_assign,
                'format': 'json'
            },
        ]
        return methods
