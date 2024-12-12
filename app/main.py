from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn
import httpx
from config import Config
from motor.motor_asyncio import AsyncIOMotorClient
from app.lib.get_api_url import get_api_url
from datetime import datetime

# MongoDB 초기화
class MongoDB:
    client = AsyncIOMotorClient(Config.MONGODB_URI)
    db = client["holiday"]

app = FastAPI()
mongo = MongoDB()


@app.on_event("startup")
async def startup_db_client():
    try:
        await mongo.client.server_info()
        print("MongoDB 연결 완료")
    except Exception as e:
        print(f"DB연결 실패: {e}")

@app.get("/")
async def root():
    return {"code": 200, "msg": "서버 접속 확인"}

# ? 연간 공휴일를 업데이트 한다.
@app.get("/holiday-update")
async def holiday_update(year: Optional[int] = None):
    # * default는 현재 연도로 생각한다.
    year = year or datetime.now().year
    api_url = get_api_url(year)

    # todo : 저장할 collection이 있는지 먼저 찾아보기
    this_year_info = await mongo.db.public_holidays.find_one({"base_year": year})

    # todo : 공휴일 API에서 데이터 가져오기
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        response.raise_for_status()
        api_data = response.json()

    data = api_data["response"]["body"]["items"]["item"]
    # * 이미 연도 데이터가 있다면 업데이트 하기
    if this_year_info:
        update_result = await mongo.db.public_holidays.update_one(
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
        result = await mongo.db.public_holidays.insert_one(new_holiday)
        if result.inserted_id:
            return {"code": 200, "msg": "새로운 데이터 생성"}
        else:
            raise HTTPException(status_code=401, detail="데이터 저장 실패")
        
# ? holiday-list를 가져온다.
@app.get("/holiday-list")
async def holiday_list(year: Optional[int] = None):
    # * default는 현재 연도로 생각한다.
    year = year or datetime.now().year
    this_year_info = await mongo.db.public_holidays.find_one({"base_year": year})
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
