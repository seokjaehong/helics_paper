#!/bin/bash

echo "🚀 ESS 500kWh 시나리오 시작"
echo "============================="

# 0. 가상환경 활성화
echo "0. 가상환경 활성화..."
source /Users/seokjaehong/work/cosim-paper/venv/bin/activate

# 1. HELICS 브로커 시작
echo "1. HELICS 브로커 시작..."
helics_broker --federates=3 --loglevel=summary &
BROKER_PID=$!
echo "   브로커 PID: $BROKER_PID"

# 브로커 시작 대기
sleep 2

# 2. 페더레이트들 실행
echo "2. 페더레이트들 실행..."

echo "   - 태양광 페더레이트 시작..."
cd /Users/seokjaehong/work/cosim-paper/case_second
CASE_TYPE=500kwh python solar_fed.py &
SOLAR_PID=$!

echo "   - ESS 페더레이트 시작 (500kWh)..."
CASE_TYPE=500kwh ESS_CAPACITY=500 python ess_fed.py &
ESS_PID=$!

echo "   - OpenDSS 페더레이트 시작..."
CASE_TYPE=500kwh python opendss_fed.py &
DSS_PID=$!

echo "3. 시뮬레이션 실행 중..."
echo "   페더레이트 PID: Solar=$SOLAR_PID, ESS=$ESS_PID, DSS=$DSS_PID"

# 페더레이트 완료 대기
wait $SOLAR_PID
wait $ESS_PID
wait $DSS_PID

echo "4. 시뮬레이션 완료!"

# 5. 브로커 종료
echo "5. 브로커 종료..."
kill $BROKER_PID

echo "✅ ESS 500kWh 완료! 결과는 case_second/data/case500kwh/ 폴더에 저장되었습니다."
