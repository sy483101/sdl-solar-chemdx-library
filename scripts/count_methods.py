"""데이터 건수 셈법 비교(A · A′ · B · C) + 지식그래프 트리플 수 — ChemDX 라이브러리 빌드 실데이터. 정의 = docs/intent/data-count-methods.md.

라이브러리 빌드 하나 → reports/count-methods-<빌드>.md(숫자만, git).
트리플 = sdl-ontology-platform 적재기(v05.load)로 실제 그래프를 만들어 센다 — 플랫폼 sdl_platform 을 쓰므로
build_library.py 와 다른 프로세스로 돈다(CLAUDE.md 함정). 플랫폼은 v0.6 시트 이름(Condition·Result·TargetAmount)을 읽어
메모리에서 이름만 바꿔 넣고, 비어 있는 Entity Type 은 플랫폼 J2 판정(개체 이름 → material·component·device)으로 채운다.

사용: python3 -I scripts/count_methods.py <library/<빌드>>
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
ASSEMBLED = ("component", "device")               # 산출물이 부품·소자 = 구조(구성) 정보 있음


def read(d, lab):
    """세트 폴더 → 플랫폼 read_package 와 같은 모양."""
    wb = openpyxl.load_workbook(d / "template.xlsx", read_only=True)
    out = {}
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        out[RENAME.get(ws.title, ws.title)] = [{h: L._s(v) for h, v in zip(rows[0], r)}
                                               for r in rows[1:] if any(v not in (None, "") for v in r)]
    for r in out["Process"]:
        r["TargetAmount"] = r.pop("Amount", "")
    for r in out["Entity"]:
        r["Type"] = r.get("Type") or J2.get((lab, r["Name"])) or EXTRA_J2[r["Name"]]
    return {s: [{c: r.get(c, "") for c in cols} for r in out[s]] for s, cols in COLUMNS.items()}


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
    pkgs = [read(lib / "2026" / s["experimentId"], lab) for s in sets]

    n = collections.Counter(sets=len(sets))
    slots = collections.defaultdict(set)          # (스텝 코드, 이름, 같은 이름 n번째) → 세트들에 나온 값
    manual = set()
    for s, p in zip(sets, pkgs):
        c = s["counts"]
        ys = [r for r in p["Result"] if is_y(r)]
        types = {r["ID"]: r["Type"] for r in p["Entity"]}
        struct = any(types.get(r["EntityID"]) in ASSEMBLED for r in p["Process"] if r["RowType"] == "output")
        n["A"] += c["composition"] + c["structure"] + c["process"] + c["analysis"]
        n["A_manual"] += c["composition"] + c["structure"] + c["process_manual"] + c["analysis"]
        n["B"] += (c["composition"] > 0) + struct + (c["process"] > 0) + len(ys)       # Y 는 반복마다
        n["C"] += 1 + len({(r["StepID"], r["Name"]) for r in ys})                       # Y 는 측정 항목마다 1
        n["Y"] += len(ys)
        n["Y_items"] += len({(r["StepID"], r["Name"]) for r in ys})
        n["Y_files"] += sum(r["OriginalFileName"] != "" for r in ys)
        n["ml_rows"] += len({(r["StepID"], r["RepeatNo"]) for r in ys})
        n["defaults"] += c["process"] - c["process_manual"]
        code = {r["ID"]: r["StepTypeCode"] for r in p["Process"] if r["RowType"] == "step"}
        seen = collections.Counter()
        for r in p["Condition"]:
            k = (code[r["StepID"]], r["Name"])
            seen[k] += 1
            slots[k + (seen[k],)].add(r["Value"])
            if r["Source"] == "manual":
                manual.add(k + (seen[k],))
    vary = sorted({f"{k[0].split('→')[-1].strip()}.{k[1]}" for k, v in slots.items() if len(v) > 1})

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
        f"이 스크립트 {commit(HERE)} · 플랫폼 적재기·J2 {commit(PLATFORM)}. 정의 = `docs/intent/data-count-methods.md`.", "",
        "| 셈법 | 정의 | 건수 | 세트당 | 트리플 ÷ 건수 |", "|---|---|---:|---:|---:|",
        f"| A 칸 단위(현행 `data_counts`) | 채워진 칸 = 1건(registry 기본값 포함) | {n['A']:,} | {per(n['A'])} | {t['full'] / n['A']:.1f} |",
        f"| A′ 칸 단위 · 기본값 제외 | 연구자가 적은 칸만 | {n['A_manual']:,} | {per(n['A_manual'])} | {t['full'] / n['A_manual']:.1f} |",
        f"| B 범주 + Y(반복마다) | 조성·구조·공정 각 1 + Y 측정 결과 행마다 1 | {n['B']:,} | {per(n['B'])} | {t['full'] / n['B']:.1f} |",
        f"| C X 1 + Y(항목마다) | X 1 + Y 측정 항목(스텝·결과 이름)마다 1 | {n['C']:,} | {per(n['C'])} | {t['full'] / n['C']:.1f} |",
        f"| (참고) ML 표본 행 | Y 를 낸 측정(스텝·반복) 하나 = 1 | {n['ml_rows']:,} | {per(n['ml_rows'])} | |", "",
        f"세트 {rows} · Y 측정 결과 행 {n['Y']:,}(그중 파일 {n['Y_files']:,}) · Y 측정 항목 {n['Y_items']:,} · 공정 칸 중 registry 기본값 {n['defaults']:,}. "
        f"공정 파라미터 자리 {len(slots)} 중 ChemDX 값이 든 자리 {len(manual)} · **세트마다 값이 달라지는 자리 {sum(len(v) > 1 for v in slots.values())}**(이름 {len(vary)}) "
        "(Process Note 에만 있는 몰농도·첨가제 비율 등은 빠짐):", "", ", ".join(vary), "",
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
    print("\n".join(lines))


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]).resolve())
