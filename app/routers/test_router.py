from fastapi import APIRouter, HTTPException

router = APIRouter()

# path parameter로 받기
@router.get('/load/{key}')
async def load_data(key: str):
    data = key
    return { "data" : data }

# query string으로 받기
@router.get('/data')
async def get_data(name: str):
    data = f'{name}님 안녕하세요.'
    return { "data" : data }