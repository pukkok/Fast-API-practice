from config import Config

# Utility function to generate API URL
def get_api_url(year: int) -> str:
    get_point = "/getRestDeInfo"
    queries = ["_type=json", f"solYear={year}", "numOfRows=30"]
    api_url = f"{Config.BASE_URL}{get_point}?{'&'.join(queries)}&ServiceKey={Config.SECRET_KEY}"
    return api_url