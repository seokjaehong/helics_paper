import helics as h
import math
import csv
import os

fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "")
h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)  # 1 second resolution

fed = h.helicsCreateValueFederate("RenewableFederate", fedinfo)
pub = h.helicsFederateRegisterGlobalPublication(fed, "PV_Output", h.HELICS_DATA_TYPE_DOUBLE, "")

h.helicsFederateEnterExecutingMode(fed)

# 데이터 저장을 위한 리스트
data = []

time = 0
while time < 300:  # 5분 (300초) 시뮬레이션
    # 태양광 발전 단순 모델 (5분 동안 일정한 출력에 변동 추가)
    base_output = 600  # 600kW 기본 출력
    # 구름 등으로 인한 빠른 변동 (10초 주기)
    fast_noise = 100 * math.sin(2 * math.pi * time / 10)
    # 느린 변동 (60초 주기)
    slow_noise = 50 * math.sin(2 * math.pi * time / 60)
    pv_output = max(0, base_output + fast_noise + slow_noise)
    
    h.helicsPublicationPublishDouble(pub, pv_output)
    if time % 60 == 0:  # 1분마다 출력
        print(f"[Renewable] t={time}s ({time/60:.1f}min), PV={pv_output:.2f} kW")
    
    # 데이터 저장
    data.append([time, pv_output])  # 초 단위 데이터 저장
    
    time = h.helicsFederateRequestTime(fed, time + 1)

# 데이터를 CSV 파일로 저장
case_type = os.environ.get('CASE_TYPE', '1')
data_dir = f'/Users/seokjaehong/work/cosim-paper/case_second/data/case{case_type}'
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, 'pv_output_data.csv')
with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['time_seconds', 'pv_output_kw'])
    writer.writerows(data)

print("✅ PV 데이터 저장 완료: results/data/pv_output_data.csv")

h.helicsFederateDisconnect(fed)
h.helicsFederateFree(fed)
h.helicsCloseLibrary()