#!/bin/bash

echo "🚀 Case 1 (ESS 없음) - 1초 단위 시뮬레이션 시작"
echo "=============================================="

# 0. 가상환경 활성화
echo "0. 가상환경 활성화..."
source /Users/seokjaehong/work/cosim-paper/venv/bin/activate

# 1. HELICS 브로커 시작
echo "1. HELICS 브로커 시작..."
helics_broker --federates=2 --loglevel=summary &
BROKER_PID=$!
echo "   브로커 PID: $BROKER_PID"

# 브로커 시작 대기
sleep 2

# 2. 페더레이트들 실행
echo "2. 페더레이트들 실행..."

echo "   - 태양광 페더레이트 시작..."
cd /Users/seokjaehong/work/cosim-paper/case_second
CASE_TYPE=1 python solar_fed.py &
SOLAR_PID=$!

echo "   - OpenDSS 페더레이트 시작..."
CASE_TYPE=1 python opendss_fed.py &
DSS_PID=$!

echo "3. 시뮬레이션 실행 중..."
echo "   페더레이트 PID: Solar=$SOLAR_PID, DSS=$DSS_PID"

# 페더레이트 완료 대기
wait $SOLAR_PID
wait $DSS_PID

echo "4. 시뮬레이션 완료!"

# 5. 브로커 종료
echo "5. 브로커 종료..."
kill $BROKER_PID

echo "✅ Case 1 완료! 결과는 case_second/data/ 폴더에 저장되었습니다."
echo "   분석 실행: cd case_second/analysis && python data_analyzer.py"
