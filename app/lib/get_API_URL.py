from app.lib.get_current_Year import currentYear
from urllib.parse import urlencode
from config import config

# 공휴일 정보를 가져오는 경로
def get_API_URL(year = currentYear) : 
  GET_POINT = '/getRestDeInfo'

  query_params = {
      "_type": "json",
      "solYear": year, # ? 현재 연도 기준으로 데이터 정보를 업데이트
      "numOfRows": "30"
  }

  API_URL = f'{config["BASE_URL"]}{GET_POINT}?{urlencode(query_params)}&ServiceKey={config["SECRET_KEY"]}'
  # print(f"Request URL: {API_URL}")
  return API_URL