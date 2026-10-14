# ChemDX 태양전지 데이터 — 받은 것의 구조

> 2026-10-14 사용자가 자기 도구로 받은 1차 원본(`raw/1_full/downloads/run-20261014T054004Z-rx23_glu`)을 조사한 결과. API 자체(엔드포인트·인증·호출 제한)는 미조사.

## 파일

- `downloads/latest.json` = `{"records_file": "run-…/records.json"}` — 최신 run 을 가리킨다.
- run 폴더 안에 **같은 13,271 레코드가 세 벌**:
  `records.json`(1.29GB, 배열 하나) · `N.zip`(그룹별 16개) · `N/N/<ID>.json`(zip 을 푼 것 — zip 항목과 바이트 동일, records.json 항목과 내용 동일).
- 2차 필터는 `N/N/<ID>.json` 을 읽는다 — 레코드 하나 = 파일 하나라 바이트 그대로 나눌 수 있다.

## 그룹 = 기관 (수집 로그와 대조)

그룹 번호와 ID 접두어가 1:1. 번호는 1~20 이지만 받은 그룹은 16개(4·5·13·16 없음 — 없는 그룹인지 권한 밖인지 모름).

| 그룹 | 이름(로그) | ID 접두어 | 건수 |
|---|---|---|---:|
| 1 | Virtual Lab | VLAB-SC | 2 |
| **2** | **KRICT** | **KRICT-SC** | **3,333** |
| 3 | UNIST | SC (기관명 없음) | 1,800 |
| 6 | CNU_EEML | CNU_EEML-SC | 351 |
| 7 | CAU | CAU-SC | 2,178 |
| 8 | KNU | KNU-SC | 405 |
| 9 | CNU_HEMD | CNU_HEMD-SC | 1,093 |
| 10 | JBNU | JBNU-SC | 785 |
| 11 | SKKU | SKKU-SC | 692 |
| 12 | KAIST | KAIST-SC | 751 |
| 14 | KU_SECL | KU_SECL-SC | 1,745 |
| 15 | UNIST_passivation | UNIST_passivation-SC | 53 |
| 17 | CNU-OE | CNU-OE-SC | 74 |
| 18 | KNU-NEML | KNU-NEML-SC | 2 |
| 19 | TRPL_GIST_TEST | TRPL_GIST_TEST-SC | 2 |
| 20 | KAIST-APTF | KAIST-APTF-SC | 5 |

## 레코드 (= 소자 하나)

| 필드 | 내용 |
|---|---|
| `id` · `_id` · `group` · `author`(번호) · `public`(0·2·없음) · `tags` | 식별·소속 |
| `created_at` · `updated_at` | 등록·수정 시각(`YYYY-MM-DD HH:MM:SS`, 시간대 표기 없음). 실험일 필드는 없다 |
| `input` | 층별 레시피 — tco · etl · perovskite(a/b/x_site 조성·molarity·solvent·antisolvent·spin_coating·annealing) · perovskite_treatment · htl · 소자 정보(device_type·type·온습도·note) |
| `process` | 층 → 스텝으로 정규화(`block`·`layer_name`·`layer_role`·`order`·`steps[step_no, step, 파라미터]`). `recipe_version` 1(13,080) · 2(191) |
| `analysisInfo.JV` | 셀별 요약 — efficiency · fill_factor · jsc · voc · cell_dimension · key |
| `analysis` | 곡선이 **숫자 배열로 들어 있다** — JV(13,271 레코드 키) · PL · UVVIS · XRD · Stability · TRPL 등. SEM 은 파일명만 |
| `fileinfo` | 업로드 원본 파일 목록(key · uploadType · original_name · save_name=서버 경로 · uploader). **파일 바이트는 받지 않았다** |

- 첨부 파일명에 측정일로 보이는 `YYYYMMDD` 가 있다 — KRICT 3,333 중 등록연도와 같음 2,856 · 다름 313 · 없음 155 · 섞임 9.

## 필드 전수에서 본 것 (T2.1, `mapping/fields.csv`)

- **같은 값이 여러 곳에**: JV 요약(efficiency·fill_factor·jsc·voc·cell_dimension)이 `analysisInfo.JV[]` · `analysis.JV[]` · `analysis.JV[].pv_cell_parameters` 세 곳.
  공정 파라미터는 `input[]`(층별 레시피)과 `process[]`(ChemDX 가 층→스텝으로 추론, `order` = inferred / to check)에 겹친다. 매핑은 한 곳만 고른다.
- **`input[]` 블록 = 층 하나** — 블록 안 키 조합으로 층을 안다(예: `etl_treatment` 옆의 `annealing` = ETL 처리 열처리). 2026 170건은 대부분
  tco → etl → etl_treatment → perovskite → perovskite_treatment → htl(+htl_doping·solvent) → anode_metal → 소자 정보 블록.
- **숫자가 문자열로**(값 종류 `numstr`) — 온도·시간·rpm·비율 대부분. 숫자와 문자열이 한 필드에 섞여 있다.
- **표기 변형**: 시간 단위 `m`·`min`·`s`·`time` · 온도 `oC`·`℃` · `1step`·`1-step` · `Bar coating`·`bar coating` · `rpm` 에 `vacuum deposition` 같은 다른 칸 값.
  농도는 `conc_unit` 칸이 따로(`unit` 이 비어 있음).
- **측정 곡선** = `analysis.JV[].V·I·J`(점 100~171개) — DataArtifact 로 뺄 대상. 2026 170건은 JV 만(2,328 곡선), PL·XRD·UV-Vis 없음.
- `analysis.JV[].measurement_conditions.note` 는 대부분 측정기 기본 문구("시료에 관한 부가적인 설명을 이곳에 적으세요")이고 상당수가 글자 깨짐(EUC-KR → Latin-1).

## 매핑 검토 메모 (2026-10-14, 사용자 질문 4건)

- **스캔 방향** — 곡선마다 세 곳이 일치: `measurement_conditions.sweep_direction` · 곡선 key 접두어(`Forward_`·`Reverse_`) · V 배열 진행(Forward = 오름, Reverse = 내림).
  2026: 2,328 중 2,327 셋 다 일치, 1개는 Forward 인데 V 가 내림(이상치). 옛 연도는 key 에 접두어 없는 것이 있으나 sweep_direction 칸은 있다.
- **실험실 온습도** — 스텝 안이 아니라 **소자 정보 블록**(device_type·type·note·cell_dimension·ar 와 같은 input 블록)에 소자당 한 값. `process[]` 에도 없다.
  2026: 22 ℃ 164 · 습도 25 % 160. 반면 `condition`(air·glove-box·vacuum evaporation)은 층 블록마다 있어 스텝별 분위기다.
- **MACl 농도 vs mol%** — 농도 칸(`concentration`+`conc_unit`)은 2025-07-18 부터. 짝이 전부 **mg/ml = 0.6 × mol%**(25→15 · 30→18 · 20→12)이고
  molarity(1.4~2.5 M)와 무관 — 화학량론이면 2.2 M × 25 % × 67.52 g/mol ≈ 37 mg/ml 여야 한다. → 농도는 고정 환산(기준 ≈ 0.89 M 상당)으로 보이며 실제 용액 농도로 읽으면 안 된다.
  mol% 는 2021~ 내내 있고 note(`1.6M MACl 30mol%`)와도 맞음 = 1차 값. 일부 레코드는 MACl 이 note 에만 있다(additive 비어 있음, 예 KRICT-SC-03583 `2.2M MACl 35mol%`). 랩 확인 대상.
- **조성 표현** — SDLEXO(`sdl-ontology-platform/data/ontology/tbox_aeonto.ttl`, SDL-0.3.3+up0.509):
  ① `aeo:hasChemicalFormula`(문자열, 산출 재료·소자에 — 원소 파싱) ② `aeo:hasStructure` → `aeo:Structure` → `aeo:hasComposition` → 조성 노드
  {`aeo:species` "FA" · `aeo:amount` 99(사이트 안 백분율 척도) · `aeo:hasConstituentRole` A-site(ConstituentRole 정의에 A/B-site 명시) · `aeo:containsElement`}.
  MPSP 0.509(SDL-MPSP v0.3.3): `materialEntity > chemicalFormula > Submitted` · `materialEntity > composition > constituent_n > Name·Fraction·Role·Concentration`
  (Role 예시는 dopant·host 등 — 사이트는 자유 문자열) · 공정 쪽 `spinCoating_n > precursor_n > Composition·additive_n > Amount` · `feedstock_n > Concentration`(용액 농도 = molarity 후보).
  5시트: Entity `ChemicalFormula` 칸(지금 엔진으로 됨) · Entity **constituent 행**(PartOf = 재료 개체 · Member = 화학종 · Role · Fraction) — 플랫폼 적재기
  `v05/load.py parts()` 가 이미 ②로 바꾼다. 단 sdl-prefill 엔진은 constituent 행을 아직 만들지 않고(템플릿 문서 "미착수") data_counts 도 안 센다.
  적재기는 PartOf 가 **재료** 개체여야 받는다 — 지금 formula 를 단 PVK 산출 개체(적층체)는 부품으로 분류될 수 있어, 페로브스카이트 재료 개체를 따로 두는 편이 맞다.
- **condition** — ChemDX 입력 양식이 층 블록마다 둔 칸(registry 가 아님). 2026: 소자 블록 air 160 · anode vacuum evaporation 160 · etl air 10 · perovskite air 10.
  registry 쪽 분위기 칸 = ETLCT `spinCoatinglabAtmosphere`(고정 문장) → MPSP `process > physical > spinCoating_n > Atmosphere` · PVK `solutionAgingAtmosphere`(용액 보관).
- **농도·mol% 표현** — 단위는 QUDT 로 해석됨(플랫폼 `ontology/qudt.resolve_unit`): mol% → PERCENT_MOL · M → MOL-PER-L · mg/mL → MilliGM-PER-MilliL · wt% → PERCENT_WT.
  자리(MPSP 0.509): 용액 농도·molarity = `spinCoating_n > feedstock_n > Concentration`(PSC `concentration` 이 이미 여기) · 첨가제 양 = `precursor_n > additive_n > Amount`
  (PSC `additiveWeight`·`additiveVolume` 이 이미 여기 — mol% 는 같은 노드에 단위만 다르게) · 재료 성분으로 보면 `materialEntity > composition > constituent_n > Concentration·Fraction`.
  SDLEXO: 스텝 값 = `aeo:ProcessParameter`(QuantityValue) · 투입 하나의 양·농도 = `aeo:Feedstock`(feedstock_n 대응) · 재료 성분 = 조성 노드(species·amount).
- **소실 검사**(dev-20261014, 2026 170건 — 원본 잎 값을 template.xlsx 셀·csv 에서 찾음): 곡선 2,328 = csv 2,328.
  설계상 버림 = 시스템 칸 · fileinfo · process[] 사본 · 측정기 문구. 바꿔서 남음 = type → 단위셀 · ar → no/yes · 사이트 비율 → 조성식 · SnO2_CBD → ETLCD 스텝 · 등록 시각 → 날짜만.
  **실제로 빠짐** = JV 부가값(rseries·rshunt·pmax·vopt·iopt·isc·fitted_isc·fitted_voc) · nplc · voltage_settling_time · 소자 블록 condition · 곡선별 cell_dimension(0.0452, 소자 블록 0.045216 을 씀) ·
  fileinfo.original_name(측정 시각이 든 원본 파일명) · note 에만 있는 MACl.
