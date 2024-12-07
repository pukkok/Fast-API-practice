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
        datas = {
            "base_year": "2024",
            "item": data["response"]["body"]["items"]["item"]
        }

        collection = request.app.mongodb["restday_info"]

        # * 이미 존재하는 도큐먼트 확인
        document = await collection.find_one({"base_year": "2024"})
        if not document:
            # ? 도큐먼트가 없으면 삽입
            result = await collection.insert_one(datas)
            return {"msg": "새 도큐먼트를 추가했습니다.", "inserted_id": str(result.inserted_id)}
        else:
            # ? 도큐먼트가 있으면 업데이트
            update_result = await collection.update_one(
                {"base_year": "2024"},  # ? 업데이트 조건
                {"$set": {"item": datas["item"]}}  # ? 업데이트 내용
            )
            if update_result.modified_count > 0:
                return {"msg": "기존 도큐먼트를 업데이트했습니다."}
            else:
                return {"msg": "업데이트할 내용이 없어 기존 도큐먼트를 그대로 유지했습니다."}

    except ValueError:
        return {"error": "응답 데이터를 JSON으로 변환할 수 없습니다."}
    except Exception as e:
        return {"error": f"MongoDB 저장 실패: {str(e)}"}



@router.get('/restday-outd')
async def get_restday_list(request: Request):
    # TODO : MongoDB에서 restday_info 컬렉션 연도별 공휴일 데이터 불러오기
    try:
        # * MongoDB 컬렉션 객체
        collection = request.app.mongodb["restday_info"]

        # * 특정 연도의 데이터만 가져오기 (예: base_year가 "2024"인 데이터)
        document = await collection.find_one({"base_year": "2024"})

        # * 데이터가 없을 경우의 오류처리
        if not document:
            return {"error": "해당 연도의 데이터가 없습니다."}

        # * _id 값은 삭제 처리  
        if "_id" in document:
            document.pop("_id")

        return {"msg" : "데이터를 정상적으로 불러왔습니다.", "data" : document}
    except Exception as e:
        return {"error": f"MongoDB 데이터를 가져오는 중 오류 발생: {str(e)}"}