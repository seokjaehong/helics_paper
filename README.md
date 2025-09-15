# 공동시뮬레이션 논문 - 전력시스템 모델링

이 프로젝트는 HELICS (Hierarchical Engine for Large-scale Infrastructure Co-Simulation)를 사용하여 다양한 전력시스템 구성요소와 모델을 통합하는 공동시뮬레이션 프레임워크를 구현합니다.

## 프로젝트 개요

이 프로젝트는 세 개의 주요 페더레이트로 구성된 분산 전력시스템 시뮬레이션을 보여줍니다:

1. **OpenDSS 페더레이트** (`opendss_fed.py`) - 배전시스템 모델링
2. **ESS 페더레이트** (`ess_fed.py`) - 에너지저장시스템 제어
3. **태양광 PV 페더레이트** (`solar_fed.py`) - 재생에너지 발전 모델링

## 시스템 구조

시뮬레이션은 서로 다른 페더레이트 간의 메시지 전달과 동기화를 위해 HELICS를 사용합니다:

```
태양광 PV 페더레이트 → ESS 페더레이트
       ↓               ↓
    PV_Output    ESS_Output
       ↓               ↓
    OpenDSS 페더레이트 (조류계산 분석)
```

## 파일 설명

### 핵심 시뮬레이션 파일

- **`opendss_fed.py`**: OpenDSS를 사용하는 메인 배전시스템 페더레이트
  - IEEE 13노드 테스트 피더 로드
  - 조류계산 분석 수행
  - 버스 전압 데이터 발행
  - ESS 제어 명령 구독

- **`ess_fed.py`**: 에너지저장시스템 페더레이트
  - 간단한 SOC(충전상태) 기반 제어
  - PV 출력 > 500 kW일 때 충전
  - PV 출력 < 200 kW일 때 방전
  - ESS 전력 출력 발행

- **`solar_fed.py`**: 태양광 PV 발전 페더레이트
  - 정현파 태양광 발전 모델 (24시간 주기)
  - 최대 출력: 1 MW
  - PV 전력 출력 발행

### 유틸리티 파일

- **`down.py`**: electricdss-tst 저장소에서 IEEE 테스트 케이스 파일 다운로드
- **`requirements.txt`**: Python 의존성 목록

## 의존성

프로젝트에는 다음 Python 패키지가 필요합니다:

```
cffi==2.0.0
click==8.2.1
dss-python==0.15.7
dss_python_backend==0.14.5
helics==3.6.1
numpy==2.2.6
opendssdirect.py==0.9.4
pycparser==2.23
strip-hints==0.1.13
typing_extensions==4.15.0
```

## 설치 방법

1. 저장소 클론
2. 가상환경 생성:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows의 경우: venv\Scripts\activate
   ```
3. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
4. 테스트 케이스 파일 다운로드:
   ```bash
   python down.py
   ```

## 사용법

### 개별 페더레이트 실행

각 페더레이트는 테스트를 위해 독립적으로 실행할 수 있습니다:

```bash
# 태양광 PV 페더레이트
python solar_fed.py

# ESS 페더레이트
python ess_fed.py

# OpenDSS 페더레이트
python opendss_fed.py
```

### 공동시뮬레이션 실행

완전한 공동시뮬레이션을 위해서는:

1. HELICS 브로커 시작
2. 모든 페더레이트를 동시에 실행
3. 각 페더레이트는 HELICS를 통해 동기화됨

**참고**: 현재 구현에서는 각 페더레이트가 단일 페더레이트 동작으로 설정되어 있습니다. 다중 페더레이트 공동시뮬레이션을 위해서는 HELICS 코어 초기화 문자열을 올바른 페더레이트 수를 반영하도록 업데이트해야 합니다.

## 기술적 세부사항

### HELICS 설정

- 통신 프로토콜: ZMQ
- 시간 간격: 1.0초
- 시뮬레이션 기간: 24시간 (태양광/ESS) 또는 10 시간 단계 (OpenDSS)

### OpenDSS 통합

- IEEE 13노드 테스트 피더 사용
- Bus 650 전압 모니터링
- ESS 명령을 통한 저장 요소 제어 지원

### ESS 모델

- 용량: 500 kWh
- 최대 전력: 200 kW
- 초기 SOC: 50%
- 간단한 임계값 기반 제어 로직

### 태양광 PV 모델

- 24시간에 걸친 정현파 발전 프로파일
- 정오 최대 발전량: 1 MW
- 야간 시간 동안 발전량 0

## 향후 개선 사항

개발 가능한 영역:

1. 다중 페더레이트 조정 및 적절한 HELICS 브로커 설정
2. 더 정교한 ESS 제어 알고리즘
3. PV 모델링을 위한 실제 기상 데이터 통합
4. 고급 전력시스템 분석 및 시각화
5. 추가 전력시스템 구성요소(부하, 발전기 등) 통합
6. 성능 최적화 및 확장성 개선

## 연구 맥락

이 코드베이스는 분산 전력시스템 모델링 및 제어 전략에 초점을 맞춘 학술 논문 발표를 위한 전력시스템 공동시뮬레이션 연구 목적으로 개발된 것으로 보입니다.