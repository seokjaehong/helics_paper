import helics as h
import opendssdirect as dss
import csv
import os

# -------------------------
# 1. HELICS Federate 생성
# -------------------------
fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreName(fedinfo, "dss_federate")
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "--federates=1 --broker=localhost")

# 시간 설정
h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)

# Value Federate 생성
fed = h.helicsCreateValueFederate("OpenDSS Federate", fedinfo)

# publish (버스 전압)
pub = h.helicsFederateRegisterGlobalPublication(fed, "bus650_voltage", h.HELICS_DATA_TYPE_VECTOR, "")

# subscribe (ESS 제어 명령)
sub = h.helicsFederateRegisterSubscription(fed, "ESS_Output", "")

h.helicsFederateEnterExecutingMode(fed)
print("✅ OpenDSS Federate 실행 시작")

# -------------------------
# 2. OpenDSS 초기화
# -------------------------
dss.Basic.ClearAll()

# IEEE13Nodeckt 파일 경로
# ieee13_path = repo_path / 'Version8' / 'Distrib' / 'IEEETestCases' / '13Bus' / 'IEEE13Nodeckt.dss'
ieee13_path = "/Users/seokjaehong/work/cosim-paper/electricdss-tst/Version8/Distrib/IEEETestCases/13Bus/IEEE13Nodeckt.dss"
print("IEEE13Nodeckt 위치:", ieee13_path)

dss.Text.Command(f"Compile [{ieee13_path}]")
dss.Solution.Solve()

# 데이터 저장을 위한 리스트 (여러 버스 모니터링)
voltage_data = []

# -------------------------
# 3. 시뮬레이션 루프
# -------------------------
time = 0
while time < 24:
    # HELICS time request
    time = h.helicsFederateRequestTime(fed, time + 1)
    
    # ESS 제어 명령 수신
    if h.helicsInputIsUpdated(sub):
        ess_power = h.helicsInputGetDouble(sub)
        print(f"[t={time}] ESS 제어 명령 수신: {ess_power:.2f} kW")
        # OpenDSS에 ESS 제어 적용 (예: Generator or Storage element 수정)
        dss.Text.Command(f"Edit Storage.ess_kw kw={ess_power}")  
        # Storage 요소가 없으므로 주석 처리
        # print(f"ESS 제어 신호 수신됨: {ess_power} kW (실제 적용은 Storage 요소 추가 후)")

    # 시뮬레이션 실행
    dss.Solution.Solve()

    # 여러 버스의 전압 데이터 수집
    bus_data = {}
    buses_to_monitor = ["650", "680", "692"]  # 변전소, 말단 버스들
    
    for bus_name in buses_to_monitor:
        try:
            dss.Circuit.SetActiveBus(bus_name)
            voltages = dss.Bus.PuVoltage()
            
            # 복소수 전압을 크기와 각도로 변환
            import cmath
            voltage_magnitude = abs(voltages[0] + 1j * voltages[1])  # 첫 번째 전압의 크기
            voltage_angle = cmath.phase(voltages[0] + 1j * voltages[1])  # 첫 번째 전압의 각도
            
            bus_data[bus_name] = {
                'magnitude': voltage_magnitude,
                'angle': voltage_angle
            }
            
            print(f"[t={time}] Bus{bus_name} Voltage (pu): {voltage_magnitude:.6f} ∠{voltage_angle:.6f}")
            
        except Exception as e:
            print(f"[t={time}] Bus{bus_name} 전압 읽기 실패: {e}")
            bus_data[bus_name] = {'magnitude': 0, 'angle': 0}
    
    # 데이터 저장 - 모든 버스의 전압 정보
    voltage_data.append([
        time,
        bus_data.get("650", {}).get('magnitude', 0),
        bus_data.get("650", {}).get('angle', 0),
        bus_data.get("680", {}).get('magnitude', 0),
        bus_data.get("680", {}).get('angle', 0),
        bus_data.get("692", {}).get('magnitude', 0),
        bus_data.get("692", {}).get('angle', 0)
    ])

    # HELICS publish
    h.helicsPublicationPublishVector(pub, voltages)

# 데이터를 CSV 파일로 저장
print(f"[DEBUG] 저장할 데이터 개수: {len(voltage_data)}")
case_type = os.environ.get('CASE_TYPE', '1')
data_dir = f'/Users/seokjaehong/work/cosim-paper/results/data/case{case_type}'
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, 'voltage_data.csv')
print(f"[DEBUG] 파일 경로: {file_path}")

with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['time', 'bus650_magnitude', 'bus650_angle', 'bus680_magnitude', 'bus680_angle', 'bus692_magnitude', 'bus692_angle'])
    writer.writerows(voltage_data)

print(f"[DEBUG] 파일 저장 완료, 파일 존재 확인: {os.path.exists(file_path)}")
print("✅ 전압 데이터 저장 완료: results/data/voltage_data.csv")

# -------------------------
# 4. 종료
# -------------------------
h.helicsFederateDisconnect(fed)
h.helicsFederateFree(fed)
h.helicsCloseLibrary()
print("🔚 OpenDSS Federate 종료")