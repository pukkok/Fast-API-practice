from fastapi import FastAPI
import uvicorn # ? 서버 실행 도구

from app.routers import mogodb_router # ? 데이터베이스 라우터

# ? MongoDB 비동기 클라이언트 
from motor.motor_asyncio import AsyncIOMotorClient

from config import config

import os


# * fastapi의 app.on_event를 더이상 사용하지 않는다.
# ? lifespan 함수를 만들기 위해 사용
# todo : asynccontextmanager 데코레이터를 사용해 앱의 생명 주기를 관리
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("앱 시작: MongoDB 연결 설정 중...")
    try:
        app.mongodb_client = AsyncIOMotorClient(config["MONGODB_URI"])
        app.mongodb = app.mongodb_client["holiday_db"]
        print("MongoDB 연결 성공")
    except Exception as e:
        print(f"MongoDB 연결 실패: {e}")
        raise e
    
    yield
    
    print("앱 종료: MongoDB 연결 해제 중...")
    app.mongodb_client.close()
    print("MongoDB 연결 해제 완료")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message" : "서버 접속 성공"}

@app.get('/db-test')
async def db_test():
    data = os.getenv("MONGODB_URI")
    return {"result" : data}

app.include_router(mogodb_router.router, prefix="/mongo", tags=["mongoDB"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# 서버 실행은 다음 명령어로 실행
# * uvicorn app.main:app --reload <- 고정된 포트 8000
# * uvicorn app.main:app --port 8080 --reload 내가 원하는 설정으로 열기