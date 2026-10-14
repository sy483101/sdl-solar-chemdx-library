# 데이터 건수 셈법 · 트리플 — dev-20261014b (2026)

빌드 `dev-20261014b`(코드 8a20b79 · sdl-prefill legacy-final-27-gf5044e8-dirty · registry 0.5.3) · 이 스크립트 0acdc2f-dirty · 플랫폼 적재기 v0.10-192-g3d0d595-dirty. 정의·논의 = `docs/intent/data-count-methods.md`.

| 셈법 | 정의 | 건수 | 세트당 | 트리플 ÷ 건수 |
|---|---|---:|---:|---:|
| A 칸 단위(현행 `data_counts`) | 채워진 칸 = 1건(registry 기본값 포함) | 28,398 | 167 | 12.0 |
| A′ 칸 단위 · 기본값 제외 | 연구자가 적은 칸만 | 18,998 | 112 | 17.9 |
| B 범주 묶음 + Y | 조성·구조·공정 있으면 각 1건 + Y 값마다 1건 | 9,652 | 57 | 35.2 |
| C X 한 건 + Y | 세트당 X 1건 + Y 값마다 1건 | 9,482 | 56 | 35.8 |
| (참고) B·C + 곡선 파일 | 원자료 파일도 1건씩 | 11,980 · 11,810 | | |
| (참고) ML 표본 행 | Y 를 낸 측정(스텝·반복) 하나 = 1건 | 2,328 | 14 | |

세트 170 · Y 값 9,312 · 곡선 파일 2,328 · 공정 칸 중 registry 기본값 9,400. 공정 파라미터 자리 128 중 ChemDX 값이 든 자리 60 · **세트마다 값이 달라지는 자리 22** (Process Note 에만 있는 몰농도·첨가제 비율 등은 빠짐):

BOTEL.material, ETLCD.thermalAnnealingTIme, ETLSF.material, ETLSF.spinCoatingVolume, HTL.dopant1Name, HTL.dopant2Name, HTL.solvent, JV.activeArea, JV.scanDirection, PVK.laboratoryRelativeHumidity, PVK.laboratoryTemperature, PVK.solvent1, PVK.solvent1Volume, PVK.solvent2, PVK.solvent2Volume, PVK.spinCoatingSpeed, PVK.spinCoatingTime, PVKSF.concentration, PVKSF.material, PVKSF.thermalAnnealingTime

## 트리플(플랫폼 적재기 v05.load — 미표현 0)

| 부분 | 트리플 |
|---|---:|
| 합계 | **339,921**(세트당 2,000) |
| Y 값 9,312 | 139,680(값당 15.0) |
| 곡선 파일 2,328 | 18,624 |
| 공정 조건(Parameter) | 164,174 — 그중 registry 기본값 85,144 |
| 메타데이터·개체·스텝·투입/산출 | 17,443 |

적재 조건: prefill 5sheet-1.1 → 플랫폼 v0.6 시트 이름만 바꿈 · Entity Type 잠정(페로브스카이트 = material · 완성소자 = device · 나머지 = component — 플랫폼 J2 판정 아님). 부분별 트리플 = 그 행을 뺀 그래프와의 차이(공유 노드 탓 합이 약간 어긋날 수 있음).
