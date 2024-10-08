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

# 예외처리 쉽게하려고 만듬
# 예외 발생할 만한 곳에 때려박음
# 예외 발생시 정보를 클라이언트에게 넘김
def return_error(tag, e):
    print("Except:\t", e)
    return {"type"      : "exception",
            "message"   : "["+tag+"]"+str(e)}


# 이제부터 클라이언트 요청 처리하는 파트

# 루 트
@app.get("/")
async def root():
    return {"type"      : "message",
            "message"   : "Usage: /devices"}

# 장치 정보를 가져옴
@app.get("/devices")
async def devices():
    try:
        file = open("./devices.txt")
        devices_list = dict([dev.strip().split() for dev in file])
        devices_num = len(devices_list)
        file.close()

        return {"type"      : "data",
                "dev_num"   : devices_num,
                "dev_names" : list(devices_list.values()),
                "dev_addrs" : list(devices_list.keys()) }
            
    except Exception as e:
        return return_error("/devices", e)
    
# 장치 사용가능 여부 scan
@app.get("/scan")
async def scan():
    return 0;
