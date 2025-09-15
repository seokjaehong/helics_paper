#!/bin/bash

echo "=== Case 2: 태양광 + ESS 사용 - 1초 단위 시뮬레이션 ==="
echo "시뮬레이션 시작 시간: $(date)"

# CASE_TYPE 환경변수 설정
export CASE_TYPE=2

# 결과 디렉토리 생성
mkdir -p /Users/seokjaehong/work/cosim-paper/results/case_second/case2_with_ess
mkdir -p /Users/seokjaehong/work/cosim-paper/results/data/case2

# 백그라운드에서 HELICS 브로커 시작
echo "HELICS 브로커 시작..."
helics_broker --federates=3 --core_type=zmq --broker_address=127.0.0.1 &
BROKER_PID=$!
sleep 3

# 백그라운드에서 각 페더레이트 실행
echo "OpenDSS 페더레이트 시작..."
python opendss_fed.py > /Users/seokjaehong/work/cosim-paper/results/case_second/case2_with_ess/opendss.log 2>&1 &
OPENDSS_PID=$!

sleep 2

echo "태양광 페더레이트 시작..."
python solar_fed.py > /Users/seokjaehong/work/cosim-paper/results/case_second/case2_with_ess/solar.log 2>&1 &
SOLAR_PID=$!

sleep 2

echo "ESS 페더레이트 시작..."
python ess_fed.py > /Users/seokjaehong/work/cosim-paper/results/case_second/case2_with_ess/ess.log 2>&1 &
ESS_PID=$!

# 모든 페더레이트 완료 대기
echo "시뮬레이션 실행 중... (약 1-2분 소요)"
wait $OPENDSS_PID
wait $SOLAR_PID
wait $ESS_PID

# 브로커 종료
kill $BROKER_PID 2>/dev/null

echo "시뮬레이션 완료 시간: $(date)"
echo "=== Case 2 완료 ==="
echo "결과 파일:"
echo "- 전압 데이터: /Users/seokjaehong/work/cosim-paper/results/data/case2/voltage_data.csv"
echo "- 태양광 데이터: /Users/seokjaehong/work/cosim-paper/results/data/case2/pv_output_data.csv"
echo "- ESS 데이터: /Users/seokjaehong/work/cosim-paper/results/data/case2/ess_output_data.csv"
echo "- 로그: /Users/seokjaehong/work/cosim-paper/results/case_second/case2_with_ess/"