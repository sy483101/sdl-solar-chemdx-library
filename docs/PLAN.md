# PLAN — ChemDX 태양전지 → SDL 라이브러리

> 범위·결정 근거 = `docs/intent/project-scope.md`. 상태 표기: `[ ]` 미착수 · `[~]` 진행 · `[x]` 완료(검증 결과는 worklog).
> 순서 원칙 = **① 2026년분 정량지표 숫자를 먼저**(연차보고서), ② 그 외는 같은 파이프라인을 다시 돌리는 것.

## 데이터 배치 (`$SOLAR_DATA_DIR`, git 밖)

```
$SOLAR_DATA_DIR/
├── raw/<스냅샷 YYYYMMDD>/          원본층 — 받은 응답 그대로
│   ├── manifest.json               받은 시각 · API 조건 · 건수 · 레코드별 해시 · 2026/그외 분류
│   └── <recordId>/record.json + files/…
└── library/<빌드 이름>/             라이브러리층 — 원본 + 코드 + 매핑으로 재생성
    ├── manifest.json               원본 스냅샷 · 이 레포 커밋 · sdl-prefill 커밋 · registry 판 · 매핑표 판
    ├── 2026/<ExperimentID>/        ① 정량지표용 — template.xlsx · metadata.json · DataArtifact/ · report.txt
    └── other/<ExperimentID>/       ② 그 외
```

## WS0 착수 준비 — 2026-10-14

- [x] 범위 합의(interview-me) → `docs/intent/project-scope.md`
- [x] 레포 · 규칙(`CLAUDE.md`) · 계획(이 문서) · `HANDOFF.md` · `.gitignore` · `.env.example`
- [x] private GitHub 레포 `sy483101/sdl-solar-chemdx-library` 생성·push(웹에서 빈 레포 → git push — 아래 함정)

## WS1 수집 — 원본층

- [ ] **T1.1 ChemDX API 조사** → `docs/chemdx-api.md`: 인증 · 엔드포인트 · 페이지 나누기 · 레코드 스키마 · 첨부(비정형) 받는 법 ·
      **기관 필드**(KRICT 판별 — 표기 변형 전수) · **생산 시점 필드**(2026 판별) · 서버 쪽 필터 가능 여부 · 호출 제한.
      입력 = API 문서·계정(사용자 제공). 완료 = 표본 몇 건을 실제로 받아 필드 목록과 대조.
- [ ] **T1.2 수집기** `fetch`: 벌크 수신 → KRICT 아닌 레코드는 쓰지 않음 → `raw/<스냅샷>/` 에 그대로 저장. 끊겨도 이어 받기(받은 것 건너뜀).
      완료 = 같은 조건 두 번 실행 시 매니페스트 해시 동일 · 타기관 레코드 0(전수 검사).
- [ ] **T1.3 분류** 2026 / 그 외 — 기준 필드는 열린 결정 D2. 매니페스트에 분류 기록(폴더를 나누지 않고 라이브러리에서 나눔).
      완료 = 분류별 건수 + 경계 사례(날짜 없음 등) 목록을 사용자 확인.

## WS2 매핑 — 매핑기

- [ ] **T2.1 필드 전수** → `mapping/fields.csv`: 필드 경로 · 채워진 비율 · 값 예 · 단위 표기 — 원본에서 자동 추출(손으로 고르지 않음).
- [ ] **T2.2 매핑표** → `mapping/chemdx_to_psc.csv`(git): 필드마다 하나로 —
      Metadata 칸 | Entity(원료 정보 등) | Step(StepType) | Parameter(StepType·이름·단위) | 결과(VocabAlias 이름·Kind·값/파일) | 버림(사유).
      **용어 = PSC registry**(기준 판을 표 머리에 기록). 레코드 하나가 공정 스텝 몇 개로 펼쳐지는지(소자 적층·층별 공정)는 T1.1 결과로 정한다.
- [ ] **T2.3 추가 후보** → `mapping/psc_additions.csv`: PSC registry 에 없는 StepType·파라미터·결과 이름 →
      sdl-prefill 받기 절차로 다음 PSC 판에(열린 결정 D5 — PSC 회신과 합칠지). **SDL-MPSP 추가 요청** → `mapping/sdl_mpsp_requests.csv`(정본 = 플랫폼).
- [ ] **T2.4 SDLEXO·MPSP 판정**: 새 StepType → SDLEXO · 새 결과/파라미터 → MPSP. 판정 방식 = 열린 결정 D4.
- [ ] **T2.5 registry 고리**: 추가 후보를 넣은 PSC registry 를 판 확정 전에 시험할 길 — sdl-prefill 에 범용 고리(예: registry 폴더 환경변수)를
      제안·커밋하거나, 확정 판만 쓰기. 이 레포에서 엔진을 바꿔 끼우지(monkeypatch) 않는다.

## WS3 변환기 — 라이브러리층

- [ ] **T3.1 record → draft**: 매핑표대로 sdl-prefill draft JSON(meta · entities · steps — 파라미터·결과·투입/산출) 생성.
      엔진 도우미(`draft.new_step`·`draft.new_entity`·`draft.validate`)를 쓴다. 첨부 파일 = draft 의 file 자리 + 바이트.
- [ ] **T3.2 draft → 세트 폴더**: `sheets.to_zip`(웹 내려받기와 같은 함수) 결과를 `library/<빌드>/<2026|other>/` 에 풀어 둔다 —
      웹 zip 과 바이트 수준으로 같은 형식이 목적. `validate` 알림은 `report.txt` + 빌드 요약.
- [ ] **T3.3 실험 ID** — 열린 결정 D1 에 따라 부여. 같은 원본 → 같은 ID(재빌드해도 안 바뀜).
- [ ] **T3.4 정량지표 집계** → `reports/indicator-<빌드>.md`(git, 숫자만): 세트 수 · `data_counts` 합(조성·구조·공정·분석) · 알림 남은 세트 수.
      완료 = 표본 세트를 sdl-prefill 웹에서 "레시피 불러오기"로 열어 같은 건수가 나오는지 대조.
- [ ] **T3.5 재현성**: 같은 원본·커밋으로 두 번 빌드 → 폴더 해시 동일(날짜 같은 비결정 칸이 있으면 고정 방법을 정함).

## WS4 JSON-LD 검토 (결정만 — 구현은 결정 뒤)

- [ ] 두 안 비교 문서 → 사용자 결정:
      (A) 5시트 열 → 자체 `@context`(SDLEXO·MPSP IRI)로 세트마다 `set.jsonld` ·
      (B) 플랫폼 적재기(`sdl-ontology-platform` `v05.load`)를 세트 단위로 돌려 ABOX 조각을 JSON-LD 로 직렬화(별도 프로세스 — 함정 참조).
      비교 축 = 플랫폼 ABOX 와 같은 뜻이 보장되는가 · 유지비(매핑 두 벌?) · 세트 폴더 하나만 보고 읽히는가.

## 열린 결정

| # | 질문 | 막히는 곳 |
|---|---|---|
| D1 | 가져온 세트의 실험 ID 체계 — sdl-prefill 웹 입력 PSC 실험(`PSC-EXP-날짜-NNN`, 서버 장부)과 겹치지 않게 | T3.3 |
| D2 | "2026년 생산" 판정 필드(실험일? 등록일?) · 날짜 없는 레코드 처리 | T1.3 |
| D3 | KRICT 판별 규칙(기관 표기 변형 · 공동연구 레코드) | T1.2 |
| D4 | SDLEXO·MPSP 판정 방식(플랫폼 J1·J3 와 같은 3판정 등) | T2.4 |
| D5 | PSC registry 추가분 반영 시점 — 대기 중인 PSC 회신과 합칠지 | T2.3 |
| D6 | 연차보고서 마감일 → ① 숫자가 필요한 날 | 전체 순서 |
| D7 | 레코드 → 실험 세트 단위(소자 하나 = 세트 하나?) | T2.2·T3.1 |
