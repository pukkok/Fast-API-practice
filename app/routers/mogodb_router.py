from fastapi import APIRouter, Request, Query
import httpx
from app.lib.get_current_Year import currentYear
from app.lib.get_API_URL import get_API_URL

router = APIRouter()

@router.get('/restday-update-db')
async def rest_update_db(request: Request, year: str = Query(default=str(currentYear))):
    print(f"Received request to update database for year: {year}")

    API_URL = get_API_URL(year)
    print(f"Fetching data from API URL: {API_URL}")

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(API_URL)
            print(f"API response status code: {res.status_code}")

        if res.status_code != 200:
            return {"error": "API 호출 실패", "code": f"{res.status_code}"}

        data = res.json()
        datas = {
            "base_year": f"{year}",
            "item": data["response"]["body"]["items"]["item"]
        }
        print(f"Data to be inserted/updated: {datas}")

        # MongoDB 연결 (request.app.state.mongodb)
        collection = request.app.state.mongodb["restday_info"]

        # 이미 존재하는 도큐먼트 확인
        document = await collection.find_one({"base_year": f"{year}"})
        if not document:
            # 도큐먼트가 없으면 삽입
            print("No existing document found, inserting a new document.")
            result = await collection.insert_one(datas)
            print(f"Inserted new document with id: {result.inserted_id}")
            return {"msg": "Added a new document.", "inserted_id": str(result.inserted_id)}
        else:
            # 도큐먼트가 있으면 업데이트
            print("Existing document found, performing update.")
            update_result = await collection.update_one(
                {"base_year": f"{year}"},  # 업데이트 조건
                {"$set": {"item": datas["item"]}}  # 업데이트 내용
            )
            if update_result.modified_count > 0:
                print("Update completed successfully.")
                return {"msg": "Update completed"}
            else:
                print("No update changes. Document remains unchanged.")
                return {"msg": "No update changes. Maintain existing document"}

    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return {"error": "Unable to convert response data to JSON."}
    except Exception as e:
        print(f"MongoDB save failed: {str(e)}")
        return {"error": f"MongoDB save failed: {str(e)}"}

@router.get('/restday-list')
async def get_restday_list(request: Request, year: str = Query(default=str(currentYear))):
    try:
        # MongoDB 연결 (request.app.state.mongodb)
        collection = request.app.state.mongodb["restday_info"]

        # 특정 연도의 데이터만 가져오기
        document = await collection.find_one({"base_year": year})

        if not document:
            return {"error": "해당 연도의 데이터가 없습니다."}

        # _id 값 삭제
        if "_id" in document:
            document.pop("_id")

        return {"msg": "데이터를 정상적으로 불러왔습니다.", "data": document}
    except Exception as e:
        return {"error": f"MongoDB 데이터를 가져오는 중 오류 발생: {str(e)}"}
