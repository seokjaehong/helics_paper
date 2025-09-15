import helics as h
import math
import csv
import json
from datetime import datetime

# Case 1: ESS 없음 - 태양광만 존재하는 시나리오

fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "--federates=2 --broker=localhost")
h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)

fed = h.helicsCreateValueFederate("SolarFederate_Case1", fedinfo)
pub = h.helicsFederateRegisterGlobalPublication(fed, "PV_Output", h.HELICS_DATA_TYPE_DOUBLE, "")

h.helicsFederateEnterExecutingMode(fed)
print("🌞 Case 1: 태양광 페더레이트 시작 (ESS 없음)")

# 데이터 저장을 위한 리스트
data = []

time = 0
while time < 24:  # 24시간 시뮬레이션
    # 태양광 발전 모델 (사인 함수 기반, 더 큰 변동성)
    base_pv = max(0, 1200 * math.sin(math.pi * time / 24))  # 최대 1.2MW
    # 구름에 의한 변동성 추가
    variation = 50 * math.sin(2 * math.pi * time / 3) if 8 <= time <= 18 else 0
    pv_output = max(0, base_pv + variation)

    h.helicsPublicationPublishDouble(pub, pv_output)
    print(f"[Solar Case1] t={time:2d}h, PV={pv_output:6.2f} kW")

    # 데이터 저장
    data.append({
        'time': time,
        'pv_output': pv_output,
        'timestamp': datetime.now().isoformat()
    })

    time = h.helicsFederateRequestTime(fed, time + 1)

# 데이터를 CSV와 JSON으로 저장
with open('/Users/seokjaehong/work/cosim-paper/results/data/solar_case1_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['time', 'pv_output', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

with open('/Users/seokjaehong/work/cosim-paper/results/data/solar_case1_data.json', 'w') as jsonfile:
    json.dump(data, jsonfile, indent=2, ensure_ascii=False)

print("📊 Case 1 태양광 데이터 저장 완료")

h.helicsFederateFinalize(fed)
h.helicsFederateDisconnect(fed)
h.helicsFederateFree(fed)
h.helicsCloseLibrary()