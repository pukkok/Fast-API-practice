from app.lib.get_current_Year import currentYear
from urllib.parse import urlencode
from config import config

# 공휴일 정보를 가져오는 경로
def get_API_URL(year=currentYear):
    GET_POINT = '/getRestDeInfo'

    query_params = {
        "_type": "json",
        "solYear": year,  # 현재 연도 기준으로 데이터 정보를 업데이트
        "numOfRows": "30"
    }

    # BASE_URL이 http:// 또는 https://로 시작하는지 확인
    if not config["BASE_URL"].startswith(('http://', 'https://')):
        raise ValueError(f"BASE_URL is missing a protocol. URL must start with 'http://' or 'https://'. Got: {config['BASE_URL']}")

    API_URL = f'{config["BASE_URL"]}{GET_POINT}?{urlencode(query_params)}&ServiceKey={config["SECRET_KEY"]}'
    return API_URL