#!/bin/bash

echo "🚀 ESS 용량별 시나리오 전체 실행"
echo "================================="

# 실행 권한 부여
chmod +x run_ess_*.sh

# Case 1 (ESS 없음) 실행
echo "📊 Case 1 (ESS 없음) 실행 중..."
./run_case1_second.sh
echo "✅ Case 1 완료"
echo ""

# ESS 100kWh 실행
echo "📊 ESS 100kWh 실행 중..."
./run_ess_100kwh.sh
echo "✅ ESS 100kWh 완료"
echo ""

# ESS 500kWh 실행
echo "📊 ESS 500kWh 실행 중..."
./run_ess_500kwh.sh
echo "✅ ESS 500kWh 완료"
echo ""

# ESS 1000kWh 실행
echo "📊 ESS 1000kWh 실행 중..."
./run_ess_1000kwh.sh
echo "✅ ESS 1000kWh 완료"
echo ""

# ESS 2000kWh 실행
echo "📊 ESS 2000kWh 실행 중..."
./run_ess_2000kwh.sh
echo "✅ ESS 2000kWh 완료"
echo ""

echo "🎉 모든 ESS 용량별 시나리오 완료!"
echo "📈 분석 실행: cd analysis && python capacity_analyzer.py"
