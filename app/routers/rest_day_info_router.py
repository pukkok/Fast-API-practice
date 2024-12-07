from fastapi import APIRouter, Query
from config import config
import httpx
from urllib.parse import urlencode

router = APIRouter()

# ? 연과 월을 받아 공휴일 restAPI에서 데이터를 불러온다.
@router.get('/restday-info')
async def rest_holiday(solYear: str = Query(default="2024"), solMonth: str = Query(default="")):
    # ? 공휴일정보를 가져오는 경로
    GET_POINT = '/getRestDeInfo'

    # ? 2자리수로 맞춰주기 위한 작업
    pad_month = str(solMonth).zfill(2)

    # ? API를 불러오기위한 쿼리파라미터 딕셔너리
    query_params = {
        "_type": "json",
        "solYear": solYear,
        "numOfRows": "30"
    }
    
    if pad_month != "00" :
        query_params["solMonth"] = pad_month
    
    url = f'{config["BASE_URL"]}{GET_POINT}?{urlencode(query_params)}&ServiceKey={config["SECRET_KEY"]}'
    # print(f"Request URL: {url}")
    
    # ? AsyncClient를 이용하여 비동기적으로 처리한다.
    # ? restAPI에 GET요청을 하여 데이터를 불러온다.
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    
    if res.status_code != 200:
        return {"error": "API 호출 실패", "code": f"{res.status_code}"}
    
    try:
        data = res.json()
    except ValueError:
        return {"error": "응답 데이터를 JSON으로 변환할 수 없습니다."}
    
    return {"data": data}