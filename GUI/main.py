# 실행:
# cd GUI
# uvicorn main:app --reload

# 서버관련 패키지
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# BLE, 비동기
import asyncio
from bleak import BleakClient, BleakScanner
import blecode as blecode

# 예외 traceback
import traceback

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
    allow_methods=["*"],
    allow_headers=["*"],
)

# 클라이언트로부터 센서 정보 받을 때 사용할 구조
class DeviceInfo(BaseModel):
    dev_list : list




# 예외처리 쉽게하려고 만듬
# 예외 발생할 만한 곳에 때려박음
# 예외 발생시 정보를 클라이언트에게 넘김
def return_error(tag, e):
    traceback.print_exc()
    print("Except:\t", e)
    return {"type"      : "exception",
            "message"   : "("+tag+"):"+str(e)}

# 서버가 클라이언트에게 메시지 보낼 때(예외가 아닌 모든 경우:연결 끊어짐 등등..)
def return_message(tag, msg):
    return {"type"      : "message",
            "message"   : "("+tag+"):"+msg}


please = 30

# 이제부터 클라이언트 요청 처리하는 파트

# 루 트
@app.get("/")
async def root():
    return {"type"      : "message",
            "message"   : "Usage: /devices, /scan, /predict_start, /predict_get"}

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
@app.post("/scan")
async def scan(item : DeviceInfo):
    #print(item.dev_list)
    try:
        dev_online = await blecode.scan_device(item.dev_list)
        return {"type"      :"data",
                "dev_online": dev_online}
    
    except Exception as e:
        return return_error("/scan", e)

# 추론을 준비하고 실행함
@app.post("/predict_start")
async def predict_start(item : DeviceInfo):
    try:
        await blecode.get_IMU(item.dev_list, 30)
        return {"type"      :"message",
                "message"   :"자세 추론?이 끝남"}
    
    except Exception as e:
        return return_error("/predict_start", e)

# 추론 결과를 얻어옴 
@app.get("/predict_get")
async def predict_get():
    try:
        blestatus = blecode.ble_status

        # ready 인 경우 -- 얻어갈 게 없음..
        if blestatus == "ready":
            return return_message("/predict_get","predict_ready first")
        # disconnected인 경우 -- 문제 발생해서 미리 알림
        elif blestatus == "disconnected":
            return return_message("/predict_get","어떤 센서가 갑자기 끊어짐;;")
        # on 상태인 경우 -- 추론 결과 설파
        elif blestatus == "on":
            return {"type"      :"data",
                    "dev_online": blecode.predict_result}
        
        # wait 상태의 경우 -- ready가 될 때 까지 히히 못가
        while(blecode.ble_status == "wait"):
            await asyncio.sleep(0.1)
        return return_message("/predict_get","wait상태 끝")
    
    except Exception as e:
        return return_error("/predict_get", e)

