import helics as h
import math
import csv
import os

fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "--federates=1 --broker=localhost")
h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)

fed = h.helicsCreateValueFederate("RenewableFederate", fedinfo)
pub = h.helicsFederateRegisterGlobalPublication(fed, "PV_Output", h.HELICS_DATA_TYPE_DOUBLE, "")

h.helicsFederateEnterExecutingMode(fed)

# 데이터 저장을 위한 리스트
data = []

time = 0
while time < 24:  # 하루 24시간 시뮬레이션
    # 태양광 발전 단순 모델 (사인 함수 기반) + 노이즈 추가
    base_output = max(0, 1000 * math.sin(math.pi * time / 24))  # 최대 1MW
    noise = 50 * math.sin(2 * math.pi * time / 6)  # 6시간 주기 변동
    pv_output = max(0, base_output + noise)
    
    h.helicsPublicationPublishDouble(pub, pv_output)
    print(f"[Renewable] t={time}h, PV={pv_output:.2f} kW")
    
    # 데이터 저장
    data.append([time, pv_output])
    
    time = h.helicsFederateRequestTime(fed, time + 1)

# 데이터를 CSV 파일로 저장
case_type = os.environ.get('CASE_TYPE', '1')
data_dir = f'/Users/seokjaehong/work/cosim-paper/results/data/case{case_type}'
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, 'pv_output_data.csv')
with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['time', 'pv_output_kw'])
    writer.writerows(data)

print("✅ PV 데이터 저장 완료: results/data/pv_output_data.csv")

h.helicsFederateDisconnect(fed)
h.helicsFederateFree(fed)
h.helicsCloseLibrary()