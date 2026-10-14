# 데이터 건수 셈법 · 트리플 — dev-20261014b (2026)

빌드 `dev-20261014b`(코드 8a20b79 · sdl-prefill legacy-final-27-gf5044e8-dirty · registry 0.5.3) · 이 스크립트 e47a5d6-dirty · 플랫폼 적재기·J2 v0.10-192-g3d0d595-dirty. 정의 = `docs/intent/data-count-methods.md`.

| 셈법 | 정의 | 건수 | 세트당 | 트리플 ÷ 건수 |
|---|---|---:|---:|---:|
| A 칸 단위(현행 `data_counts`) | 채워진 칸 = 1건(registry 기본값 포함) | 28,398 | 167.0 | 12.0 |
| A′ 칸 단위 · 기본값 제외 | 연구자가 적은 칸만 | 18,998 | 111.8 | 17.9 |
| B 범주 + Y(반복마다) | 조성·구조·공정 각 1 + Y 측정 결과 행마다 1 | 12,150 | 71.5 | 28.0 |
| C X 1 + Y(항목마다) | X 1 + Y 측정 항목(스텝·결과 이름)마다 1 | 1,850 | 10.9 | 184.0 |
| (참고) ML 표본 행 | Y 를 낸 측정(스텝·반복) 하나 = 1 | 2,328 | 13.7 | |

세트 170 · Y 측정 결과 행 11,640(그중 파일 2,328) · Y 측정 항목 1,680 · 공정 칸 중 registry 기본값 9,400. 공정 파라미터 자리 128 중 ChemDX 값이 든 자리 60 · **세트마다 값이 달라지는 자리 22**(이름 20) (Process Note 에만 있는 몰농도·첨가제 비율 등은 빠짐):

BOTEL.material, ETLCD.thermalAnnealingTIme, ETLSF.material, ETLSF.spinCoatingVolume, HTL.dopant1Name, HTL.dopant2Name, HTL.solvent, JV.activeArea, JV.scanDirection, PVK.laboratoryRelativeHumidity, PVK.laboratoryTemperature, PVK.solvent1, PVK.solvent1Volume, PVK.solvent2, PVK.solvent2Volume, PVK.spinCoatingSpeed, PVK.spinCoatingTime, PVKSF.concentration, PVKSF.material, PVKSF.thermalAnnealingTime

## 트리플(플랫폼 적재기 v05.load — 미표현 0)

| 부분 | 트리플 |
|---|---:|
| 합계 | **340,431**(세트당 2,003) |
| Y 측정 결과 행 11,640 | 158,304(행당 13.6) |
| 공정 조건(Parameter) | 164,174 — 그중 registry 기본값 85,144 |
| 메타데이터·개체·스텝·투입/산출 | 17,953 |

적재 조건: prefill 5sheet-1.1 → 플랫폼 v0.6 시트 이름만 바꿈 · Entity Type = 플랫폼 J2(페로브스카이트 재료 개체만 material 로 보탬). 부분별 트리플 = 그 행을 뺀 그래프와의 차이(공유 노드 탓 합이 약간 어긋날 수 있음).
