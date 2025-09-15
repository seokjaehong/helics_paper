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
h.helicsFederateInfoSetCoreInitString(fedinfo, "")

# 시간 설정
h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)  # 1 second resolution

# Value Federate 생성
fed = h.helicsCreateValueFederate("OpenDSS Federate", fedinfo)

# publish (버스 전압들)
pub_650 = h.helicsFederateRegisterGlobalPublication(fed, "bus650_voltage", h.HELICS_DATA_TYPE_VECTOR, "")
pub_680 = h.helicsFederateRegisterGlobalPublication(fed, "bus680_voltage", h.HELICS_DATA_TYPE_VECTOR, "")
pub_692 = h.helicsFederateRegisterGlobalPublication(fed, "bus692_voltage", h.HELICS_DATA_TYPE_VECTOR, "")

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
while time < 300:  # 5분 (300초) 시뮬레이션
    # HELICS time request
    time = h.helicsFederateRequestTime(fed, time + 1)
    
    # 시간대별 부하 변동 추가 (더 현실적인 시뮬레이션)
    import math
    # 시간대별 부하 변동 (5분 동안의 일일 패턴) - 더 큰 변동
    time_hour = (time / 60) % 24  # 시간으로 변환
    base_load_factor = 0.6 + 0.4 * math.sin(2 * math.pi * time_hour / 24)  # 일일 패턴 (0.2~1.0)
    random_variation = 0.15 * math.sin(2 * math.pi * time / 30)  # 30초 주기 변동 (더 큰 변동)
    fast_variation = 0.1 * math.sin(2 * math.pi * time / 10)  # 10초 주기 빠른 변동
    load_factor = base_load_factor + random_variation + fast_variation
    
    # 부하 조정 (시간대별 변동)
    dss.Text.Command(f"Edit Load.671 kW=1155 kvar=660")  # 기본 부하
    dss.Text.Command(f"Edit Load.634a kW={160 * load_factor:.1f} kvar={110 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.634b kW={120 * load_factor:.1f} kvar={90 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.634c kW={120 * load_factor:.1f} kvar={90 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.645 kW={170 * load_factor:.1f} kvar={125 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.646 kW={230 * load_factor:.1f} kvar={132 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.692 kW={170 * load_factor:.1f} kvar={151 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.675a kW={485 * load_factor:.1f} kvar={190 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.675b kW={68 * load_factor:.1f} kvar={60 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.675c kW={290 * load_factor:.1f} kvar={212 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.611 kW={170 * load_factor:.1f} kvar={80 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.652 kW={128 * load_factor:.1f} kvar={86 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.670a kW={17 * load_factor:.1f} kvar={10 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.670b kW={66 * load_factor:.1f} kvar={38 * load_factor:.1f}")
    dss.Text.Command(f"Edit Load.670c kW={117 * load_factor:.1f} kvar={68 * load_factor:.1f}")

    # ESS 제어 명령 수신
    if h.helicsInputIsUpdated(sub):
        ess_power = h.helicsInputGetDouble(sub)
        if time % 60 == 0:  # 1분마다 출력
            print(f"[t={time}s ({time/60:.1f}min)] ESS 제어 명령 수신: {ess_power:.2f} kW")
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
            
            if time % 60 == 0:  # 1분마다 출력
                print(f"[t={time}s ({time/60:.1f}min)] Bus{bus_name} Voltage (pu): {voltage_magnitude:.6f} ∠{voltage_angle:.6f}")
            
        except Exception as e:
            if time % 60 == 0:  # 1분마다 출력
                print(f"[t={time}s ({time/60:.1f}min)] Bus{bus_name} 전압 읽기 실패: {e}")
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

    # HELICS publish (각 버스별로 전압 정보 전송)
    h.helicsPublicationPublishVector(pub_650, [bus_data.get("650", {}).get('magnitude', 0), bus_data.get("650", {}).get('angle', 0)])
    h.helicsPublicationPublishVector(pub_680, [bus_data.get("680", {}).get('magnitude', 0), bus_data.get("680", {}).get('angle', 0)])
    h.helicsPublicationPublishVector(pub_692, [bus_data.get("692", {}).get('magnitude', 0), bus_data.get("692", {}).get('angle', 0)])

# 데이터를 CSV 파일로 저장
print(f"[DEBUG] 저장할 데이터 개수: {len(voltage_data)}")
case_type = os.environ.get('CASE_TYPE', '1')
data_dir = f'/Users/seokjaehong/work/cosim-paper/case_second/data/case{case_type}'
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, 'voltage_data.csv')
print(f"[DEBUG] 파일 경로: {file_path}")

with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['time_seconds', 'bus650_magnitude', 'bus650_angle', 'bus680_magnitude', 'bus680_angle', 'bus692_magnitude', 'bus692_angle'])
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