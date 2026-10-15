"""데이터 건수 셈법 비교(A 레시피 1+측정·분석 · B 설계인자+묶음+응답 · C 트리플 · 참고 칸 단위 — 10-15 이름 바꿈: 옛 C→A · 옛 A→C) — ChemDX 라이브러리 빌드 실데이터.
정의 = docs/intent/data-count-methods.md "재논의(10-15)" 절 · 설득 문서 = docs/data-count-methods-brief.md.

라이브러리 빌드 하나 → reports/count-methods-<빌드>.md(숫자만, git).
트리플 = sdl-ontology-platform 적재기(v05.load)로 실제 그래프를 만들어 센다 — 플랫폼 sdl_platform 을 쓰므로
build_library.py 와 다른 프로세스로 돈다(CLAUDE.md 함정). 플랫폼은 v0.6 시트 이름(Condition·Result·TargetAmount)을 읽어
메모리에서 이름만 바꿔 넣고, 비어 있는 Entity Type 은 플랫폼 J2 판정(개체 이름 → material·component·device)으로 채운다.

사용: python3 -I scripts/count_methods.py <library/<빌드>>
     python3 -I scripts/count_methods.py --triples <폴더>   # <폴더>/<랩>/<레시피>/template.xlsx → 레시피별 트리플 수(JSON) — lab_estimate.py 가 부른다
"""
import collections, json, os, pathlib, subprocess, sys

import openpyxl

HERE = pathlib.Path(__file__).resolve().parent
PLATFORM = (HERE.parent / os.environ.get("SDL_PLATFORM_DIR", "../sdl-ontology-platform")).resolve()
sys.path.insert(0, str(PLATFORM))                 # PYTHONPATH 의 다른 sdl_platform 보다 앞에
import sdl_platform  # noqa: E402
assert pathlib.Path(sdl_platform.__file__).resolve().is_relative_to(PLATFORM), sdl_platform.__file__
from sdl_platform.v05 import load as L  # noqa: E402
from sdl_platform.v05.sheets import COLUMNS  # noqa: E402

RENAME = {"Parameter": "Condition", "Value": "Result"}   # prefill 5sheet-1.1 → 플랫폼 v0.6
J2 = {(r["context"]["lab"], r["context"]["name"]): r["id"]
      for r in json.loads((PLATFORM / "reference_data/normalization/J2.json").read_text())
      if r["status"] in ("auto", "approved", "corrected")}
EXTRA_J2 = {"페로브스카이트": "material"}         # 변환기가 만든 재료 개체(convert.py) — J2 판정 전
INFO = ("CAS", "ChemicalFormula", "Supplier", "Product", "Lot")   # 조성 정보 칸 = prefill sheets.INFO
# 관측 변동 중 변동 인자(환경)·측정 설정 → 고정·변동 인자 묶음. 데이터팀 1차 분류(사용자 10-15) — 랩 확인 전
BUNDLE = {"laboratoryTemperature", "laboratoryRelativeHumidity", "scanDirection"}


def read(d, lab):
    """세트 폴더 → (시트 그대로 — 셈용, 플랫폼 read_package 와 같은 모양 — 트리플용)."""
    wb = openpyxl.load_workbook(d / "template.xlsx", read_only=True)
    out = {}
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        out[RENAME.get(ws.title, ws.title)] = [{h: L._s(v) for h, v in zip(rows[0], r)}
                                               for r in rows[1:] if any(v not in (None, "") for v in r)]
    for r in out["Process"]:
        r["TargetAmount"] = r.pop("Amount", "")
    for r in out["Entity"]:
        r["Type"] = r.get("Type") or J2.get((lab, r["Name"])) or EXTRA_J2.get(r["Name"], "")   # 없으면 적재기가 미표현으로 남긴다
    return out, {s: [{c: r.get(c, "") for c in cols} for r in out[s]] for s, cols in COLUMNS.items()}


def is_y(r):
    # Y = Value 시트의 측정 결과 행(숫자·파일 모두), 공정 기록(Kind Process)만 X.
    # ponytail: 시트 Kind 로 가름 — PSC 라이브러리엔 Process 결과가 없다. 다른 랩 데이터면 랩 Kind(registry)로
    return r["Value"] != "" and r["Kind"] != "Process"


def triples(pkgs, keep=lambda s, r: True):
    ld = L.Loader()
    for p in pkgs:
        ld.load({s: [r for r in rows if keep(s, r)] for s, rows in p.items()})
    return ld


def main(lib):
    man = json.loads((lib / "manifest.json").read_text())
    lab = man["recipe"].split()[0]
    sets = [s for s in man["sets"] if s["group"] == "2026"]
    raws, pkgs = zip(*(read(lib / "2026" / s["experimentId"], lab) for s in sets))

    n = collections.Counter(sets=len(sets))
    slots = collections.defaultdict(set)          # (스텝 코드, 이름, 같은 이름 n번째) → 세트들에 나온 값
    ents = collections.defaultdict(set)           # (개체 이름, 정보 칸) → 세트들에 나온 값
    manual, declared, per_set = set(), set(), []
    for s, p in zip(sets, raws):
        c = s["counts"]
        ys = [r for r in p["Result"] if is_y(r)]
        n["cells"] += c["composition"] + c["structure"] + c["process"] + c["analysis"]
        n["cells_manual"] += c["composition"] + c["structure"] + c["process_manual"] + c["analysis"]
        n["Y"] += len(ys)
        n["Y_items"] += len({(r["StepID"], r["Name"]) for r in ys})
        n["Y_files"] += sum(r["OriginalFileName"] != "" for r in ys)
        n["ml_rows"] += len({(r["StepID"], r["RepeatNo"]) for r in ys})
        n["defaults"] += c["process"] - c["process_manual"]
        code = {r["ID"]: r["StepTypeCode"] for r in p["Process"] if r["RowType"] == "step"}
        seen, mine = collections.Counter(), []
        for r in p["Condition"]:
            k = (code[r["StepID"]], r["Name"])
            seen[k] += 1
            k += (seen[k],)
            slots[k].add(r["Value"])
            mine.append(k)
            if r["Source"] == "manual":
                manual.add(k)
            if r.get("Variable") == "Y":                                                # 랩 선언
                declared.add(k)
        ent = [e for e in p["Entity"] if (e.get("RowType") or "entity") == "entity" and e.get("Source") != "import"]
        info = [(e["Name"], f) for e in ent for f in INFO if e.get(f, "") != ""]
        for e in ent:
            for f in INFO:
                if e.get(f, "") != "":
                    ents[(e["Name"], f)].add(e[f])
        # 응답: 시편(측정 대상 개체)·스텝·항목마다 1, 같은 시편 반복이면 n 과 무관하게 2(값 + 불확도)
        rep = collections.Counter((r["TargetEntityID"], r["StepID"], r["Name"]) for r in ys)
        per_set.append((mine, info, sum(min(v, 2) for v in rep.values())))
    # 설계인자 = 랩 선언 ∪ 세트마다 값이 달라진 자리(묶음 이름 제외)
    design = {k for k, v in slots.items() if len(v) > 1 and k[1] not in BUNDLE} | declared
    design_ent = {k for k, v in ents.items() if len(v) > 1}
    for mine, info, resp in per_set:
        n["B_comp"] += sum(k in design_ent for k in info)   # ponytail: 범주 = 시트 위치(개체 정보 → 조성, 파라미터 → 공정) — MPSP 경로 세분·구조는 다른 랩 데이터 때
        n["B_proc"] += sum(k in design for k in mine)
        n["B_resp"] += resp
    n["B"] = n["sets"] + n["B_comp"] + n["B_proc"] + n["B_resp"]
    # A(10-15 재정의 · 주 지표) = 레시피 1 + 측정·분석 — 측정·분석 셈 = B 응답과 같다(대상·스텝·항목마다 1, 같은 자리 반복 2).
    # ponytail: 같은 자리·같은 설정을 스텝을 나눠 적은 반복은 안 합친다 — ChemDX JV 스텝은 방향·면적이 서로 달라 해당 없음, 그런 데이터가 오면
    n["A"] = n["sets"] + n["B_resp"]
    vary = sorted({f"{k[0].split('→')[-1].strip()}.{k[1]}" for k in design})
    bundle = sorted({f"{k[0].split('→')[-1].strip()}.{k[1]}" for k, v in slots.items() if len(v) > 1 and k[1] in BUNDLE})

    full = triples(pkgs)
    assert not full.unexpressed, collections.Counter(u["reason"] for u in full.unexpressed)   # 행을 뺀 그래프는 미표현이 생길 수 있다(스캔 방향 등)
    without = lambda keep: len(full.g) - len(triples(pkgs, keep).g)   # 그 행들이 만든 트리플  # noqa: E731
    t = {"full": len(full.g),
         "Y": without(lambda s, r: not (s == "Result" and is_y(r))),
         "condition": without(lambda s, r: s != "Condition"),
         "defaults": without(lambda s, r: not (s == "Condition" and r["Source"] == "default"))}
    t["rest"] = t["full"] - t["Y"] - t["condition"]

    git = lambda p, *a: subprocess.run(["git", "-C", str(p), *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
    commit = lambda p: git(p, "describe", "--always") + ("-dirty" if git(p, "status", "--porcelain") else "")  # noqa: E731
    rows = n["sets"]
    per = lambda x: f"{x / rows:,.1f}"  # noqa: E731
    lines = [
        f"# 데이터 건수 셈법 · 트리플 — {lib.name} (2026)", "",
        f"빌드 `{lib.name}`(코드 {man['code']} · sdl-prefill {man['sdlPrefill']} · registry {man['registryVersion']}) · "
        f"이 스크립트 {commit(HERE)} · 플랫폼 적재기·J2 {commit(PLATFORM)}. 정의 = `docs/intent/data-count-methods.md`(재논의 10-15).", "",
        "| 셈법 | 정의 | 건수 | 세트당 | 트리플 ÷ 건수 |", "|---|---|---:|---:|---:|",
        f"| **A** 레시피 1 + 측정·분석 | 레시피 전체 1 + 측정·분석(대상·스텝·항목마다 1, 같은 자리 2회 이상이면 2) | {n['A']:,} | {per(n['A'])} | {t['full'] / n['A']:.1f} |",
        f"| **C** 트리플 | 플랫폼 적재기로 만든 그래프의 트리플 수 | {t['full']:,} | {per(t['full'])} | 1.0 |",
        f"| **B** 설계인자 + 묶음 + 응답 | 고정·변동 인자 묶음 1 + 설계인자 각 1 + 응답(시편·항목마다 1, 같은 시편 반복이면 2) | {n['B']:,} | {per(n['B'])} | {t['full'] / n['B']:.1f} |",
        f"| (참고) 칸 단위(현행 `data_counts`) | 채워진 칸 = 1건(registry 기본값 포함) | {n['cells']:,} | {per(n['cells'])} | {t['full'] / n['cells']:.1f} |",
        f"| (참고) 칸 단위 · 기본값 제외 | 연구자가 적은 칸만 | {n['cells_manual']:,} | {per(n['cells_manual'])} | {t['full'] / n['cells_manual']:.1f} |",
        f"| (참고) ML 표본 행 | 응답을 낸 측정(스텝·반복) 하나 = 1 | {n['ml_rows']:,} | {per(n['ml_rows'])} | |", "",
        f"**B 내역** = 묶음 {n['sets']:,} + 설계인자 조성 {n['B_comp']:,}(세트당 {per(n['B_comp'])}) · 공정 {n['B_proc']:,}({per(n['B_proc'])}) "
        f"+ 응답 {n['B_resp']:,}({per(n['B_resp'])}). 범주 = 시트 위치(개체 정보 → 조성 · 파라미터 → 공정) · 구조 설계인자 없음(소자 구조 고정). "
        "시편 = 측정 대상 개체 — 픽셀이 소자 개체 하나의 반복으로 들어가 있어 픽셀 10개도 2건(공통 원칙은 전 실험실 실데이터 확인 뒤).", "",
        f"세트 {rows} · 응답(측정 결과 행) {n['Y']:,}(그중 파일 {n['Y_files']:,}) · 측정 항목 {n['Y_items']:,} · 공정 칸 중 registry 기본값 {n['defaults']:,}. "
        f"공정 파라미터 자리 {len(slots)} 중 ChemDX 값이 든 자리 {len(manual)} · 세트마다 값이 달라지는 자리 {sum(len(v) > 1 for v in slots.values())} "
        f"→ **설계인자 {len(design)}**(랩 선언 {len(declared)}) · 묶음 {sum(len(v) > 1 and k[1] in BUNDLE for k, v in slots.items())} "
        f"· 개체 정보 설계인자 {', '.join(f'{a}.{b}' for a, b in sorted(design_ent))} (Process Note 에만 있는 몰농도·첨가제 비율 등은 빠짐).", "",
        f"설계인자: {', '.join(vary)}", "", f"묶음으로 보낸 관측 변동: {', '.join(bundle)}", "",
        "## 트리플(플랫폼 적재기 v05.load — 미표현 0)", "",
        "| 부분 | 트리플 |", "|---|---:|",
        f"| 합계 | **{t['full']:,}**(세트당 {t['full'] / rows:,.0f}) |",
        f"| Y 측정 결과 행 {n['Y']:,} | {t['Y']:,}(행당 {t['Y'] / n['Y']:.1f}) |",
        f"| 공정 조건(Parameter) | {t['condition']:,} — 그중 registry 기본값 {t['defaults']:,} |",
        f"| 메타데이터·개체·스텝·투입/산출 | {t['rest']:,} |", "",
        "적재 조건: prefill 5sheet-1.1 → 플랫폼 v0.6 시트 이름만 바꿈 · Entity Type = 플랫폼 J2(페로브스카이트 재료 개체만 material 로 보탬). "
        "부분별 트리플 = 그 행을 뺀 그래프와의 차이(공유 노드 탓 합이 약간 어긋날 수 있음).",
    ]
    out = HERE.parent / "reports" / f"count-methods-{lib.name}.md"
    out.write_text("\n".join(lines) + "\n")
    out.with_suffix(".json").write_text(json.dumps(   # 세트당 숫자 — plot_count_methods.py 가 읽는다
        {"sets": rows, "A": n["A"] / rows, "B": n["B"] / rows, "C": t["full"] / rows, "cells": n["cells"] / rows}, indent=1) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    if sys.argv[1] == "--triples":
        root = pathlib.Path(sys.argv[2])
        print(json.dumps({d.name: len(triples([read(d, d.parent.name)[1]]).g) for d in sorted(root.glob("*/*"))}))
    else:
        main(pathlib.Path(sys.argv[1]).resolve())
