# 분점

# BLE, 비동기 프로그래밍 관련
import asyncio
from bleak import BleakClient, BleakScanner


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