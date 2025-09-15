import helics as h
import csv
import json
from datetime import datetime

# Case 2: ESS 페더레이트 - 개선된 제어 로직

fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "--federates=3 --broker=localhost")
h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)

fed = h.helicsCreateValueFederate("ESSFederate_Case2", fedinfo)
sub = h.helicsFederateRegisterSubscription(fed, "PV_Output", "")
pub = h.helicsFederateRegisterGlobalPublication(fed, "ESS_Output", h.HELICS_DATA_TYPE_DOUBLE, "")

h.helicsFederateEnterExecutingMode(fed)
print("🔋 Case 2: ESS 페더레이트 시작")

# ESS 파라미터 (개선된 설정)
SOC = 0.5  # 초기 ESS 상태 (50%)
capacity = 800  # kWh (증가된 용량)
max_power = 300  # kW (증가된 출력)
min_soc = 0.1  # 최소 SOC
max_soc = 0.9  # 최대 SOC

# 제어 임계값 (더 정교한 제어)
pv_high_threshold = 800  # PV 높음 임계값 (충전 시작)
pv_low_threshold = 300   # PV 낮음 임계값 (방전 시작)

# 데이터 저장을 위한 리스트
ess_data = []

time = 0
while time < 24:
    time = h.helicsFederateRequestTime(fed, time + 1)
    pv_output = h.helicsInputGetDouble(sub)

    # 개선된 ESS 제어 로직
    ess_output = 0.0

    if pv_output > pv_high_threshold and SOC < max_soc:
        # PV 출력이 높고 SOC가 최대가 아니면 충전
        charge_power = min(max_power, (max_soc - SOC) * capacity)
        ess_output = -charge_power  # 충전 (음수)
        SOC += charge_power / capacity
        control_mode = "충전"

    elif pv_output < pv_low_threshold and SOC > min_soc:
        # PV 출력이 낮고 SOC가 최소가 아니면 방전
        discharge_power = min(max_power, (SOC - min_soc) * capacity)
        ess_output = discharge_power  # 방전 (양수)
        SOC -= discharge_power / capacity
        control_mode = "방전"

    else:
        # 대기 모드
        ess_output = 0.0
        control_mode = "대기"

    # SOC 제한
    SOC = max(min_soc, min(max_soc, SOC))

    h.helicsPublicationPublishDouble(pub, ess_output)
    print(f"[ESS Case2] t={time:2d}h, PV={pv_output:6.1f}kW, ESS={ess_output:6.1f}kW, SOC={SOC:.2%}, {control_mode}")

    # 데이터 저장
    ess_data.append({
        'time': time,
        'pv_output': pv_output,
        'ess_output': ess_output,
        'soc': SOC,
        'control_mode': control_mode,
        'timestamp': datetime.now().isoformat()
    })

# 데이터 저장
with open('/Users/seokjaehong/work/cosim-paper/results/data/ess_case2_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['time', 'pv_output', 'ess_output', 'soc', 'control_mode', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ess_data)

with open('/Users/seokjaehong/work/cosim-paper/results/data/ess_case2_data.json', 'w') as jsonfile:
    json.dump(ess_data, jsonfile, indent=2, ensure_ascii=False)

print("📊 Case 2 ESS 데이터 저장 완료")
print(f"최종 SOC: {SOC:.2%}")

h.helicsFederateFinalize(fed)
h.helicsFederateDisconnect(fed)
h.helicsFederateFree(fed)
h.helicsCloseLibrary()