import helics as h
import csv
import os

fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "--federates=1 --broker=localhost")
h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)  # 1 second resolution

fed = h.helicsCreateValueFederate("ESSFederate", fedinfo)
sub_pv = h.helicsFederateRegisterSubscription(fed, "PV_Output", "")
sub_voltage = h.helicsFederateRegisterSubscription(fed, "bus680_voltage", "")  # 말단 버스 전압 구독
pub = h.helicsFederateRegisterGlobalPublication(fed, "ESS_Output", h.HELICS_DATA_TYPE_DOUBLE, "")

h.helicsFederateEnterExecutingMode(fed)

# ESS 용량을 환경변수로 설정 (기본값: 500 kWh)
import os
capacity = float(os.environ.get('ESS_CAPACITY', '500'))  # kWh
max_power = min(200, capacity * 0.4)  # 용량의 40% 또는 최대 200kW

print(f"🔋 ESS 설정: 용량={capacity} kWh, 최대출력={max_power} kW")

# 데이터 저장을 위한 리스트
data = []

time = 0
SOC = 0.5  # 초기 ESS 상태 (50%)

while time < 300:  # 5분 (300초) 시뮬레이션
    time = h.helicsFederateRequestTime(fed, time + 1)
    pv_output = h.helicsInputGetDouble(sub_pv)
    
    # 전압 정보 수신 (벡터에서 크기 추출)
    voltage_vector = h.helicsInputGetVector(sub_voltage)
    if len(voltage_vector) >= 2:
        import cmath
        voltage_magnitude = abs(voltage_vector[0] + 1j * voltage_vector[1])
    else:
        voltage_magnitude = 0.98  # 기본값
    
    # 최적화된 ESS 제어 로직
    target_voltage = 0.99  # 목표 전압 (pu)
    voltage_error = voltage_magnitude - target_voltage
    
    # 전압 기반 제어 (PID 제어기 스타일)
    if abs(voltage_error) > 0.005:  # 전압 오차가 0.5% 이상일 때만 제어
        if voltage_error > 0:  # 전압이 높음 → 충전 (부하 증가)
            if SOC < 0.95:  # SOC 여유가 있을 때만 충전
                # 전압 오차에 비례한 충전량
                charge_power = min(max_power, abs(voltage_error) * 2000)  # 0.01 pu 오차당 20kW
                ess_output = -min(charge_power, (1.0 - SOC) * capacity)
                SOC = min(1.0, SOC - ess_output / capacity)
            else:
                ess_output = 0.0
        else:  # 전압이 낮음 → 방전 (부하 감소)
            if SOC > 0.05:  # SOC가 있을 때만 방전
                # 전압 오차에 비례한 방전량
                discharge_power = min(max_power, abs(voltage_error) * 2000)  # 0.01 pu 오차당 20kW
                ess_output = min(discharge_power, SOC * capacity)
                SOC = max(0.0, SOC - ess_output / capacity)
            else:
                ess_output = 0.0
    else:
        # 전압이 안정적일 때는 SOC 유지
        if SOC > 0.8:  # SOC가 높으면 약간 방전
            ess_output = min(20, SOC * capacity * 0.05)  # 소량 방전
            SOC = max(0.0, SOC - ess_output / capacity)
        elif SOC < 0.2:  # SOC가 낮으면 약간 충전
            ess_output = -min(20, (1.0 - SOC) * capacity * 0.05)  # 소량 충전
            SOC = min(1.0, SOC - ess_output / capacity)
        else:
            ess_output = 0.0
    
    h.helicsPublicationPublishDouble(pub, ess_output)
    if time % 60 == 0:  # 1분마다 출력
        print(f"[ESS] t={time}s ({time/60:.1f}min), PV={pv_output:.2f}, ESS={ess_output:.2f} kW, SOC={SOC:.2f}, V={voltage_magnitude:.4f} pu, Error={voltage_error:.4f}")
    
    # 데이터 저장 (초 단위)
    data.append([time, pv_output, ess_output, SOC])

# 데이터를 CSV 파일로 저장
case_type = os.environ.get('CASE_TYPE', '2')
data_dir = f'/Users/seokjaehong/work/cosim-paper/case_second/data/case{case_type}'
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, 'ess_output_data.csv')
with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['time_seconds', 'pv_output_kw', 'ess_output_kw', 'soc'])
    writer.writerows(data)

print("✅ ESS 데이터 저장 완료: results/data/ess_output_data.csv")

h.helicsFederateDisconnect(fed)
h.helicsFederateFree(fed)
h.helicsCloseLibrary()