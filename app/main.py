from fastapi import FastAPI
import uvicorn # ? 서버 실행 도구

from app.routers import test_router # ? test 라우터
from app.routers import rest_day_info_router # ? 공휴일 불러오기 라우터

app = FastAPI()

@app.get("/")
async def root():
    return {"message" : "서버 접속 성공"}

# ? app에 prefix로 엔드포인트를 설정하여 router를 불러올 수 있다. 
app.include_router(test_router.router, prefix='/test', tags=["test"])
app.include_router(rest_day_info_router.router, prefix='/api', tags=["holiday"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# 서버 실행은 다음 명령어로 실행
# * uvicorn app.main:app --reload <- 고정된 포트 8000
# * uvicorn app.main:app --port 8080 --reload 내가 원하는 설정으로 열기