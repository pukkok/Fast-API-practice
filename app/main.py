from fastapi import FastAPI
from app.routers import test_router
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message" : "서버 접속 성공"}
 
app.include_router(test_router.router, prefix='/test', tags=["test"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)

# 서버 실행은 다음 명령어로 실행
# uvicorn app.main:app --reload