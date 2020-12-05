from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Dict
from uuid import UUID, uuid4
from fastapi import FastAPI, Body, Depends, HTTPException, Header, Form
from pydantic import BaseModel, HttpUrl, PositiveFloat, PositiveInt
from pydantic.main import Path

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine, Model, ObjectId, Field

from core.config import settings

client = AsyncIOMotorClient(settings.MONGO_DATABASE_URI)
engine = AIOEngine(motor_client=client, database="catalog_shop")

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_STR}/openapi.json"
)


async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}



