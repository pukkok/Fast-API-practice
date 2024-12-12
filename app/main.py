from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
from config import Config

print("----------------")
print(Config.MONGODB_URI)
print(Config.BASE_URL)
print(Config.SECRET_KEY)
print("----------------")

app = FastAPI()

@app.get("/")
async def root():
    return {"code": 200, "msg": "서버 접속 확인"}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=404, content={"code": 404, "msg": "페이지를 찾을 수 없습니다."})

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=500, content={"code": 500, "msg": "서버 에러 발생"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
