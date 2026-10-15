# JSON-LD 정본 — 라이브러리 세트 → 빌더 → 그래프 DB·RDB (2026-10-15 interview-me 합의)

> 사용자 확인 = "착수"(10-15). 범위 문서 `project-scope.md` 의 "JSON-LD 확정(검토만)" 을 이 문서가 바꾼다. PLAN WS4 = (B)안 결정으로 닫음.

## 합의

- **결과물**: 라이브러리 세트 폴더마다 **플랫폼 빌더(적재기)가 만든 `set.jsonld`** — SDLEXO·MPSP·QUDT 가 매핑된 ABox 조각.
  그래프 DB 와 RDB 가 이 파일을 당겨간다. 소비자 기준 정본 = JSON-LD, xlsx = 사람이 보는 입력 원본. 템플릿 판 정본 = prefill 5sheet-1.1.
- **흐름**: prefill(웹 입력 · ChemDX 변환) → 세트 폴더(xlsx + DataArtifact) → 빌더 + 참조 문서(registry · J2·J3 · 단위표 · SDLEXO) → `set.jsonld` → 그래프 DB · RDB.
  JSON-LD 는 xlsx 와 참조 문서로 언제든 다시 만든다(손편집 금지).
- **본거지 = 플랫폼 PRJ22**(라이브러리 → DB 파이프라인)의 다음 작업 묶음. 템플릿 쪽은 prefill, registry 는 받기 절차. 각 레포 일은 그 레포 세션에서.
- **메타데이터**: 세트 `metadata.json` = JSON 색인 그대로(뜻은 `set.jsonld` 의 Experiment·ExperimentMetadata — 매핑을 빌더 하나로).
  빌드 `manifest.json` = JSON-LD(키 그대로 + `@context` — PROV·DCAT).
- **성공**: 같은 세트 두 번 빌드 → `set.jsonld` 바이트 같음(빈 노드 없음) · 그래프 DB 트리플 수 = 파일 트리플 수(C 는 파일에서) ·
  RDB 가 같은 파일을 중첩 JSON(고정 모양)으로 읽음 · 적재기가 빌드 폴더를 링크 없이 읽음.
- **시점**: 마감(10-26)과 무관하게 지금부터.
- **범위 밖**: prefill 이 JSON-LD 를 직접 내기 · 세트 `metadata.json` JSON-LD 화 · 이미 보고한 숫자 바꾸기 · RDB 스키마 설계 · D1 전 웹 세트와 합치기.

## 인터뷰 기록(요지)

| 물음 | 답 |
|---|---|
| JSON-LD 를 누가 읽나 | RDB 와 그래프 DB 가 당겨감. 엑셀 템플릿보다 적합. 메타데이터도 JSON-LD 로 |
| 정본은 | JSON 이 정본, xlsx 는 참고용 |
| 언제 | 마감과 무관하게 지금부터 |
| 판 차이(prefill Parameter·Value vs 플랫폼 v0.6 Condition·Result) | prefill 이 정본 |
| 구조 | 라이브러리 템플릿 + 문서체계를 매핑하는 빌더가 세트마다 JSON-LD 를 만들고 그래프 DB 가 받아감(사용자 제안 = WS4 (B)안) |
| 본거지 | 플랫폼 |
| 이 레포 빌드 폴더 | `library/<빌드>/<랩>/<연도>/<실험ID>/`(빌드 이름 유지, 웹 세트 합치기는 D1 뒤) |
| 메타데이터 범위 | 세트 `metadata.json` 은 JSON 그대로, 빌드 `manifest.json` 만 JSON-LD(같은 뜻의 출처가 둘이 되는 것을 피함) |

## 근거 — 지금 구조의 빈틈(10-15 조사, 플랫폼 9ead95b · prefill f43d853)

| 빈틈 | 템플릿(prefill) | 적재기·SDLEXO(플랫폼) |
|---|---|---|
| 부분-전체(적층체 ↔ 재료) · 조성 성분 | `PartOf`·`Member`·`Order`·`Fraction`·`Basis` 열은 있으나 엔진이 `entity` 행만 씀(`sheets.py:62`) | part 행 → Architecture·Placement·hasEntity, constituent 행 → hasStructure·hasComposition 이미 읽음(`load.py:373-416`). isPartOf·part_of 속성은 없음 — Placement 가 적층 순서·비율을 담음 |
| 결과 ↔ 스텝 | Value 행마다 `StepID` 있음 | 측정 노드(Characterization)를 스텝과 잇지 않음(`load.py:486-565`) · TBox 에 Step↔Characterization 속성 없음 · 값 행마다 노드 1(측정 사건 단위 아님) |
| 반복 · 맥락 | Value 에만 `RepeatNo`, Parameter 에 없음 · 맥락 = 스텝 순서 + 개체 사슬 | `RepeatNo` 버림(스텝 `Repeat` → `aeo:repetitions` 만) · `MeasurementCondition` 을 측정과 잇는 속성 없음 · 시료 상태·에이징 개념 없음 |
| 단위 | 자유 글자 | `unit_registry.csv` 정확 일치만 QUDT · 못 찾으면 글자로 남김(리포트 `units_unmapped`) |
| 값 노드 | — | QuantityValue = 빈 노드(`qudt.py:183`) → 다시 적재·병합 때 중복 · 바이트 결정성 깨짐. TBox 는 "숫자와 단위를 묶는 노드"(IRI/빈 노드 미지정) |
| 개체 종류 | Entity `Type` 비움(분류 = DB 적재) | 빈 Type = 재료(PRJ22) — ChemDX 소자 680·부품 672 가 재료로 적재됨(옛 J2 판정과 다름, WP2-3 대기) |

## 넘길 요청

**플랫폼(PRJ22 다음 묶음)**
1. 빌더가 세트마다 `set.jsonld` 출력 — `@context`(SDLEXO·MPSP·QUDT·PROV) + RDB 용 고정 모양(framing) · 판(플랫폼 커밋·registry 판) 기록 · 파생 링크(추론)는 넣지 않거나 분리.
2. 빈 노드 없애기 — QuantityValue 에 IRI(예: 값 노드 IRI + 접미사). 두 번 빌드 바이트 같음이 검사.
3. 측정 ↔ 스텝 연결 속성(TBox) + 적재기 연결 · 측정 사건 단위 노드 검토(지금 JV 1회 = 측정 노드 4).
4. 반복 번호(`RepeatNo`) 표현 · `MeasurementCondition` ↔ 측정 연결 · 시료 상태(에이징 등) 개념.
5. 단위 미매핑을 JSON-LD 에서 드러내기(QUDT IRI 없으면 소견) — 매핑표는 플랫폼 하나.
6. Entity 규약(WP2-3) — 빈 Type = 재료로 소자·부품이 재료가 되는 문제.
7. 선택: QuantityValue 를 값 노드에 합치는 안(노드 1·트리플 3~4 줄고 값 이중 기록 사라짐 — SDLEXO 패턴 변경이라 플랫폼 결정).

**prefill**
1. part·constituent 행 생성(draft · build · 화면) — 환류 7-1·7-2.
2. Parameter `RepeatNo` — 환류 7-4.
3. 참고: 값·결과에 고정 ID 없음(내보낼 때 순번) — 같은 draft 면 같은 ID 지만 다시 편집하면 바뀐다. `set.jsonld` @id 의 안정성 범위.

**registry(받기 절차)**: PSC 에이징 스텝 — PSC 회신 받을 때.

## 이 레포 몫

- [x] 빌드 출력 = `library/<빌드>/<랩>/<연도>/<실험ID>/`(`build_library.py` — 실험 ID 에서 기계적으로, 플랫폼 `check_set` 과 같은 규칙). dev 빌드 `dev-20261015`.
- [x] 빌드 `manifest.json` = JSON-LD(아래 어휘). 세트마다 `@id` = 플랫폼 ABox 실험 노드 IRI(`aeod:<실험ID>`) — 목록과 그래프가 이어짐.
- [x] `count_methods.py` = 적재기 `read_set` 으로 세트 폴더를 그대로 읽음(시트 이름 바꾸기·J2 채우기 삭제).
- [ ] 플랫폼 요청 1 이 나오면 빌드 때 세트 폴더에 `set.jsonld` 넣기(별도 프로세스) · C = 파일에서 세기.

### manifest 어휘

표준 어휘: `@type` = `dcat:Dataset`·`prov:Entity` · `source` = `prov:wasDerivedFrom`(2차 원본 스냅샷 폴더, file IRI) · `years` = `dcterms:temporal` ·
`sets` = `dcterms:hasPart` · `experimentId` = `dcterms:identifier`. 나머지 키 = `@vocab`(이 문서 `#<키>`):

| 키 | 뜻 |
|---|---|
| `sourceManifestSha256` | 2차 원본 스냅샷 `manifest.json` 의 sha256 — 기계와 무관하게 원본을 가리킴 |
| `code` · `sdlPrefill` | 이 레포 · sdl-prefill 커밋(`git describe`, 커밋 안 된 변경이 있으면 `-dirty`) |
| `registryVersion` · `templateVersion` · `recipe` | registry 판 · 템플릿 판 · 변환 골격 레시피 |
| `path` · `chemdxId` · `group` | 빌드 안 세트 폴더 · ChemDX 레코드 ID · 2026 / other |
| `counts`(composition·structure·process·analysis·process_manual) | 칸 단위 참고 지표(`sheets.data_counts`) |
| `findings`(error·miss·warn) · `totals` | 세트별 엔진 알림 수 · 묶음별 합계 |
| `skipped`(chemdxId·group·reason) | 변환기 골격 밖이라 건너뛴 레코드와 이유(실험 ID 번호는 비워 둠) |

잠정: `@vocab` 네임스페이스(이 문서 URL)와 빌드 `@id`(`urn:sdl-solar-chemdx-library:build:<빌드>`)는 플랫폼 `set.jsonld` 설계 때 맞춰 바꿀 수 있다.
`totals` 의 `2026` 키가 속성 이름이 되는 것은 해롭지 않아 둠.
