# 실험 시나리오 및 결과 분석

## 🔬 실험 개요

이 폴더에는 HELICS 기반 전력시스템 공동시뮬레이션의 두 가지 주요 시나리오와 결과 분석 도구들이 포함되어 있습니다.

### 연구 목적
- 재생에너지(태양광) 출력 변동이 배전계통 전압에 미치는 영향 분석
- 에너지저장시스템(ESS)의 전압 안정화 효과 검증
- HELICS 기반 분산 시뮬레이션 프레임워크 성능 평가

## 📁 폴더 구조

```
results/
├── README.md                    # 이 파일
├── case1_no_ess/               # Case 1: ESS 없음 시나리오
│   ├── solar_fed_case1.py      # 태양광 페더레이트
│   └── opendss_fed_case1.py    # OpenDSS 페더레이트
├── case2_with_ess/             # Case 2: ESS 있음 시나리오
│   ├── solar_fed_case2.py      # 태양광 페더레이트
│   ├── ess_fed_case2.py        # ESS 페더레이트
│   └── opendss_fed_case2.py    # OpenDSS 페더레이트
├── data/                       # 시뮬레이션 결과 데이터
│   ├── *_case1_data.csv        # Case 1 결과
│   ├── *_case2_data.csv        # Case 2 결과
│   └── *.json                  # JSON 형식 데이터
├── analysis/                   # 데이터 분석 도구
│   ├── data_analyzer.py        # 통계 분석
│   └── metrics_summary.json    # 분석 결과 요약
└── plots/                      # 그래프 및 시각화
    ├── plot_generator.py       # 그래프 생성 도구
    └── *.png                   # 생성된 그래프들
```

## 🌟 시나리오 설명

### Case 1: ESS 없음
**목적**: 재생에너지 변동성이 전력계통에 미치는 기본 영향 분석

**구성**:
- **태양광 페더레이트**: 24시간 사인파 기반 발전 모델 (최대 1.2MW)
- **OpenDSS 페더레이트**: IEEE 13-node 테스트 피더 + PV 발전기

**특징**:
- 낮 시간: 태양광 발전량 증가 → 전압 과상승 가능성
- 저녁/밤: 태양광 발전량 감소 → 전압 저하 가능성
- 구름 등에 의한 PV 출력 변동성 모델링

**실행 방법**:
```bash
# 터미널 1: HELICS 브로커
helics_broker --federates=2 --core_type=zmq

# 터미널 2: 태양광 페더레이트
cd results/case1_no_ess
python solar_fed_case1.py

# 터미널 3: OpenDSS 페더레이트
cd results/case1_no_ess
python opendss_fed_case1.py
```

### Case 2: ESS 있음
**목적**: ESS 도입을 통한 전압 안정화 효과 분석

**구성**:
- **태양광 페더레이트**: Case 1과 동일한 발전 프로파일
- **ESS 페더레이트**: 개선된 충방전 제어 로직 (800kWh, 300kW)
- **OpenDSS 페더레이트**: IEEE 13-node + PV + ESS Storage

**ESS 제어 로직**:
- **충전 조건**: PV > 800kW 이고 SOC < 90%
- **방전 조건**: PV < 300kW 이고 SOC > 10%
- **대기 모드**: 위 조건 외의 경우

**실행 방법**:
```bash
# 터미널 1: HELICS 브로커
helics_broker --federates=3 --core_type=zmq

# 터미널 2: 태양광 페더레이트
cd results/case2_with_ess
python solar_fed_case2.py

# 터미널 3: ESS 페더레이트
cd results/case2_with_ess
python ess_fed_case2.py

# 터미널 4: OpenDSS 페더레이트
cd results/case2_with_ess
python opendss_fed_case2.py
```

## 📊 분석 지표

### 전압 품질 지표
- **전압 범위**: 최대/최소 전압값 (pu)
- **전압 변동폭**: Vmax - Vmin
- **전압 표준편차**: 전압 변동의 통계적 측정
- **과전압/저전압 발생 횟수**: 1.05pu 초과 / 0.95pu 미만

### ESS 운영 지표
- **총 충전/방전 에너지**: kWh 단위
- **SOC 활용도**: 최대-최소 SOC 차이
- **제어 모드 분포**: 충전/방전/대기 시간 비율

### 개선 효과 지표
- **전압 안정화**: 변동폭 감소율 (%)
- **전압 품질**: 표준편차 감소율 (%)
- **계통 안정성**: 과/저전압 발생 감소 횟수

## 🔧 분석 도구 사용법

### 1. 데이터 분석
```bash
cd results/analysis
python data_analyzer.py
```

**출력**:
- 터미널에 분석 결과 요약 출력
- `metrics_summary.json` 파일에 상세 지표 저장

### 2. 그래프 생성
```bash
cd results/plots
python plot_generator.py
```

**생성되는 그래프**:
- `solar_profile.png`: 태양광 출력 프로파일
- `voltage_comparison.png`: Case 1 vs Case 2 전압 비교
- `power_balance.png`: 전력 수급 균형 (Case 2)
- `voltage_statistics.png`: 전압 분포 통계
- `ess_soc_profile.png`: ESS SOC 및 충방전 프로파일

## 🎯 기대 결과

### 가설
1. **Case 1**: 태양광 출력 변동으로 인한 전압 변동성 증가
2. **Case 2**: ESS 도입으로 전압 변동성 완화 및 안정성 개선

### 예상 효과
- 전압 변동폭 10-30% 감소
- 과전압/저전압 발생 빈도 감소
- 전압 표준편차 감소를 통한 전압 품질 개선

## 🚀 실행 전 체크리스트

### 필수 조건
- [ ] Python 가상환경 활성화
- [ ] 필수 패키지 설치: `pip install -r requirements.txt`
- [ ] IEEE 테스트 케이스 다운로드: `python down.py`
- [ ] HELICS 브로커 설치 및 경로 설정

### 실행 순서
1. **HELICS 브로커 먼저 시작** (각 시나리오별 페더레이트 수에 맞게)
2. **모든 페더레이트를 거의 동시에 실행** (30초 이내)
3. **24시간 시뮬레이션 완료 대기**
4. **데이터 분석 및 그래프 생성**

### 문제 해결
- **브로커 연결 실패**: 방화벽 설정 확인, 포트 충돌 확인
- **데이터 파일 없음**: 시뮬레이션이 완전히 끝났는지 확인
- **그래프 생성 실패**: matplotlib 설치 확인, 한글 폰트 설정 확인

## 📈 논문 활용 방안

### 핵심 기여점
1. **HELICS 기반 분산 시뮬레이션 프레임워크** 제시
2. **재생에너지-ESS-배전망 통합 모델링** 구현
3. **ESS의 전압 안정화 효과** 정량적 검증

### 확장 가능성
- 다양한 ESS 제어 알고리즘 비교
- 실제 기상 데이터 적용
- 다중 재생에너지원 및 부하 모델링
- 통신 지연 및 신뢰성 영향 분석
- 경제성 분석 통합

### 결과 해석 시 고려사항
- IEEE 13-node는 간소화된 테스트 모델
- 실제 계통 운영 조건과의 차이
- ESS 제어 로직의 단순화
- 시뮬레이션 시간 간격(1시간)의 한계

## 📞 지원

문제 발생 시:
1. `CLAUDE.md` 파일의 디버깅 팁 참조
2. HELICS 로그 레벨을 높여서 상세 로그 확인
3. 개별 페더레이트 단독 테스트부터 시작