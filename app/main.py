from fastapi import FastAPI
from app.routers import test_router
from config import config
import uvicorn
import requests

app = FastAPI()

GET_POINT = '/getRestDeInfo'
DEFAULT_QUERY = '?_type=json'

@app.get("/")
async def root():
    return {"message" : "서버 접속 성공"}

@app.get('/rest-day-info')
async def rest_holiday():
    url = f'{config["BASE_URL"]}{GET_POINT}{DEFAULT_QUERY}&solYear=2024&numOfRows=30&ServiceKey={config["SECRET_KEY"]}'
    data = requests.get(url)
    return {"data" : data.json()}

 
app.include_router(test_router.router, prefix='/test', tags=["test"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# 서버 실행은 다음 명령어로 실행
# uvicorn app.main:app --reload