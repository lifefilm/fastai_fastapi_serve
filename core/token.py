from fastapi import Header, HTTPException
from config import settings

async def get_token_header(x_token: str = Header(...)):
    if x_token != settings.TOKEN:
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != settings.TOKEN:
        raise HTTPException(status_code=400, detail="No TOKEN provided")