from fastapi import APIRouter, Request
from config import config
import httpx
from urllib.parse import urlencode

router = APIRouter()

@router.get('/restday-ind')
async def rest_ind(request: Request):
    # 공휴일 정보를 가져오는 경로
    GET_POINT = '/getRestDeInfo'

    query_params = {
        "_type": "json",
        "solYear": "2024",
        "numOfRows": "30"
    }

    url = f'{config["BASE_URL"]}{GET_POINT}?{urlencode(query_params)}&ServiceKey={config["SECRET_KEY"]}'
    print(f"Request URL: {url}")

    async with httpx.AsyncClient() as client:
        res = await client.get(url)

    if res.status_code != 200:
        return {"error": "API 호출 실패", "code": f"{res.status_code}"}

    try:
        data = res.json()
        print(data)

        # MongoDB 저장 (restday_info 컬렉션)
        result = await request.app.mongodb["restday_info"].insert_one(data)
        print(f"Inserted ID: {result.inserted_id}")

    except ValueError:
        return {"error": "응답 데이터를 JSON으로 변환할 수 없습니다."}
    except Exception as e:
        return {"error": f"MongoDB 저장 실패: {str(e)}"}

    return {"message": "MongoDB 사용 성공", "inserted_id": str(result.inserted_id)}