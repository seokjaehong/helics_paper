import helics as h
import opendssdirect as dss
import csv
import json
from datetime import datetime

# Case 2: ESS 있음 - 태양광 + ESS 협조제어에 따른 전압 안정화 효과

fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreName(fedinfo, "dss_federate_case2")
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "--federates=3 --broker=localhost")

h.helicsFederateInfoSetTimeProperty(fedinfo, h.HELICS_PROPERTY_TIME_DELTA, 1.0)

fed = h.helicsCreateValueFederate("OpenDSS_Federate_Case2", fedinfo)

# subscribe
pv_sub = h.helicsFederateRegisterSubscription(fed, "PV_Output", "")
ess_sub = h.helicsFederateRegisterSubscription(fed, "ESS_Output", "")

# publish
pub = h.helicsFederateRegisterGlobalPublication(fed, "bus650_voltage", h.HELICS_DATA_TYPE_VECTOR, "")

h.helicsFederateEnterExecutingMode(fed)
print("🔌 Case 2: OpenDSS 페더레이트 시작 (ESS 있음)")

# OpenDSS 초기화
dss.Basic.ClearAll()
ieee13_path = "/Users/seokjaehong/work/cosim-paper/electricdss-tst/Version8/Distrib/IEEETestCases/13Bus/IEEE13Nodeckt.dss"
dss.Text.Command(f"Compile [{ieee13_path}]")

# PV 발전기 추가 (Bus 650에 연결)
dss.Text.Command("New Generator.PV1 Bus1=650 Phases=3 kV=4.16 kW=0 kvar=0 Model=1")

# ESS 추가 (Storage 요소로 모델링)
dss.Text.Command("New Storage.ESS1 Bus1=650 Phases=3 kV=4.16 kWrated=300 kWhrated=800 kWstored=400 State=Idling")

# 데이터 저장을 위한 리스트
voltage_data = []

for t in range(0, 24):
    pv_output = 0
    ess_output = 0

    # 태양광 출력 수신
    if h.helicsInputIsUpdated(pv_sub):
        pv_output = h.helicsInputGetDouble(pv_sub)
        dss.Text.Command(f"Edit Generator.PV1 kW={pv_output}")

    # ESS 출력 수신
    if h.helicsInputIsUpdated(ess_sub):
        ess_output = h.helicsInputGetDouble(ess_sub)
        # ESS 출력 적용 (양수: 방전, 음수: 충전)
        if ess_output > 0:
            # 방전 모드
            dss.Text.Command(f"Edit Storage.ESS1 kW={ess_output} State=Discharging")
        elif ess_output < 0:
            # 충전 모드
            dss.Text.Command(f"Edit Storage.ESS1 kW={abs(ess_output)} State=Charging")
        else:
            # 대기 모드
            dss.Text.Command("Edit Storage.ESS1 kW=0 State=Idling")

        print(f"[OpenDSS Case2] t={t:2d}h, PV={pv_output:6.1f}kW, ESS={ess_output:6.1f}kW")

    # 시뮬레이션 실행
    dss.Solution.Solve()

    # 전체 버스 전압 수집
    bus_names = dss.Circuit.AllBusNames()
    voltages_all = {}

    for bus_name in bus_names:
        dss.Circuit.SetActiveBus(bus_name)
        voltages = dss.Bus.puVoltages()
        if voltages:
            voltages_all[bus_name] = {
                'pu_voltages': voltages,
                'voltage_magnitude': abs(complex(voltages[0], voltages[1])) if len(voltages) >= 2 else abs(voltages[0])
            }

    # Bus 650 전압 (PV + ESS 연결점)
    dss.Circuit.SetActiveBus("650")
    bus650_voltages = dss.Bus.puVoltages()
    bus650_magnitude = abs(complex(bus650_voltages[0], bus650_voltages[1])) if len(bus650_voltages) >= 2 else abs(bus650_voltages[0])

    print(f"[OpenDSS Case2] t={t:2d}h, Bus650 전압: {bus650_magnitude:.4f} pu")

    # HELICS publish
    h.helicsPublicationPublishVector(pub, bus650_voltages)

    # 순 주입 전력 계산 (PV - ESS 충전 or PV + ESS 방전)
    net_power = pv_output + ess_output  # ess_output: 방전시 양수, 충전시 음수

    # 데이터 저장
    voltage_data.append({
        'time': t,
        'pv_output': pv_output,
        'ess_output': ess_output,
        'net_power': net_power,
        'bus650_voltage_pu': bus650_magnitude,
        'bus650_voltages_complex': bus650_voltages,
        'all_bus_voltages': voltages_all,
        'timestamp': datetime.now().isoformat()
    })

    # HELICS time request
    h.helicsFederateRequestTime(fed, t+1)

# 데이터 저장
with open('/Users/seokjaehong/work/cosim-paper/results/data/voltage_case2_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['time', 'pv_output', 'ess_output', 'net_power', 'bus650_voltage_pu', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in voltage_data:
        writer.writerow({
            'time': row['time'],
            'pv_output': row['pv_output'],
            'ess_output': row['ess_output'],
            'net_power': row['net_power'],
            'bus650_voltage_pu': row['bus650_voltage_pu'],
            'timestamp': row['timestamp']
        })

with open('/Users/seokjaehong/work/cosim-paper/results/data/voltage_case2_data.json', 'w') as jsonfile:
    json.dump(voltage_data, jsonfile, indent=2, ensure_ascii=False)

print("📊 Case 2 전압 데이터 저장 완료")
print(f"최대 전압: {max(d['bus650_voltage_pu'] for d in voltage_data):.4f} pu")
print(f"최소 전압: {min(d['bus650_voltage_pu'] for d in voltage_data):.4f} pu")

h.helicsFederateFinalize(fed)
h.helicsFederateDisconnect(fed)
h.helicsFederateFree(fed)
h.helicsCloseLibrary()
print("🔚 OpenDSS Case 2 페더레이트 종료")