import dss
from dss.examples import download_repo_snapshot

# electricdss-tst 리포지토리에서 예제 회로 다운로드
repo_path = download_repo_snapshot('.', repo_name='electricdss-tst', use_version=False)

# IEEE13Nodeckt 파일 경로
ieee13_path = repo_path / 'Version8' / 'Distrib' / 'IEEETestCases' / '13Bus' / 'IEEE13Nodeckt.dss'

print("IEEE13Nodeckt 위치:", ieee13_path)

# DSS-Python 으로 회로 불러오기
dss.Text.Command(f'redirect {ieee13_path}')
dss.ActiveCircuit.Solution.Solve()

# 예: Bus 650 전압 출력
dss.Circuit.SetActiveBus("650")
voltages = dss.Bus.puVoltages()
print("Bus 650 전압 (pu):", voltages)