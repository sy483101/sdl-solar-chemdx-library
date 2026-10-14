"""2차 원본 스냅샷 → 라이브러리층: 레코드마다 draft(convert.py) → 엔진 검증·zip(sheets.to_zip, 웹 내려받기와 같은 함수)
→ <out>/<2026|other>/<실험ID>/ 로 풀기 + manifest.json + reports/indicator-<빌드>.md(숫자만, git).

사용: python3 scripts/build_library.py <2_krict/YYYYMMDD> <library/<빌드 이름>> [연도 …]   (연도 생략 = 전부)
"""
import collections, hashlib, io, json, os, pathlib, subprocess, sys, zipfile

HERE = pathlib.Path(__file__).resolve().parent
PREFILL = (HERE.parent / os.environ.get("SDL_PREFILL_DIR", "../sdl-prefill")).resolve()
sys.path[:0] = [str(PREFILL), str(HERE)]          # PYTHONPATH 의 다른 sdl_platform 보다 앞에(CLAUDE.md 함정)
import sdl_platform  # noqa: E402
assert pathlib.Path(sdl_platform.__file__).resolve().is_relative_to(PREFILL), sdl_platform.__file__
from sdl_platform.paths import REGISTRY_VERSION  # noqa: E402
from sdl_platform.v05 import draft as D, sheets  # noqa: E402
import convert  # noqa: E402

COLS = ("composition", "structure", "process", "analysis")


def commit(path):
    git = lambda *a: subprocess.run(["git", "-C", str(path), *a], capture_output=True, text=True).stdout.strip()
    return git("describe", "--always") + ("-dirty" if git("status", "--porcelain") else "")   # 새 파일(untracked)도 dirty


def main(snap, out, years):
    out.mkdir(parents=True)                          # 이미 있으면 멈춤 — 기존 빌드를 덮어쓰지 않는다
    recs = [json.loads(p.read_bytes()) for p in sorted(snap.glob("*/*.json")) if not years or p.parent.name in years]
    # 일련번호 = 같은 등록일 안 ChemDX ID 순(D1). 날짜는 연도를 넘지 않아 연도별 부분 빌드도 같은 번호가 나온다.
    seq, per_day = {}, collections.Counter()
    for r in sorted(recs, key=lambda r: (r["created_at"][:10], r["id"])):
        per_day[r["created_at"][:10]] += 1
        seq[r["id"]] = per_day[r["created_at"][:10]]

    sets, totals = [], collections.defaultdict(collections.Counter)
    for r in recs:
        d, blobs = convert.convert(r, seq[r["id"]])
        findings = D.validate(d, {k: len(v) for k, v in blobs.items()})
        exp_id, z = sheets.to_zip(d, blobs, findings)
        group = "2026" if r["created_at"].startswith("2026") else "other"
        assert not (out / group / exp_id).exists(), f"실험 ID 겹침 {exp_id}"
        zipfile.ZipFile(io.BytesIO(z)).extractall(out / group)
        rows = sheets.build(d)[0]
        counts = sheets.data_counts(rows)
        counts["process_manual"] = sum(p["Source"] == "manual" and str(p["Value"]).strip() != "" for p in rows["Parameter"])
        levels = collections.Counter(f["level"] for f in findings)
        sets.append({"experimentId": exp_id, "chemdxId": r["id"], "group": group, "counts": counts, "findings": levels})
        totals[group].update(counts)
        totals[group].update(sets=1, sets_with_findings=bool(findings), **{f"findings_{k}": n for k, n in levels.items()})

    manifest = {"source": str(snap), "sourceManifestSha256": hashlib.sha256((snap / "manifest.json").read_bytes()).hexdigest(),
                "years": years or "all", "code": commit(HERE), "sdlPrefill": commit(PREFILL),
                "registryVersion": REGISTRY_VERSION, "templateVersion": sheets.TEMPLATE_VERSION,
                "recipe": f"{convert.LAB} {convert.RECIPE}", "totals": totals, "sets": sets}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))

    lines = [f"# 정량지표 — {out.name}", "",
             f"원본 `{snap.name}` · 코드 `{manifest['code']}` · sdl-prefill `{manifest['sdlPrefill']}` · registry {REGISTRY_VERSION} · "
             f"template {sheets.TEMPLATE_VERSION} · 골격 {manifest['recipe']}", "",
             "| 구분 | 세트 | 조성 | 구조 | 공정 | 분석 | 합계 | 공정 중 manual | 알림 남은 세트 | 오류 · 미입력 · 확인 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for g, t in sorted(totals.items()):
        lines.append(f"| {g} | {t['sets']} | " + " | ".join(f"{t[c]:,}" for c in COLS) + f" | {sum(t[c] for c in COLS):,} | "
                     f"{t['process_manual']:,} | {t['sets_with_findings']} | {t['findings_error']} · {t['findings_miss']} · {t['findings_warn']} |")
    report = HERE.parent / "reports" / f"indicator-{out.name}.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve(), sys.argv[3:])
