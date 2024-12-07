from fastapi import APIRouter, Request
from config import config
import httpx
from urllib.parse import urlencode

from bson import ObjectId  # MongoDB ObjectId를 다룰 때 사용
from typing import List

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
        datas = {
            "base_year" : "2024",
            "data" : data["response"]["body"]["items"]
        }

        # MongoDB 저장 (restday_info 컬렉션)
        result = await request.app.mongodb["restday_info"].insert_one(datas)
        print(f"Inserted ID: {result.inserted_id}")

    except ValueError:
        return {"error": "응답 데이터를 JSON으로 변환할 수 없습니다."}
    except Exception as e:
        return {"error": f"MongoDB 저장 실패: {str(e)}"}

    return {"message": "MongoDB 사용 성공", "inserted_id": str(result.inserted_id)}


@router.get('/restday-outd')
async def get_restday_list(request: Request):
    """
    MongoDB에서 restday_info 컬렉션의 모든 데이터를 불러옵니다.
    """
    try:
        # MongoDB 컬렉션 객체
        collection = request.app.mongodb["restday_info"]
        # print(collection)
        # 모든 데이터를 가져오기 (커서 사용)
        data = await collection.find_one({"base_year" : "2024"})
        print(data["data"])        
        # result = []
        # async for document in cursor:
        #     document["_id"] = str(document["_id"])  # ObjectId를 문자열로 변환
        #     result.append(document)

        # return result
        return {"msg" : "동작중", "data" : "data"}
    except Exception as e:
        return {"error": f"MongoDB 데이터를 가져오는 중 오류 발생: {str(e)}"}