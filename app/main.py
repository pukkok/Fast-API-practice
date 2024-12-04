from fastapi import FastAPI
from app.routers import test_router
from config import config
import uvicorn
import httpx
from urllib.parse import urlencode

app = FastAPI()


@app.get("/")
async def root():
    return {"message" : "서버 접속 성공"}

@app.get('/restday-info')
async def rest_holiday():
    GET_POINT = '/getRestDeInfo'
    query_params = {
        "_type": "json",
        "solYear": "2024",
        "numOfRows": "30",
        "ServiceKey": config["SECRET_KEY"]
    }
    url = f'{config["BASE_URL"]}{GET_POINT}?{urlencode(query_params)}'
    print(f"Request URL: {url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    if response.status_code != 200:
        return {"error": f"API 호출 실패. 상태 코드: {response.status_code}"}
    
    try:
        data = response.json()
    except ValueError:
        return {"error": "응답 데이터를 JSON으로 변환할 수 없습니다."}
    
    return {"data": data}


 
app.include_router(test_router.router, prefix='/test', tags=["test"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# 서버 실행은 다음 명령어로 실행
# uvicorn app.main:app --reload