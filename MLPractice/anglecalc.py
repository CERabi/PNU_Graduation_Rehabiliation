import serial
import numpy as np

# 시리얼 포트 설정
handport = serial.Serial(port = 'COM5', baudrate=9600)
armport = serial.Serial(port = 'COM8', baudrate=9600)

# 미리 계산된 weight, bias (Ridge Regression 이용)
coefs = [ 1.28123355e+00, 4.34966600e+01, 4.28350327e+00, 1.93793641e-02, \
   1.81387252e-02,  4.19872825e-02,  9.49757049e-02,  6.72037274e-02, \
   7.60493054e-03, -5.87107768e+00, -2.55045981e+01,  4.94706580e+01, \
   8.96187969e-02, -8.00975347e-03,  3.21549074e-02,  2.79065772e-02, \
  -1.01278930e-01, -2.30957552e-01]
coefs = np.array(coefs)
intercept = 41.0434

while True:
    try:
        # 시리얼 포트로부터 데이터 수신
        handdata = handport.readline().decode().strip()
        armdata = armport.readline().decode().strip()
        
        # 수신된 데이터를 합치고 double 타입으로 변환
        data = np.array(handdata.split(",")[1:] + armdata.split(",")[1:])
        data = np.double(data)
        
        # 각도 추정
        print(np.dot(data,coefs) + intercept)
        
        
    except:
        # 포트 닫기
        handport.close()
        armport.close()
        break
