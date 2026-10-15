# 데이터 건수 셈법 · 트리플 — dev-20261015c (other)

빌드 `dev-20261015c`(코드 c9c457c · sdl-prefill legacy-final-29-gf43d853-dirty · registry 0.5.3) · 이 스크립트 c9c457c-dirty · 플랫폼 적재기 v0.10-199-g072a9ae-dirty. 정의 = `docs/intent/data-count-methods.md`(재논의 10-15).

| 셈법 | 정의 | 건수 | 세트당 | 트리플 ÷ 건수 |
|---|---|---:|---:|---:|
| **A** 레시피 1 + 측정·분석 | 레시피 전체 1 + 측정·분석(대상·스텝·항목마다 1, 같은 자리 2회 이상이면 2) | 10,487 | 19.3 | 101.3 |
| **C** 트리플 | 플랫폼 적재기로 만든 그래프의 트리플 수 | 1,062,356 | 1,960.1 | 1.0 |
| **B** 설계인자 + 묶음 + 응답 | 고정·변동 인자 묶음 1 + 설계인자 각 1 + 응답(시편·항목마다 1, 같은 시편 반복이면 2) | 27,359 | 50.5 | 38.8 |
| (참고) 칸 단위(현행 `data_counts`) | 채워진 칸 = 1건(registry 기본값 포함) | 88,322 | 163.0 | 12.0 |
| (참고) 칸 단위 · 기본값 제외 | 연구자가 적은 칸만 | 55,724 | 102.8 | 19.1 |
| (참고) ML 표본 행 | 응답을 낸 측정(스텝·반복) 하나 = 1 | 7,822 | 14.4 | |

**B 내역** = 묶음 542 + 설계인자 조성 542(세트당 1.0) · 공정 16,330(30.1) + 응답 9,945(18.3). 범주 = 시트 위치(개체 정보 → 조성 · 파라미터 → 공정) · 구조 설계인자 없음(소자 구조 고정). 시편 = 측정 대상 개체 — 픽셀이 소자 개체 하나의 반복으로 들어가 있어 픽셀 10개도 2건(공통 원칙은 전 실험실 실데이터 확인 뒤).

세트 542 · 응답(측정 결과 행) 39,110(그중 파일 7,822) · 측정 항목 5,050 · 공정 칸 중 registry 기본값 32,598. 공정 파라미터 자리 130 중 ChemDX 값이 든 자리 67 · 세트마다 값이 달라지는 자리 43 → **설계인자 39**(랩 선언 0) · 묶음 4 · 개체 정보 설계인자 페로브스카이트.ChemicalFormula (Process Note 에만 있는 몰농도·첨가제 비율 등은 빠짐).

설계인자: BOTEL.material, ETLCD.thermalAnnealingTIme, ETLCT.spinCoatingSpeed, ETLCT.spinCoatingVolume, ETLCT.thermalAnnealingTemperature, ETLCT.thermalAnnealingTime, ETLSF.material, ETLSF.spinCoatingVolume, ETLSF.thermalAnnealingTemperature, HTL.additiveVolume, HTL.dopant1Name, HTL.dopant1Volume, HTL.dopant2Name, HTL.holeTransportMaterial, HTL.solvent, HTL.solventVolume, HTL.spinCoatingSpeed, HTL.spinCoatingTime, HTL.spinCoatingVolume, JV.activeArea, JV.antireflectionFIlmUsage, PVK.additive, PVK.solvent1, PVK.solvent1Volume, PVK.solvent2, PVK.solvent2Volume, PVK.spinCoatingSpeed, PVK.spinCoatingTime, PVKSF.concentration, PVKSF.material, PVKSF.spinCoatingSpeed, PVKSF.spinCoatingTime, PVKSF.spinCoatingVolume, PVKSF.thermalAnnealingTime, TOPEL.material

묶음으로 보낸 관측 변동: JV.scanDirection, PVK.laboratoryRelativeHumidity, PVK.laboratoryTemperature

## 트리플(플랫폼 적재기 v05.load — 미표현 0)

| 부분 | 트리플 |
|---|---:|
| 합계 | **1,062,356**(세트당 1,960) |
| Y 측정 결과 행 39,110 | 531,896(행당 13.6) |
| 공정 조건(Parameter) | 482,804 — 그중 registry 기본값 296,713 |
| 메타데이터·개체·스텝·투입/산출 | 47,656 |

적재 조건: 적재기가 세트 폴더를 그대로 읽음(read_set · 빈 Entity Type = 재료 — 플랫폼 PRJ22) · 파생 링크(추론) 제외. 부분별 트리플 = 그 행을 뺀 그래프와의 차이(공유 노드 탓 합이 약간 어긋날 수 있음).

**C 조건(10-15)** = 명시적·인스턴스(ABox) 트리플(VoID `void:triples`) — 이 빌드를 적재기로 만든 그래프에서 센다(추론 없음 · TBox 0 확인). 저장소(Fuseki)에서 세지 않는다(이름 없는 값 노드는 다시 적재하면 중복 · 다른 연도·온톨로지 그래프가 섞임). 판 = 위 머리의 플랫폼 커밋(적재기·aeonto·MPSP) + registry 판 — 그 해 숫자는 다시 세지 않는다.

| 구성(겹치지 않게) | 트리플 | 비율 |
|---|---:|---:|
| 값 노드(이름 없음, QuantityValue — 종류·숫자·단위) | 0 | 0.0% |
| 클래스 표시 rdf:type(이름 있는 노드) | 246,548 | 23.2% |
| MPSP 연결 rdfs:seeAlso | 138,588 | 13.0% |
| 나머지(개체·스텝·조건·결과의 값과 연결) | 677,115 | 63.7% |
| 공유 참조(랩·장비·스텝 종류·레시피 — 그래프 전체에 1번) | 105 | 0.0% |

클래스별 인스턴스(VoID classPartition, 실험 범위): QuantityValue 60,170 · ProcessParameter 48,670 · SetPointParameter 48,670 · Characterization 39,110 · Performance 31,288 · DataArtifact 7,822 · MaterialEntity 4,362 · Step 4,288 · Experiment 542 · ExperimentMetadata 542 · Workflow 542 · GroupStep 542
