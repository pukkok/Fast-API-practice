from fastapi import FastAPI
import uvicorn
from app.routers import mogodb_router
from motor.motor_asyncio import AsyncIOMotorClient
from config import config
import sys
import io
from contextlib import asynccontextmanager

# 출력 스트림을 UTF-8로 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("앱 시작: MongoDB 연결 설정 중...")
    try:
        # MongoDB 연결 시도
        app.mongodb_client = AsyncIOMotorClient(config["MONGODB_URI"])

        # MongoDB 연결 상태 확인
        # ping() 명령을 통해 연결 상태를 점검
        try:
            await app.mongodb_client.admin.command('ping')
            print("MongoDB 연결 성공")
        except Exception as e:
            print(f"MongoDB 연결 실패: {e}")
            raise e
        
        # DB 연결 객체
        app.mongodb = app.mongodb_client["holiday_db"]
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
    return {"message": "서버 접속 성공"}

# MongoDB 라우터 포함
app.include_router(mogodb_router.router, prefix="/mongo", tags=["mongoDB"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
