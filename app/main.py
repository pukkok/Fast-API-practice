from fastapi import FastAPI
import uvicorn # ? 서버 실행 도구

from app.routers import test_router # ? test 라우터
from app.routers import rest_day_info_router # ? 공휴일 불러오기 라우터

# ? MongoDB 비동기 클라이언트 
from motor.motor_asyncio import AsyncIOMotorClient

# * fastapi의 app.on_event를 더이상 사용하지 않는다.
# ? lifespan 함수를 만들기 위해 사용
# todo : asynccontextmanager 데코레이터를 사용해 앱의 생명 주기를 관리
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 실행되는 코드 (startup 대체)
    print("앱 시작: MongoDB 연결 설정 중...")
    app.mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
    app.mongodb = app.mongodb_client["python-db"]  # 사용할 데이터베이스 선택
    print("MongoDB 연결 성공")

    yield  # * 애플리케이션 실행

    # 앱 종료 시 실행되는 코드 (shutdown 대체)
    print("앱 종료: MongoDB 연결 해제 중...")
    app.mongodb_client.close()
    print("MongoDB 연결 해제 완료")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message" : "서버 접속 성공"}

# ? app에 prefix로 엔드포인트를 설정하여 router를 불러올 수 있다. 
app.include_router(test_router.router, prefix='/test', tags=["test"])
app.include_router(rest_day_info_router.router, prefix='/api', tags=["holiday"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# 서버 실행은 다음 명령어로 실행
# * uvicorn app.main:app --reload <- 고정된 포트 8000
# * uvicorn app.main:app --port 8080 --reload 내가 원하는 설정으로 열기