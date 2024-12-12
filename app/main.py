from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn
import httpx
from config import Config
from motor.motor_asyncio import AsyncIOMotorClient
from app.lib.get_api_url import get_api_url
from datetime import datetime

# MongoDB Initialization
class MongoDB:
    client = None
    db = None

# * fastapi의 app.on_event를 더이상 사용하지 않는다.
# ? lifespan 함수를 만들기 위해 사용
# todo : asynccontextmanager 데코레이터를 사용해 앱의 생명 주기를 관리
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mongo = MongoDB()
    print("앱 시작: MongoDB 연결 설정 중...")
    try:
        app.state.mongo.client = AsyncIOMotorClient(Config.MONGODB_URI)
        app.state.mongo.db = app.state.mongo.client["holiday"]
        print("MongoDB 연결 성공")
    except Exception as e:
        print(f"MongoDB 연결 실패: {e}")
        raise e
    
    yield
    
    print("앱 종료: MongoDB 연결 해제 중...")
    app.state.mongo.client.close()
    print("MongoDB 연결 해제 완료")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"code": 200, "msg": "서버 접속 확인"}

# ? 연간 공휴일를 업데이트 한다.
@app.get("/holiday-update")
async def holiday_update(req: Request, year: Optional[int] = None):
    # * default는 현재 연도로 생각한다.
    year = year or datetime.now().year
    api_url = get_api_url(year)

    collection = req.app.state.mongo.db.public_holidays

    # todo : 저장할 collection이 있는지 먼저 찾아보기
    this_year_info = await collection.find_one({"base_year": year})

    # todo : 공휴일 API에서 데이터 가져오기
    async with httpx.AsyncClient() as client:
        res = await client.get(api_url)
        res.raise_for_status()
        api_data = res.json()

    data = api_data["response"]["body"]["items"]["item"]
    # * 이미 연도 데이터가 있다면 업데이트 하기
    if this_year_info:
        update_result = await collection.update_one(
            {"_id": this_year_info["_id"]},
            {"$set": {"item": data}}
        )
        if update_result:
            return {"code": 200, "msg" : "업데이트 완료"}
    # * 없다면 새로 넣기기
    else:
        new_holiday = {
            "base_year": year,
            "item": data
        }
        result = await collection.insert_one(new_holiday)
        if result.inserted_id:
            return {"code": 200, "msg": "새로운 데이터 생성"}
        else:
            raise HTTPException(status_code=401, detail="데이터 저장 실패")
        
# ? holiday-list를 가져온다.
@app.get("/holiday-list")
async def holiday_list(req: Request, year: Optional[int] = None):
    # * default는 현재 연도로 생각한다.
    year = year or datetime.now().year
    collection = req.app.state.mongo.db.public_holidays

    this_year_info = await collection.find_one({"base_year": year})
    if this_year_info:
        # ! ObjectId를 문자열로 변환, str형태가 아니면 에러 발생
        this_year_info["_id"] = str(this_year_info["_id"])
        return {"code": 200, "data": this_year_info}
    else:
        return {"code": 404, "msg": "데이터가 없습니다."}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=404, content={"code": 404, "msg": "페이지를 찾을 수 없습니다."})

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=500, content={"code": 500, "msg": "서버 에러 발생"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
