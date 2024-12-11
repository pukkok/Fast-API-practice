from fastapi import FastAPI, Request
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
    return {"message": "서버 접속 성공"}

@app.get('/hi')
async def insa():
    return {"message": "안녕"}

@app.get("/test-db-connection")
async def test_db_connection(request: Request):

    try:
        collection = request.app.mongodb["holiday_db"]
        # 간단한 쿼리 실행
        test_document = await collection.find_one({"base_year": "2023"})
        if test_document:
            return {"msg": "MongoDB 연결 성공", "data": test_document}
        else:
            return {"error": "MongoDB 연결 성공, 하지만 데이터 없음"}
    except Exception as e:
        return {"error": f"MongoDB 연결 실패: {str(e)}"}

# MongoDB 라우터 포함
app.include_router(mogodb_router.router, prefix="/mongo", tags=["mongoDB"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
