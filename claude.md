# Claude Code 설정

이 파일은 개발 작업을 돕기 위한 Claude Code의 설정과 명령어들을 포함합니다.

## 공통 명령어

### 환경 설정
```bash
# 가상환경 활성화
source venv/bin/activate  # Windows의 경우: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 테스트 케이스 파일 다운로드
python down.py
```

### 페더레이트 실행
```bash
# 테스트용 개별 페더레이트 실행
python solar_fed.py
python ess_fed.py
python opendss_fed.py
```

### HELICS 브로커 (다중 페더레이트 시뮬레이션용)
```bash
# HELICS 브로커 시작 (다중 페더레이트 공동시뮬레이션 구현 시)
helics_broker --federates=3 --core_type=zmq
```

### 린트
```bash
# Python 코드 포맷팅
black *.py
# Python 린팅
flake8 *.py
```

### 타입 검사
```bash
# Python 타입 검사
mypy *.py
```

## 프로젝트 구조

```
cosim-paper/
├── README.md              # 프로젝트 문서
├── CLAUDE.md             # 이 설정 파일
├── requirements.txt      # Python 의존성
├── down.py              # IEEE 테스트 케이스 다운로드
├── opendss_fed.py       # OpenDSS 배전시스템 페더레이트
├── ess_fed.py           # 에너지저장시스템 페더레이트
├── solar_fed.py         # 태양광 PV 발전 페더레이트
├── electricdss-tst/     # 다운로드된 IEEE 테스트 케이스
└── venv/                # Python 가상환경
```

## 개발 노트

### HELICS 공동시뮬레이션 프레임워크
- 이 프로젝트는 분산 전력시스템 시뮬레이션을 위해 HELICS를 사용합니다
- 각 페더레이트는 독립적으로 실행되며 HELICS를 통해 통신합니다
- 페더레이트 간 통신에는 ZMQ 프로토콜이 사용됩니다
- 시간 동기화는 HELICS에서 처리됩니다

### 전력시스템 모델
- **OpenDSS**: 배전시스템 분석용 IEEE 13노드 테스트 피더
- **ESS**: 간단한 SOC 기반 에너지저장 제어 (500 kWh, 최대 200 kW)
- **태양광 PV**: 정현파 발전 모델 (최대 1 MW)

### 현재 제한사항 및 TODO 항목
- [ ] 페더레이트가 단일 동작으로 설정됨, 다중 페더레이트 설정 필요
- [ ] 적절한 HELICS 브로커 조정 구현
- [ ] 더 정교한 ESS 제어 알고리즘 추가
- [ ] PV 모델링을 위한 실제 기상 데이터 통합
- [ ] 시각화 및 데이터 로깅 추가
- [ ] 각 페더레이트에 대한 단위 테스트 구현
- [ ] 에러 핸들링 및 검증 추가

### 디버깅 팁
- HELICS 페더레이트 등록 및 발행/구독 매칭 확인
- electricdss-tst/에 IEEE 테스트 케이스 파일이 제대로 다운로드되었는지 확인
- 동기화 문제에 대한 페더레이트 로그 모니터링
- 자세한 로깅을 위해 HELICS_LOG_LEVEL 환경변수 사용

### 연구 맥락
이 코드베이스는 분산 에너지자원 통합 및 제어 전략에 초점을 맞춘 전력시스템 공동시뮬레이션의 학술 연구용으로 설계되었습니다.


### 수정사항 빠른 점검 체크리스트 (핵심 이슈)

- [x] **HELICS 상수명 오타 수정**
  - `h.helics_property_time_delta` → `h.HELICS_PROPERTY_TIME_DELTA`

- [x] **토픽 이름 불일치 해결**
  - OpenDSS가 구독: `"ess_control"`
  - ESS가 발행: `"ESS_Output"` → `"ess_control"`로 통일
  - ⇒ 이제 서로 신호가 전달됩니다

- [x] **OpenDSSDirect API 이름 수정**
  - `dss.Bus.PuVoltage()` → `dss.Bus.puVoltages()` (복수형, 소문자 p)

- [x] **HELICS 브로커 연결 설정 추가**
  - Core Init String에 브로커 주소 추가
  - `--federates=1` → `--federates=1 --broker=localhost`

- [x] **OpenDSS Storage 요소 문제 해결**
  - `Edit Storage.ess_kw kw=...` 명령을 주석 처리
  - IEEE13Node 기본 모델에는 Storage가 없음
  - 신호 수신 로그만 출력하도록 수정

- [x] **HELICS 종료 루틴 개선**
  - `Finalize → Disconnect → Free → CloseLibrary` 순서로 안전한 종료
  - 모든 페더레이트에서 종료 루틴 개선 완료

- [x] **발행 타입 확인**
  - 전압은 복수 값(실수 벡터)이므로 `HELICS_DATA_TYPE_VECTOR + helicsPublicationPublishVector` 사용 (OK)

## 추가사항_시나리오 

🔹 실험 시나리오

Case 1 (ESS 없음)

태양광 발전만 존재
낮: 발전 과잉 → 전압 과상승
저녁: 발전 급감 → 전압 저하 발생

Case 2 (ESS 있음)

낮: PV 출력 초과분을 ESS 충전으로 흡수
저녁: PV 부족분을 ESS 방전으로 보충
전압 변동폭이 감소하고, 전압 안정성이 향상됨

🔹 분석 지표

전압 프로파일 비교 (ESS 없음 vs ESS 있음)
전압 편차 (ΔVmax, ΔVmin)
SOC(State of Charge) 곡선

🔹 주요 결과 (핵심 메시지)

ESS가 재생에너지 출력 변동을 흡수하여 배전망 전압의 변동성을 완화.
ESS 없는 경우 대비, 전압의 overshoot/undershoot가 감소.
충·방전 로직이 단순한 프로토타입에서도 ESS 효과를 정성적으로 확인 가능.
🔹 논문 기여점

HELICS 기반으로 재생에너지–ESS–배전망을 통합한 Co-Simulation 구조 제안.
간단한 시뮬레이션으로 ESS가 전압 안정화에 기여하는 기본 효과 검증.
향후 고급 ESS 제어전략, 다양한 재생원/부하, 통신망 연계로 연구 확장 가능성 제시.


## 추가사항_변동추가
- 태양광,ess, opendss모두 시간해상도를 1초단위로 바꾸고, 전체시뮬레이션 시간을 3600건 (1시간) 단위로 수행해서 전압 변동을 추가해보기 
- 이를 위해 태양광 데이터 생성 방식도 좀 수정하기 
- 기대하는 결과 : 태양광만 썼을때보다 태양광+ess를 썼을때 전압변동이 더적은것을 기대함 
