# 분점

# -------- 라이브러리 ----------#

# BLE, 비동기 프로그래밍 관련
import asyncio
from bleak import BleakClient, BleakScanner
# 데이터 처리
import struct
from collections import defaultdict
import csv
import numpy as np

# -------- 변수들 ----------#

# 전역 상태변수
ble_status = "ready" # ready(일반), wait(기다림), on(실행 중), disconnected(뭐가 연결 해제됨)
predict_result = "hehe"

# BLE 서비스 characteristic uuid
UUID_NOTIFY = "cafe0003-87a1-aade-bab0-c0ffeef3ae45"  # 센서로부터
UUID_WRITE = "cafe0002-87a1-aade-bab0-c0ffeef3ae45"   # 센서로

# 같은 시간의 데이터를 한 행에 묶기 위한 변수들
frames = []                                 # 전체 데이터, 이후에 CSV파일로 저장. list(list) 형태
frames_temp = defaultdict(lambda:[])        # 임시로, 각 timestamp 별 센싱 데이터를 저장할 공간. 가득 차면 정렬하여 frames에 붙인다.
curr_frame_dev_num = defaultdict(lambda:0)  # frames_temp에서 timestamp 마다 센싱 데이터가 몇 개 쌓였는지 체크
max_frame_dev_num = 0                       # frames_temp의 timestamp마다 최대 몇 개의 데이터가 쌓일 수 있는지. 즉 데이터를 얻고 있는 총 센서 수를 뜻함.

# Critical Section lock
lock = asyncio.Lock()


# -------- 함수들 ----------#

# BLE 센서 스캔
async def scan_device(dev_list : list):
    print("센서 검색 중..")
    scanner = BleakScanner()

    # 장치 online여부 기록할 리스트
    dev_online = dict.fromkeys(dev_list,False)

    # 2초간 검색 시작
    await scanner.start()
    await asyncio.sleep(2.0)
    await scanner.stop()
    
    # 검색된 장치 가져오기
    devices = scanner.discovered_devices

    for d in devices:
        if d.address in dev_list:
            dev_online[d.address] = True
    
    return list(dev_online.values())
    # 검색 완료된 장치 목록 출력?

# 같은 시간의 데이터를 한 행에 묶기 위한 작업.
async def make_frame(data):
    # 장치 이름, 데이터 시간, 데이터
    devname = data[0].decode()
    devtime = data[1]
    devdata = data[2:]

    # 장치 이름과 데이터를 합치기
    temp = [devname]
    temp.extend(devdata)

    global frames

    # Critical section lock
    await lock.acquire()
    try:
        frames_temp[devtime].append(temp)           # frames_temp 딕셔너리의 timestamp 위치에 장치 이름과 데이터 추가.
        curr_frame_dev_num[devtime] += 1            # 그리고 해당 timestamp의 센싱 데이터 수 1 증가

        if curr_frame_dev_num[devtime] == max_frame_dev_num: # 그러다 이 timestamp에서 모든 장치의 센싱이 완료되면
            # 이제 하나의 frame으로 구성해 frames에 append.
            frame = [devtime]                       # 먼저 가장 앞에 시간 데이터 추가
            for i in sorted(frames_temp[devtime], key=lambda x:x[0]): # 장치 이름순으로 정렬
                frame.extend(i[1:])                 # 장치 이름은 뗌
            
            # 최종적으로 frames에 추가
            frames.append(frame)

            # 머신러닝 추론 수행
            if False:
                #print(frame)
                inp = np.array(frame[1:])
                res = model.predict(scaler.transform(inp.reshape(1,-1)))
                #print(res)
                print("{:.2f}s|".format(devtime/1000), end="")
                print("True" if res[0]==1 else "False")
                
            global predict_result
            predict_result = "result in make_frame"
            
    finally:
        # lock 해제
        lock.release()

# 센서로부터 값을 notify받을 때 발생하는 callback
async def when_notified(sender, data):

    # 수신된 값을 풀어해침.(c : char, i : int, 6f : float*6)
    imudata = struct.unpack('ci6f',data)

    # 서버 단에서 값을 보고 싶다면 주석 해제하기
    #print("\tName={}|Time={}|".format(imudata[0].decode(),imudata[1]),imudata[2:])

    # 수신된 값을 가지고 frame생성. (모든 센서 값이 한 행으로 이루어진 데이터)
    await make_frame(imudata)

# 센서와 연결 해제시 발생하는 callback
def on_disconnect(client: BleakClient):
    print("\t연결 해제됨:\tAddress={}".format(client.address))
    # 만약 값을 가져올 수 있는 상태에서 연결 해제가 발생한 경우
    # 무언가 연결 해제되었음을 알림
    global ble_status
    if ble_status == "on":
        ble_status = "disconnected"

# 센서에게 특정 메시지를 송신
async def write_message(client : BleakClient, time, message):
    print("\t메시지 전송!:","Address=",client.address)
    await client.write_gatt_char(UUID_WRITE, message) # 송신

# IMU 데이터 수집
# 장치 센싱 중에 연결 해제되면 exception 발생시키기
async def get_IMU(dev_addrs : list, gettime : int):
    
    # 센싱 데이터 관리용 변수 초기화
    global frames
    global max_frame_dev_num
    global frames_temp
    global curr_frame_dev_num
    frames = []                                 # 전체 데이터 초기화
    frames_temp = defaultdict(lambda:[])        # 임시 데이터도 초기화.
    max_frame_dev_num = len(dev_addrs)            # 한 frame 당 최대 센서 개수 지정
    curr_frame_dev_num = defaultdict(lambda:0)  # 현재 timestamp 에서 센싱 완료한 센서 개수 초기화

    print("센서와 연결 시작")

    # 상태를 wait로--값을 받을 수 있을 때까지 대기 유도
    global ble_status
    ble_status = "wait"
    
    # BleakClient 보관 리스트
    clients = list()   
    # 장치마다 client 클래스 생성
    for addr in dev_addrs:
        clients.append(BleakClient(addr, disconnected_callback=on_disconnect))
    
    try:
        # 장치 차례로 연결 시도(동시에 연결하게도 가능할 듯?)
        for client in clients:
            await client.connect()
            print("\t센서 연결됨:\tAddress={}".format(client.address))
            await client.start_notify(UUID_NOTIFY,when_notified)

        # 모든 장치의 timestamp를 동시에 초기화
        print("모든 센서의 timestamp 초기화")
        task = []
        for client in clients:
            task.append(asyncio.create_task(write_message(client, 1, struct.pack("hh",1,0))))
        await asyncio.wait(task)
        # 이를 통해 리스트에 등록된 모든 task가 동시에 수행된다.

        # 여기서부터 측정 시작됨

        # 값 가져올수 있음
        ble_status = "on"

        # 정해진 시간만큼 측정을 위해 sleep
        await asyncio.sleep(gettime)
        
        # 시간 경과
        print("시간 경과")

        # 값 이제 못 가져옴
        ble_status = "ready"

        # stop notify
        for client in clients:    
            await client.stop_notify(UUID_NOTIFY)

        return

    except Exception as e:
        print("센서 연결 과정에서 문제 발생")
        raise e

    finally:
        print('모든 센서 연결 해제')
        for client in clients:
            await client.disconnect()
        ble_status = "ready"

        # frames 잘 만들어지나?? ㅇㅇ
        # print(frames)