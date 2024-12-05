from fastapi import APIRouter
from config import config
import httpx
from urllib.parse import urlencode

router = APIRouter()

@router.get('/restday-info')
async def rest_holiday():
    GET_POINT = '/getRestDeInfo'
    query_params = {
        "_type": "json",
        "solYear": "2024",
        "numOfRows": "30"
    }
    url = f'{config["BASE_URL"]}{GET_POINT}?{urlencode(query_params)}&ServiceKey={config["SECRET_KEY"]}'
    # print(f"Request URL: {url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    if response.status_code != 200:
        return {"error": f"API 호출 실패. 상태 코드: {response.status_code}"}
    
    try:
        data = response.json()
    except ValueError:
        return {"error": "응답 데이터를 JSON으로 변환할 수 없습니다."}
    
    return {"data": data}