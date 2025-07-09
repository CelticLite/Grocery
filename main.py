import pickle
import secrets
import base64
import logging
import random, string
from typing import Annotated
from fastapi import Depends, FastAPI, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Model(BaseModel):
    model: bytes

class SubmitResponse(BaseModel):
	modelId: int


app = FastAPI()
security = HTTPBasic()
models = {}
users = []
passwords = {}

def randomword(length):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))


def login(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
	current_password_bytes = credentials.password.encode("utf8")
	try:
		correct_password_bytes = bytes(passwords[credentials.username].encode('utf-8'))
	except Exception as err:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username",
			headers={"WWW-Authenticate": "Basic"},
		)
	is_correct_password = secrets.compare_digest(
		current_password_bytes, correct_password_bytes
	)
	if not is_correct_password:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect password",
			headers={"WWW-Authenticate": "Basic"},
		)
	return True


@app.get("/")
async def root():
	return {"message": "Hello, I am a machine learning model storage and quick retrieval system."}


@app.get("/info")
async def info():
	message = "This service provides a convenient storage system for machine learning models. \
				You can safely store your trained models here for future retrieval from any other \
				device. Using this service takes the hassel out of transfering trained models from \
				your training environment to production! Just upload your models to the submit endpoint \
				and you will be able to access it at any time! You can retrieve your model at the \
				/models/MODEL_ID endpoint."
	return {"message": message}

@app.get("/user")
async def user(request: Request):
	username = randomword(8)
	password = randomword(12)
	users.append(username)
	passwords[username] = password
	models[request.client.host] = []
	return {"username":username,"password":password}

@app.post("/models", status_code=201, response_model=SubmitResponse)
async def submit(request: Request, login_status: Annotated[bool, Depends(login)]):
	'''
	Submit: reads in models from body of request in pickle format
	returns: model_id. The location in the models array to retrieve the desired model. 
	'''
	req_body = await request.body()
	user = request.client.host
	if login_status:
		try:
			model_read = pickle.loads(base64.urlsafe_b64decode(req_body))
		except Exception as e:
			logging.warning("failed to pickle model")
			return {"modelId": -1}
		models[user].append(model_read)
		model_id = str(len(models[user]) - 1)
		return {"modelId": model_id}
	return {"modelId": -1}

@app.get("/models/{user}/{model_id}")
async def info(model_id: int, user: str, request: Request, login_status: Annotated[bool, Depends(login)]):
	data = b''
	if login_status:
		try:
			data = pickle.dumps(models[user][model])
		except Exception as e:
			return {'data':data,"message":'model does not exist'}
	return {'data':data, "message": 'Here is your model'}