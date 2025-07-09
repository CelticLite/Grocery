# Grocery 

A minimal FastAPI service that allows users to **store** and **retrieve** pickled machine learning models via a simple HTTP API. This system is ideal for transporting trained models between environments (e.g., from training to production) in a lightweight, credential-secured fashion.


#### WARNING: This is a vulnerable API for machine learning model storage and retrieval. This API is intended ONLY for demo purposes to show vulnerabilities in Python Pickle serialization. 

---

## Features

* Secure access using HTTP Basic Auth
* Per-user model storage
* Model submission with Base64-encoded pickled objects
* Retrieval of stored models by user and model ID
* Random user credentials for quick prototyping

---

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


---

## API Endpoints

### `GET /`

Returns a simple welcome message.

```json
{
  "message": "Hello, I am a machine learning model storage and quick retrieval system."
}
```

---

### `GET /info`

Provides a description of the service and how to use it.

---

### `GET /user`

Generates a random username and password for accessing the model submission and retrieval endpoints. Each client IP gets a separate storage pool.

**Response:**

```json
{
  "username": "abcxyz12",
  "password": "supersecurepw"
}
```

---

### `POST /models`

Uploads a pickled model using a Base64-encoded request body.

**Headers:**

* Basic Auth credentials

**Request Body:**
Raw binary (Base64-encoded) pickled model.

**Response:**

```json
{
  "modelId": 0
}
```

---

### `GET /models/{user}/{model_id}`

Downloads a pickled model given the user and model ID.

**Headers:**

* Basic Auth credentials

**Response:**

```json
{
  "data": "<binary data>",
  "message": "Here is your model"
}
```

---

## Authentication

All model submission and retrieval endpoints are protected using HTTP Basic Auth. Use the credentials obtained from `/user`.

---

## Security Warning

* **Do not expose this service publicly without further hardening.**
* Pickle format is **inherently unsafe**. Only use this API in secure, trusted environments for demo purposes only.
* This demo is not suitable for production without additional encryption, authentication, and validation layers.

---

## Example Usage with Python

### Submit Model

```python
import pickle, base64, requests

model = {"weights": [1, 2, 3]}  # Example model
data = base64.urlsafe_b64encode(pickle.dumps(model))

r = requests.post("http://localhost:8000/models", data=data,
    auth=("your_username", "your_password"))
print(r.json())
```

### Retrieve Model

```python
r = requests.get("http://localhost:8000/models/your_username/0",
    auth=("your_username", "your_password"))
model = pickle.loads(r.json()["data"])
print(model)
```

## Exploitation 

Full instructions can be found in `writeup.md`