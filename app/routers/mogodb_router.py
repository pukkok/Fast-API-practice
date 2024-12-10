from fastapi import APIRouter, Request, Query
import httpx
from app.lib.get_current_Year import currentYear
from app.lib.get_API_URL import get_API_URL

router = APIRouter()

# * 데이터베이스를 업데이트 할 때 사용한다.
@router.get('/restday-update-db')
async def rest_update_db(request: Request, year : str = Query(default=str(currentYear))):

    API_URL = get_API_URL(year) # * 공휴일 API URL

    async with httpx.AsyncClient() as client:
        res = await client.get(API_URL)

    if res.status_code != 200:
        return {"error": "API 호출 실패", "code": f"{res.status_code}"}

    try:
        data = res.json()
        datas = {
            "base_year": f"{year}",
            "item": data["response"]["body"]["items"]["item"]
        }

        collection = request.app.mongodb["restday_info"]

        # * 이미 존재하는 도큐먼트 확인
        document = await collection.find_one({"base_year": f"{year}"})
        if not document:
            # ? 도큐먼트가 없으면 삽입
            result = await collection.insert_one(datas)
            return {"msg": "Added a new document.", "inserted_id": str(result.inserted_id)}
        else:
            # ? 도큐먼트가 있으면 업데이트
            update_result = await collection.update_one(
                {"base_year": f"{year}"},  # ? 업데이트 조건
                {"$set": {"item": datas["item"]}}  # ? 업데이트 내용
            )
            if update_result.modified_count > 0:
                return {"msg": "Update completed"}
            else:
                return {"msg": "No update changes. Maintain existing document"}

    except ValueError:
        return {"error": "Unable to convert response data to JSON."}
    except Exception as e:
        return {"error": f"MongoDB 저장 실패: {str(e)}"}


# * 공휴일 연도별 데이터를 불러온다.
@router.get('/restday-list')
async def get_restday_list(request: Request, year : str = Query(default=str(currentYear))):
    # TODO : MongoDB에서 restday_info 컬렉션 연도별 공휴일 데이터 불러오기
    try:
        # * MongoDB 컬렉션 객체
        collection = request.app.mongodb["restday_info"]

        # * 특정 연도의 데이터만 가져오기 (예: base_year가 "2024"인 데이터)
        document = await collection.find_one({"base_year": year})

        # * 데이터가 없을 경우의 오류처리
        if not document:
            return {"error": "해당 연도의 데이터가 없습니다."}

        # * _id 값은 삭제 처리  
        if "_id" in document:
            document.pop("_id")

        return {"msg" : "데이터를 정상적으로 불러왔습니다.", "data" : document}
    except Exception as e:
        return {"error": f"MongoDB 데이터를 가져오는 중 오류 발생: {str(e)}"}