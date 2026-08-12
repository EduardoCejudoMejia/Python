from fastapi import FastAPI, Form
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth_schema = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
def loggin(username=Form(), password=Form()):
    return "token"


# uvicorn main:app --reload
