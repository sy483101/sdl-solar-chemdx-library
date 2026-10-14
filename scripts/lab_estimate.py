"""랩별 세트당 데이터 건수 추산 — registry 레시피로 '레시피대로 한 실험 1세트'를 엔진으로 만들어 셈법 A·B·C 로 센다.
정의 = docs/intent/data-count-methods.md "재논의(10-15)" 절 · 목표 = 연차보고서 배포본 2026 표(PLAN).
→ reports/lab-estimate-registry-v<판>.md(+ .json — plot_count_methods.py 가 읽는다)

가정(랩 확인 전 추산): 레시피 고정값·registry 기본값은 적힘 · Variable 파라미터는 연구자가 채움 · 기본값 없는 선택 파라미터는 빈칸 ·
원료 개체마다 정보 칸 2개(CAS·화학식) · 투입량은 안 적음 · 결과는 정의된 것마다 1회.
설계인자 = registry Variable(랩 선언)만 — 실데이터가 없어 '세트마다 값이 달라진 것'은 못 본다(ELF·CAM 의 Variable 엔 sampleId 같은 운용값도 있어 과대).
응답 = 결과 중 랩 Kind 가 공정이 아닌 것. B 는 측정 1회(응답 각 1) ~ 같은 시편 반복(응답 각 2)의 범위.
A 트리플 = 이 레시피 1세트를 플랫폼 적재기에 넣은 그래프(count_methods.py --triples, 다른 프로세스 — CLAUDE.md 함정).

사용: python3 -I scripts/lab_estimate.py
"""
import json, os, pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
PREFILL = (HERE.parent / os.environ.get("SDL_PREFILL_DIR", "../sdl-prefill")).resolve()
PLATFORM = (HERE.parent / os.environ.get("SDL_PLATFORM_DIR", "../sdl-ontology-platform")).resolve()
sys.path.insert(0, str(PREFILL))                  # PYTHONPATH 의 다른 sdl_platform 보다 앞에(CLAUDE.md 함정)
import sdl_platform  # noqa: E402
assert pathlib.Path(sdl_platform.__file__).resolve().is_relative_to(PREFILL), sdl_platform.__file__
from sdl_platform.paths import REGISTRY_VERSION  # noqa: E402
from sdl_platform.v05 import draft as D, recipe, sheets  # noqa: E402

# 연차보고서 1세부 배포본(2026_연차보고서/reference/1차년도연차보고서_배포용.hwpx) "소재데이터 (10만건)" 표의 2026 열:
# 분야 → (합성시료 세트, (조성, 구조, 공정, 분석) 건, 랩). 이차전지 = KAIST 세 랩(SBM 은 registry 없음). CHA = 분석 지원(분야 목표 없음).
PLAN = {"석유화학촉매": (35, (105, 70, 105, 400), ["KRICT-PCC"]),
        "태양전지": (300, (0, 0, 300, 3000), ["KRICT-PSC"]),
        "유기광다이오드": (60, (60, 120, 60, 1200), ["KRICT-OPD"]),
        "전기화학촉매": (30, (30, 30, 60, 60), ["KIER-ECC"]),
        "이차전지": (30, (30, 30, 180, 60), ["KAIST-ELF", "KAIST-CAM", "KAIST-BAS"]),
        "(분석 지원)": (0, (0, 0, 0, 0), ["KRICT-CHA"])}


def one_set(lab, code, out):
    """레시피 → 채운 1세트의 셈 · out/<랩>/<레시피>/template.xlsx 를 남긴다(트리플용)."""
    d = D.from_recipe(lab, code, {"date": "2026-01-01", "seq": "001"})
    produced = {o["entity"] for s in d["steps"] for o in s["outputs"]}
    for e in d["entities"]:
        if D.is_raw(e, produced, d["steps"]):
            e["cas"], e["formula"] = "x", "x"
    y = df = 0
    for s in d["steps"]:
        for p in s["params"]:
            if p.get("variable"):
                df += 1
                if not p["value"]:
                    p["value"], p["use"] = "1", True
        for r in s["results"]:
            v = r["values"][0]
            if D.is_file(r):
                v["file"] = {"id": f"{s['key']}-{r['name']}", "name": "x.bin", "size": 1}
            else:
                v["value"] = "1"
            y += r.get("kindLab") != "Process"
    rows = sheets.build(d)[0]
    (out / lab / code).mkdir(parents=True)
    (out / lab / code / "template.xlsx").write_bytes(sheets.to_xlsx(rows))
    # 레시피의 결과는 (스텝, 이름)마다 하나 → 측정 항목 수 = 응답 수
    return {"cells": sum(sheets.data_counts(rows).values()), "Y": y, "DF": df,
            "B1": 1 + df + y, "B2": 1 + df + 2 * y, "C": 1 + y}


def main():
    git = lambda p, *a: subprocess.run(["git", "-C", str(p), *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
    commit = lambda p: git(p, "describe", "--always") + ("-dirty" if git(p, "status", "--porcelain") else "")  # noqa: E731
    tmp = pathlib.Path(tempfile.mkdtemp())
    est = {f: [(code, one_set(lab, code, tmp)) for lab in labs for code in recipe.recipes(lab)] for f, (_, _, labs) in PLAN.items()}
    tri = json.loads(subprocess.run([sys.executable, "-I", str(HERE / "count_methods.py"), "--triples", str(tmp)],
                                    capture_output=True, text=True, check=True).stdout)
    for e in est.values():
        for code, x in e:
            x["A"] = tri[code]
    lines = [f"# 랩별 세트당 데이터 건수 추산 — registry v{REGISTRY_VERSION}", "",
             f"이 스크립트 {commit(HERE)} · sdl-prefill {commit(PREFILL)} · 플랫폼 적재기·J2 {commit(PLATFORM)}. "
             "정의·가정 = `docs/intent/data-count-methods.md` 재논의 절 · 스크립트 머리말. 1세트 = 레시피대로, 결과 1회.", "",
             "| 분야 | 레시피 | A 트리플 | B 1회 ~ 반복 | C | 응답 | 설계인자(랩 선언) | 칸 단위(참고) |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    summary, tot = [], {}
    for field, (n, plan, _) in PLAN.items():
        if not est[field]:
            lines.append(f"| {field} | (레시피 결과 미정의 — 추산 불가) | | | | | | |")
        for code, e in est[field]:
            lines.append(f"| {field} | {code} | {e['A']:,} | {e['B1']} ~ {e['B2']} | {e['C']} | {e['Y']} | {e['DF']} | {e['cells']} |")
        if n and est[field]:
            rng = {k: (min(e[k] for _, e in est[field]) * n, max(e[k] for _, e in est[field]) * n) for k in ("A", "B1", "B2", "C")}
            summary.append((field, n, sum(plan), rng))
            for k, v in rng.items():
                tot[k] = (tot.get(k, (0, 0))[0] + v[0], tot.get(k, (0, 0))[1] + v[1])
    fmt = lambda v: f"{v[0]:,}" if v[0] == v[1] else f"{v[0]:,}~{v[1]:,}"  # noqa: E731
    lines += ["", "## 2026 목표 세트 × 1세트 추산", "",
              "| 분야 | 계획 세트 | 계획 건(세트당) | × A | × B 1회 | × B 반복 | × C |", "|---|---:|---:|---:|---:|---:|---:|"]
    for field, n, p, rng in summary:
        lines.append(f"| {field} | {n} | {p:,} ({p / n:.1f}) | {fmt(rng['A'])} | {fmt(rng['B1'])} | {fmt(rng['B2'])} | {fmt(rng['C'])} |")
    lines.append(f"| 합계(추산 가능 분야) | | {sum(p for _, _, p, _ in summary):,} | {fmt(tot['A'])} | {fmt(tot['B1'])} | {fmt(tot['B2'])} | {fmt(tot['C'])} |")
    out = HERE.parent / "reports" / f"lab-estimate-registry-v{REGISTRY_VERSION}.md"
    out.write_text("\n".join(lines) + "\n")
    out.with_suffix(".json").write_text(json.dumps(   # plot_count_methods.py 가 읽는다
        {f: {"plan_per_set": sum(PLAN[f][1]) / PLAN[f][0], "recipes": dict(est[f])} for f in est if PLAN[f][0]},
        ensure_ascii=False, indent=1) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
