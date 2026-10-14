# 범위 합의 — 2026-10-14 (interview-me, sdl-prefill 세션)

## 계기

전략연구사업 데이터 건수를 연차보고서 전에 일부 채워야 한다. 태양전지 쪽은 올해 실험 데이터를 별도 DB 플랫폼(ChemDX)에서 가져온다.

## 합의한 내용

- **결과물**: ChemDX API 벌크 수신 → KRICT 만 필터 → ① 2026년 생산분 / ② 그 외 분리 보관 → 매핑기(PSC registry 용어 · StepType→SDLEXO ·
  VocabAlias→MPSP, 없는 것만 추가) → 변환기(레코드 → sdl-prefill draft → 엔진) → **라이브러리**(세트별 폴더 = template.xlsx + DataArtifact, JSON-LD 검토).
- **3층 구조**: 원본층(레포지터리 — 받은 그대로) → 라이브러리층(세트별 폴더) → ABOX층(빌더 → Fuseki). **이번 작업 = 라이브러리까지.**
- **쓰는 곳**: ① = 전략연구사업 정량지표(연차보고서) · ① + ② = 거대 KG 추가 연구.
- **성공**: 세트 수 = 폴더 수 · 건수 = sdl-prefill `data_counts` 셈법(웹 입력분과 같은 셈) · 원본 + 코드 + 매핑 + prefill 커밋으로 라이브러리 재생성 가능.
- **제약**: 데이터(수 GB)는 git 밖, 맥에만 · git 에는 코드와 매핑기만 · prefill 엔진은 고치지 않고 라이브러리로 씀 · 타기관 데이터는 보관하지 않음.
- **범위 밖**: 빌더·ABOX·Fuseki 적재 · sdl-prefill 웹 화면 연동 · JSON-LD 확정(검토만).

## 레포를 나눈 이유

- 변환기·매핑기는 **ChemDX 태양전지 전용** — sdl-prefill(웹 입력 서비스) 엔진에 넣을 기능이 아니다(사용자).
- sdl-prefill `main` → `release` 는 공개 NCP 서버·borona 실서버로 나간다 — 외부 DB 전용 코드·맥 경로 설정이 서비스 배포물에 섞인다.
- sdl-prefill 의 커밋 게이트(make test · e2e · trial)와 이 작업의 시험(맥의 GB 데이터가 있어야 도는 것)이 서로 짐이 된다.
- SDL-MPSP 추가 발행은 어차피 `sdl-ontology-platform` 정본 — 이 작업은 원래 세 레포에 걸쳐 있다.
- 비용 = sdl-prefill 엔진을 옆 체크아웃으로 import(빌드마다 prefill 커밋 기록) · 용어는 PSC registry 를 읽고 새 용어는 prefill 받기 절차로.

## 인터뷰 기록(요지)

1. 정량지표 건수 = prefill `data_counts` 셈법인가 → **예. 세트 수 = 폴더 개수, 건수 = 그 셈법.**
2. 외부 DB 를 가상의 랩으로 보고 registry 형식 매핑 + 엔진 재사용인가 → **3층 구조(원본 → 라이브러리 → ABOX), 이번은 라이브러리까지. prefill 엔진 필요.**
3. 데이터를 git 밖에 두나 → **git 에 안 넣음. 맥에 보관(수 GB). 코드와 매핑기만. 변환기·매핑기는 prefill 메인 엔진이 아니라 별도로(외부 DB 전용).**
4. 매핑 용어 = PSC registry 를 따르고 없는 것만 추가하나 → **예.**
5. → **별도 레포로**(이름 `sdl-solar-chemdx-library`, 사용자 지정).
