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

@app.get("/")
async def root():
    return {"code": 200, "msg": "서버 접속 확인"}

@app.get("/holiday-update")
async def holiday_update(year: Optional[int] = None):
    year = year or datetime.now().year
    api_url = get_api_url(year)

    this_year_info = await mongo.db.public_holidays.find_one({"base_year": year})

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        response.raise_for_status()
        api_data = response.json()

    data = api_data["response"]["body"]["items"]["item"]

    if this_year_info:
        result = await mongo.db.public_holidays.update_one(
            {"_id": this_year_info["_id"]},
            {"$set": {"item": data}}
        )
        if result.modified_count:
            return {"code": 200, "msg": "업데이트 완료"}
        else:
            raise HTTPException(status_code=400, detail="업데이트 실패")
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

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=404, content={"code": 404, "msg": "페이지를 찾을 수 없습니다."})

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=500, content={"code": 500, "msg": "서버 에러 발생"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
