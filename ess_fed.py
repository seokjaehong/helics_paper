import helics as h
import csv
import os

fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "--federates=1 --broker=localhost")
h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)

fed = h.helicsCreateValueFederate("ESSFederate", fedinfo)
sub = h.helicsFederateRegisterSubscription(fed, "PV_Output", "")
pub = h.helicsFederateRegisterGlobalPublication(fed, "ESS_Output", h.HELICS_DATA_TYPE_DOUBLE, "")

h.helicsFederateEnterExecutingMode(fed)

# 데이터 저장을 위한 리스트
data = []

time = 0
SOC = 0.5  # 초기 ESS 상태 (50%)
capacity = 500  # kWh
max_power = 200  # kW

while time < 24:
    time = h.helicsFederateRequestTime(fed, time + 1)
    pv_output = h.helicsInputGetDouble(sub)
    
    # 전압 안정화를 위한 적극적인 ESS 제어
    # PV 변동에 반응하여 전압 안정화
    if pv_output > 600:  # PV가 높을 때 충전 (전압 상승 억제)
        if SOC < 0.9:
            ess_output = -min(max_power, (1.0 - SOC) * capacity)
            SOC = min(1.0, SOC - ess_output / capacity)
        else:
            ess_output = 0.0
    elif pv_output < 400:  # PV가 낮을 때 방전 (전압 하락 방지)
        if SOC > 0.1:
            ess_output = min(max_power, SOC * capacity)
            SOC = max(0.0, SOC - ess_output / capacity)
        else:
            ess_output = 0.0
    else:  # 중간 범위에서는 SOC 유지
        if SOC > 0.7:  # SOC가 높으면 약간 방전
            ess_output = min(50, SOC * capacity * 0.1)
            SOC = max(0.0, SOC - ess_output / capacity)
        elif SOC < 0.3:  # SOC가 낮으면 약간 충전
            ess_output = -min(50, (1.0 - SOC) * capacity * 0.1)
            SOC = min(1.0, SOC - ess_output / capacity)
        else:
            ess_output = 0.0
    
    h.helicsPublicationPublishDouble(pub, ess_output)
    print(f"[ESS] t={time}h, PV={pv_output:.2f}, ESS={ess_output:.2f} kW, SOC={SOC:.2f}")
    
    # 데이터 저장
    data.append([time, pv_output, ess_output, SOC])

# 데이터를 CSV 파일로 저장
case_type = os.environ.get('CASE_TYPE', '2')
data_dir = f'/Users/seokjaehong/work/cosim-paper/results/data/case{case_type}'
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, 'ess_output_data.csv')
with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['time', 'pv_output_kw', 'ess_output_kw', 'soc'])
    writer.writerows(data)

print("✅ ESS 데이터 저장 완료: results/data/ess_output_data.csv")

h.helicsFederateDisconnect(fed)
h.helicsFederateFree(fed)
h.helicsCloseLibrary()