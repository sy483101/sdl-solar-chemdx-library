# sdl-solar-chemdx-library — ChemDX 태양전지 데이터 → SDL 라이브러리

@HANDOFF.md

> **작업 시작 시: `HANDOFF.md`(지금·다음 할 일)와 아래 "함정" 절을 먼저 읽을 것.**
> **작업 종료 시: 아래 "커밋 주기" 절차대로 마감.**
> 범위·결정의 근거 = `docs/intent/project-scope.md`(2026-10-14 interview-me 합의) · 계획 = `docs/PLAN.md`.

## 개요

- 외부 DB 플랫폼 **ChemDX** 의 태양전지 데이터를 API 로 벌크로 받아 **KRICT 데이터만** 남기고,
  **① 2026년 생산분**(전략연구사업 정량지표용)과 **② 그 외**(①과 합쳐 거대 KG 연구용)로 나눠 관리한다.
- 3층 구조 — **원본층**(받은 그대로) → **라이브러리층**(세트별 폴더) → ABOX층(Fuseki). **이 레포의 범위 = 라이브러리층까지.**
  ABOX화(빌더·Fuseki 적재)는 `sdl-ontology-platform` 의 일(적재기 `v05.load` 가 5시트 패키지를 읽는다).
- 라이브러리 세트 = **sdl-prefill 이 내려주는 zip 과 같은 폴더 구조**: `{ExperimentID}/template.xlsx`(5시트) · `metadata.json` ·
  `DataArtifact/`(비정형 데이터) · `report.txt`(남은 알림). JSON-LD 는 검토 대상(PLAN WS4).
- 정량지표: **세트 수 = 폴더 수**, **건수 = sdl-prefill `sheets.data_counts`**(웹 입력분과 같은 셈법 — 조성·구조·공정·분석).

## 데이터 규칙 (YOU MUST)

- **원본·라이브러리 데이터는 git 에 넣지 않는다**(수 GB). 위치 = 환경변수 `SOLAR_DATA_DIR`(이 맥) — 레포 안을 가리키지 말 것.
  git 에 들어가는 것 = 코드 · 매핑표 · 문서 · 집계 결과(숫자만).
- **원본층 = 두 단**(2026-10-14 사용자 결정 — 이전 "타기관 레코드 디스크에 안 씀" 규칙을 바꿈): **1차 `raw/1_full/`** = API 응답 전체 그대로(타기관 포함) ·
  **2차 `raw/2_krict/`** = 1차에서 KRICT 만 골라 복사. 라이브러리층은 **2차만** 읽는다 — 타기관 레코드는 2차·라이브러리·git(집계 포함)에 넣지 않는다.
- 원본층 = 받은 응답 그대로(가공·정리 금지). 라이브러리층 = 원본 + 코드 + 매핑 + prefill 커밋으로 **다시 만들 수 있어야** 한다 — 손편집 금지.
  빌드마다 매니페스트에 원본 스냅샷 · 이 레포 커밋 · prefill 커밋 · registry 판 · 매핑표 판을 남긴다.
- 비밀(ChemDX API 키 등)은 `.env`(gitignore) — `.env.example` 에 이름만.

## sdl-prefill 의존 (YOU MUST)

- 5시트 생성·폴더 구조·검증·건수는 **sdl-prefill v05 엔진**(`sdl_platform/v05/draft.py`·`sheets.py`)을 그대로 쓴다 — 옆 체크아웃
  `SDL_PREFILL_DIR`(기본 `../sdl-prefill`)을 import 경로로. **엔진을 이 레포에 복사하거나 고치지 않는다.**
  범용 고리가 필요하면(예: registry 를 `data/registry/` 밖에서 읽기) sdl-prefill 에 일반 커밋으로 넣는다(그쪽 규칙 — make test 등).
- 변환기가 만드는 것은 **draft JSON 까지**(웹 화면이 만드는 것과 같은 모양). 그 뒤는 엔진(`sheets.to_zip` 등)이 한다.
- 용어 = **PSC 랩 registry**(sdl-prefill `data/registry/v<판>/sdl_registry_v<판>_KRICT-PSC.xlsx`)를 따른다. 없는 용어는 추가 후보로 모아
  sdl-prefill 의 **받기 절차**(`scripts/registry_intake.py`)로 다음 PSC 판에 반영 — 이 레포에서 registry 파일을 직접 고치지 않는다.
- MPSP 로 부족한 개념 = **SDL-MPSP 추가 발행 요청 목록**으로 — 정본은 `sdl-ontology-platform`(2026-10-01 이관). 여기서 발행하지 않는다.

## 문서 4범주 · 작업 규칙

- 규칙·함정 = 이 파일 · 지금 = `HANDOFF.md` · 계획 = `docs/PLAN.md` · 이력 = `docs/archive/worklog.md`(append-only) · 합의 기록 = `docs/intent/`.
- `main` 직접 작업. 시작 `git pull` / 종료 `commit && push`.
- **커밋 주기(YOU MUST)**: WP 종료 또는 반나절 1회 중 먼저 오는 시점 — HANDOFF 갱신 + worklog 에 보고(완료 Task·검증·다음 할 일) append →
  테스트가 있으면 green 확인 → `commit && push`.
- 결정이 필요한 곳(PLAN "열린 결정")은 추론으로 메우지 말고 사용자에게 묻는다(interview-me).
- 모델 정책: 판단·설계·계획·리뷰·고도코딩 = 메인 루프. 조사·기계적 구현·병렬 작업 = 서브에이전트.

## 함정

- **패키지 이름 `sdl_platform` 이 셋**: sdl-prefill · sdl-ontology-platform · onto-nl2sparql 이 모두 같은 이름을 쓴다. 이 맥의 PYTHONPATH 에는
  onto-nl2sparql 것이 잡혀 있다(sdl-prefill HANDOFF 10-06) → 이 레포 프로세스는 `SDL_PREFILL_DIR` 을 `sys.path` **맨 앞**에 두고 시작 시
  `sdl_platform.__file__` 이 sdl-prefill 쪽인지 확인한다. 플랫폼 코드(예: JSON-LD 검토에서 `v05.load`)가 필요하면 **별도 프로세스**(그쪽 venv·경로)로.
- sdl-prefill 의 registry 경로는 `paths.REGISTRY_DIR` 에 고정(환경변수 없음) — 다른 판·추가 후보를 시험하려면 고리가 필요하다(PLAN WS2).
- sdl-prefill 의 실험 ID 장부(`idbook`)는 **서버**(borona·NCP)에 있다 — 이 레포는 오프라인 변환이라 장부에 기록되지 않는다. ID 겹침 = 열린 결정 D1.
- 개발 Mac 의 Python = 3.9(sdl-prefill `requirements.txt` 판). 엔진을 import 하므로 같은 환경을 쓴다.
- 연구원망(KREONet)은 밖으로 나가는 SSH(22)를 막는다 — GitHub 는 HTTPS 로.
- 연구원 DNS(203.250.2.5)가 `api.github.com` 을 SERVFAIL(10-14 — `github.com` 은 정상, IP 직접 접속도 정상) → `gh` 로그인·레포 생성 불가.
  git push(HTTPS·키체인)는 된다. GitHub API 가 필요한 일(PR·이슈·레포 생성)은 웹에서 하거나 DNS 가 풀린 뒤에.
