# 실행:
# cd GUI
# uvicorn main:app --reload

# 서버관련 패키지
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import asyncio

# 서버생성, CROS관련 설정
app = FastAPI()
origins = [
	"*" # 모든 출처? 허용
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_origin_regex="http://127\.0\.0\.1(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    return {"message":"Usage: /devices"}


