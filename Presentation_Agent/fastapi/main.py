from fastapi import FastAPI
from routes import router
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
app.include_router(router)

# 이미지 저장 경로
STATIC_IMAGE_DIR = r"..\data\temp_images"
app.mount("/static", StaticFiles(directory=STATIC_IMAGE_DIR), name="static")