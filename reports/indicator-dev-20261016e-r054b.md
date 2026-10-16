# 정량지표 — dev-20261016e-r054b

원본 `20261014` · 코드 `b25874e` · sdl-prefill `legacy-final-41-g5c80c1a-dirty` · registry 0.5.4b · template 5sheet-1.3 · 참고 레시피 KRICT-PSC PSC-RCP-03

| 구분 | 세트 | **산정 건수 A**(세트당) | 조성 | 구조 | 공정 | 분석 | 칸 합계(참고) | 공정 중 manual | 알림 남은 세트 | 오류 · 미입력 · 확인 | 건너뜀 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 2026 | 170 | **3,490**(20.5) | 170 | 0 | 10,066 | 11,640 | 21,876 | 10,066 | 170 | 0 · 1344 · 180 | 0 |
| other | 2107 | **32,527**(15.4) | 2,107 | 0 | 75,747 | 97,085 | 174,939 | 75,747 | 2103 | 0 · 13728 · 5035 | 1,056 |

건너뛴 레코드(registry 에 담을 StepType 없음 등 — manifest `skipped`):

- other · 691 · 버퍼층 BCP 공정 값 없음 — 스핀(ETLSF)·증착(BUFEV) 중 무엇인지 랩 확인
- other · 140 · PVK 진공 증착 — registry PVK StepType 은 용액 공정
- other · 137 · 표면처리층(surface_treatment) — registry 에 그 층 StepType 없음
- other · 31 · ETL C60+PCBM — 한 블록에 여러 층(어느 층 값인지 랩 확인)
- other · 15 · ETL C60/SnO2 — 한 블록에 여러 층(어느 층 값인지 랩 확인)
- other · 13 · 열증착층(thermal_evaporation) — registry 에 그 층 StepType 없음
- other · 8 · 소자 구조 None — 랩 확인
- other · 6 · 버퍼층 PEIE 공정 값 없음 — 스핀(ETLSF)·증착(BUFEV) 중 무엇인지 랩 확인
- 그 밖 6가지 이유 · 15건
