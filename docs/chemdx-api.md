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
