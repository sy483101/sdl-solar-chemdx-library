"""랩별 세트당 데이터 건수 추산 — registry 레시피로 '레시피대로 한 실험 1세트'를 엔진으로 만들어 셈법 A·A′·B·C 로 센다.
정의 = docs/intent/data-count-methods.md · 목표 = 연차보고서 배포본 2026 표(PLAN). → reports/lab-estimate-registry-v<판>.md

가정(사용자 확인 2026-10-14 — 랩 확인 전 추산): 레시피 고정값·registry 기본값은 적힘 · Variable 파라미터는 연구자가 채움 ·
기본값 없는 선택 파라미터는 빈칸 · 원료 개체마다 정보 칸 2개(CAS·화학식) · 투입량은 안 적음(양은 파라미터로) ·
결과는 정의된 것마다 1회(반복 수는 registry 에 없다 → B 는 '계획 달성에 필요한 반복 수'를 거꾸로 셈).

사용: python3 -I scripts/lab_estimate.py
"""
import json, math, os, pathlib, subprocess, sys

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
J2 = {(r["context"]["lab"], r["context"]["name"]): r["id"]
      for r in json.loads((PLATFORM / "reference_data/normalization/J2.json").read_text())
      if r["status"] in ("auto", "approved", "corrected")}


def one_set(lab, code):
    """레시피 → 채운 1세트의 셈. Y = 결과 행 중 랩 Kind 가 공정(Process)이 아닌 것(숫자·파일·글 모두)."""
    d = D.from_recipe(lab, code, {"date": "2026-01-01", "seq": "001"})
    produced = {o["entity"] for s in d["steps"] for o in s["outputs"]}
    for e in d["entities"]:
        if D.is_raw(e, produced, d["steps"]):
            e["cas"], e["formula"] = "x", "x"
    y = 0
    for s in d["steps"]:
        for p in s["params"]:
            if p.get("variable") and not p["value"]:
                p["value"], p["use"] = "1", True
        for r in s["results"]:
            v = r["values"][0]
            if D.is_file(r):
                v["file"] = {"id": f"{s['key']}-{r['name']}", "name": "x.bin", "size": 1}
            else:
                v["value"] = "1"
            y += r.get("kindLab") != "Process"
    rows = sheets.build(d)[0]
    c = sheets.data_counts(rows)
    a = sum(c.values())
    names = {e["key"]: e["name"] for e in d["entities"]}
    tiers = [J2.get((lab, names[k])) for k in produced]
    nx = (c["composition"] > 0) + any(t in ("component", "device") for t in tiers) + (c["process"] > 0)
    return {"A": a, "A1": a - sum(p["Source"] == "default" for p in rows["Parameter"]), "nx": nx, "Y": y,
            "B": nx + y, "C": 1 + y, "noJ2": sum(t is None for t in tiers)}


def main():
    git = lambda p, *a: subprocess.run(["git", "-C", str(p), *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
    commit = lambda p: git(p, "describe", "--always") + ("-dirty" if git(p, "status", "--porcelain") else "")  # noqa: E731
    lines = [f"# 랩별 세트당 데이터 건수 추산 — registry v{REGISTRY_VERSION}", "",
             f"이 스크립트 {commit(HERE)} · sdl-prefill {commit(PREFILL)} · 플랫폼 J2 {commit(PLATFORM)}. "
             "정의·가정 = `docs/intent/data-count-methods.md` · 스크립트 머리말. 1세트 = 레시피대로, 결과 1회.", "",
             "| 분야 | 레시피 | A | A′ | B(1회) | C | X 범주 | Y | B 로 계획 맞출 반복 수 |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    tot, summary = {}, []
    for field, (n, plan, labs) in PLAN.items():
        per = sum(plan) / n if n else 0
        est = [(code, one_set(lab, code)) for lab in labs for code in recipe.recipes(lab)]
        if not est:
            lines.append(f"| {field} | (레시피 결과 미정의 — 추산 불가) | | | | | | | |")
        for code, e in est:
            need = "—" if not n else "충족" if e["B"] >= per else math.ceil((per - e["nx"]) / e["Y"]) if e["Y"] else "Y 없음"
            lines.append(f"| {field} | {code}{' (J2 없음 ' + str(e['noJ2']) + ')' if e['noJ2'] else ''} | {e['A']} | {e['A1']} | "
                         f"{e['B']} | {e['C']} | {e['nx']} | {e['Y']} | {need} |")
        if n:
            rng = {k: (min(e[k] for _, e in est) * n, max(e[k] for _, e in est) * n) if est else None for k in ("A", "B", "C")}
            summary.append((field, n, sum(plan), per, rng))
            for k, v in rng.items():
                if v:
                    tot[k] = (tot.get(k, (0, 0))[0] + v[0], tot.get(k, (0, 0))[1] + v[1])
    fmt = lambda v: "—" if not v else f"{v[0]:,}" if v[0] == v[1] else f"{v[0]:,}~{v[1]:,}"  # noqa: E731
    lines += ["", "## 2026 목표 세트 × 1세트 추산(B 는 반복 1회 = 하한)", "",
              "| 분야 | 계획 세트 | 계획 건(세트당) | × A | × B(1회) | × C |", "|---|---:|---:|---:|---:|---:|"]
    for field, n, p, per, rng in summary:
        lines.append(f"| {field} | {n} | {p:,} ({per:.1f}) | {fmt(rng['A'])} | {fmt(rng['B'])} | {fmt(rng['C'])} |")
    plan_est = sum(p for f, n, p, per, rng in summary if rng["A"])
    lines.append(f"| 합계(추산 가능 분야) | | {plan_est:,} | {fmt(tot['A'])} | {fmt(tot['B'])} | {fmt(tot['C'])} |")
    out = HERE.parent / "reports" / f"lab-estimate-registry-v{REGISTRY_VERSION}.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
