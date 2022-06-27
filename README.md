# Quiz Builder API

This is a simple RESTful quiz builder web API.

### Create and activate a virtual environment:

Linux:
```
python -m venv venv && source venv/bin/activate
```

Windows:
```
python -m venv venv && venv\Scripts\activate
```


### Install the requirements:
```
(venv)$ pip install -r requirements.txt
```

### Create a .env in the project folder

```
SECRET_KEY = "generate yours with: openssl rand -hex 32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Run
```
python main.py
```

### Documentation

http://localhost:8081/docs