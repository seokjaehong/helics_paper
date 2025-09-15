#!/bin/bash

# Case 2 (ESS 있음) 시나리오 실행 스크립트

echo "🚀 Case 2 (ESS 있음) 시나리오 시작"
echo "=================================="

# 가상환경 활성화
echo "0. 가상환경 활성화..."
source venv/bin/activate

# HELICS 브로커 백그라운드 실행
echo "1. HELICS 브로커 시작..."
helics_broker --federates=3 --core_type=zmq --loglevel=summary &
BROKER_PID=$!
echo "   브로커 PID: $BROKER_PID"

# 잠시 대기 (브로커 초기화)
sleep 2

# 페더레이트들 실행
echo "2. 페더레이트들 실행..."

echo "   - 태양광 페더레이트 시작..."
CASE_TYPE=2 python solar_fed.py &
SOLAR_PID=$!

echo "   - ESS 페더레이트 시작..."
CASE_TYPE=2 python ess_fed.py &
ESS_PID=$!

echo "   - OpenDSS 페더레이트 시작..."
CASE_TYPE=2 python opendss_fed.py &
DSS_PID=$!

echo "3. 시뮬레이션 실행 중..."
echo "   페더레이트 PID: Solar=$SOLAR_PID, ESS=$ESS_PID, DSS=$DSS_PID"

# 페더레이트 완료 대기
wait $SOLAR_PID
wait $ESS_PID
wait $DSS_PID

echo "4. 시뮬레이션 완료!"

# 브로커 종료
echo "5. 브로커 종료..."
kill $BROKER_PID 2>/dev/null

echo "✅ Case 2 완료! 결과는 data/ 폴더에 저장되었습니다."
echo "   분석 실행: cd analysis && python data_analyzer.py"
echo "   그래프 생성: cd plots && python plot_generator.py"