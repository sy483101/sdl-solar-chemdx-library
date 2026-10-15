# 데이터 건수 셈법 · 트리플 — dev-20261014b (2026)

빌드 `dev-20261014b`(코드 8a20b79 · sdl-prefill legacy-final-27-gf5044e8-dirty · registry 0.5.3) · 이 스크립트 22f75e4-dirty · 플랫폼 적재기·J2 v0.10-192-g3d0d595-dirty. 정의 = `docs/intent/data-count-methods.md`(재논의 10-15).

| 셈법 | 정의 | 건수 | 세트당 | 트리플 ÷ 건수 |
|---|---|---:|---:|---:|
| **A** 레시피 1 + 측정·분석 | 레시피 전체 1 + 측정·분석(대상·스텝·항목마다 1, 같은 자리 2회 이상이면 2) | 3,490 | 20.5 | 97.5 |
| **C** 트리플 | 플랫폼 적재기로 만든 그래프의 트리플 수 | 340,431 | 2,002.5 | 1.0 |
| **B** 설계인자 + 묶음 + 응답 | 고정·변동 인자 묶음 1 + 설계인자 각 1 + 응답(시편·항목마다 1, 같은 시편 반복이면 2) | 6,695 | 39.4 | 50.8 |
| (참고) 칸 단위(현행 `data_counts`) | 채워진 칸 = 1건(registry 기본값 포함) | 28,398 | 167.0 | 12.0 |
| (참고) 칸 단위 · 기본값 제외 | 연구자가 적은 칸만 | 18,998 | 111.8 | 17.9 |
| (참고) ML 표본 행 | 응답을 낸 측정(스텝·반복) 하나 = 1 | 2,328 | 13.7 | |

**B 내역** = 묶음 170 + 설계인자 조성 170(세트당 1.0) · 공정 3,035(17.9) + 응답 3,320(19.5). 범주 = 시트 위치(개체 정보 → 조성 · 파라미터 → 공정) · 구조 설계인자 없음(소자 구조 고정). 시편 = 측정 대상 개체 — 픽셀이 소자 개체 하나의 반복으로 들어가 있어 픽셀 10개도 2건(공통 원칙은 전 실험실 실데이터 확인 뒤).

세트 170 · 응답(측정 결과 행) 11,640(그중 파일 2,328) · 측정 항목 1,680 · 공정 칸 중 registry 기본값 9,400. 공정 파라미터 자리 128 중 ChemDX 값이 든 자리 60 · 세트마다 값이 달라지는 자리 22 → **설계인자 19**(랩 선언 0) · 묶음 3 · 개체 정보 설계인자 페로브스카이트.ChemicalFormula (Process Note 에만 있는 몰농도·첨가제 비율 등은 빠짐).

설계인자: BOTEL.material, ETLCD.thermalAnnealingTIme, ETLSF.material, ETLSF.spinCoatingVolume, HTL.dopant1Name, HTL.dopant2Name, HTL.solvent, JV.activeArea, PVK.solvent1, PVK.solvent1Volume, PVK.solvent2, PVK.solvent2Volume, PVK.spinCoatingSpeed, PVK.spinCoatingTime, PVKSF.concentration, PVKSF.material, PVKSF.thermalAnnealingTime

묶음으로 보낸 관측 변동: JV.scanDirection, PVK.laboratoryRelativeHumidity, PVK.laboratoryTemperature

## 트리플(플랫폼 적재기 v05.load — 미표현 0)

| 부분 | 트리플 |
|---|---:|
| 합계 | **340,431**(세트당 2,003) |
| Y 측정 결과 행 11,640 | 158,304(행당 13.6) |
| 공정 조건(Parameter) | 164,174 — 그중 registry 기본값 85,144 |
| 메타데이터·개체·스텝·투입/산출 | 17,953 |

적재 조건: prefill 5sheet-1.1 → 플랫폼 v0.6 시트 이름만 바꿈 · Entity Type = 플랫폼 J2(페로브스카이트 재료 개체만 material 로 보탬). 부분별 트리플 = 그 행을 뺀 그래프와의 차이(공유 노드 탓 합이 약간 어긋날 수 있음).

**C 조건(10-15)** = 명시적·인스턴스(ABox) 트리플(VoID `void:triples`) — 이 빌드를 적재기로 만든 그래프에서 센다(추론 없음 · TBox 0 확인). 저장소(Fuseki)에서 세지 않는다(이름 없는 값 노드는 다시 적재하면 중복 · 다른 연도·온톨로지 그래프가 섞임). 판 = 위 머리의 플랫폼 커밋(적재기·aeonto·MPSP) + registry 판 — 그 해 숫자는 다시 세지 않는다.

| 구성(겹치지 않게) | 트리플 | 비율 |
|---|---:|---:|
| 값 노드(이름 없음, QuantityValue — 종류·숫자·단위) | 57,894 | 17.0% |
| 클래스 표시 rdf:type(이름 있는 노드) | 60,176 | 17.7% |
| MPSP 연결 rdfs:seeAlso | 44,252 | 13.0% |
| 나머지(개체·스텝·조건·결과의 값과 연결) | 178,004 | 52.3% |
| 공유 참조(랩·장비·스텝 종류·레시피 — 그래프 전체에 1번) | 105 | 0.0% |

클래스별 인스턴스(VoID classPartition, 실험 범위): QuantityValue 19,298 · ProcessParameter 16,588 · SetPointParameter 16,588 · Characterization 11,640 · Performance 9,312 · DataArtifact 2,328 · Step 1,518 · DeviceEntity 680 · ComponentEntity 672 · Experiment 170 · ExperimentMetadata 170 · MaterialEntity 170 · Workflow 170 · GroupStep 170
