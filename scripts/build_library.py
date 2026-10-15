"""2차 원본 스냅샷 → 라이브러리층: 레코드마다 draft(convert.py) → 엔진 검증·zip(sheets.to_zip, 웹 내려받기와 같은 함수)
→ <out>/<랩>/<연도>/<실험ID>/ 로 풀기(플랫폼 라이브러리 규격 — 적재기가 실험 ID 에서 같은 경로를 계산) + manifest.json(JSON-LD)
+ reports/indicator-<빌드>.md(숫자만, git).

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
# manifest = JSON-LD — 키는 그대로 두고 @context 만 덧붙인다(사용자 10-15 · docs/intent/json-ld.md). 표준 어휘가 없는 키 = @vocab(정의 = 그 문서).
CONTEXT = {"@version": 1.1, "@base": "file:///",
           "@vocab": "https://github.com/sy483101/sdl-solar-chemdx-library/blob/main/docs/intent/json-ld.md#",
           "dcat": "http://www.w3.org/ns/dcat#", "dcterms": "http://purl.org/dc/terms/", "prov": "http://www.w3.org/ns/prov#",
           "aeod": "http://sdl.platform/data#",            # 플랫폼 ABox 의 실험 노드와 같은 IRI(세트 = 실험 ID)
           "source": {"@id": "prov:wasDerivedFrom", "@type": "@id"},   # 2차 원본 스냅샷 폴더(file IRI)
           "years": "dcterms:temporal", "sets": "dcterms:hasPart", "experimentId": "dcterms:identifier"}
SKIP_HEAD = 8                                        # 집계에 적을 건너뜀 이유 줄 수


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

    sets, skipped, totals = [], [], collections.defaultdict(collections.Counter)
    for r in recs:
        group = "2026" if r["created_at"].startswith("2026") else "other"
        try:
            d, blobs = convert.convert(r, seq[r["id"]])
        except convert.Skip as e:                    # 골격 밖 레코드 — 번호(seq)는 비워 둔다: 나중에 들어와도 다른 세트 ID 가 안 바뀜
            skipped.append({"chemdxId": r["id"], "group": group, "reason": str(e)})
            totals[group]["skipped"] += 1
            continue
        findings = D.validate(d, {k: len(v) for k, v in blobs.items()})
        exp_id, z = sheets.to_zip(d, blobs, findings)
        lab, ymd = exp_id.split("-EXP-")                 # 실험 ID {랩}-EXP-{YYYYMMDD}-{NNN} → <랩>/<연도>(플랫폼 load.check_set 과 같은 규칙)
        path = f"{lab}/{ymd[:4]}/{exp_id}"
        assert not (out / path).exists(), f"실험 ID 겹침 {exp_id}"
        zipfile.ZipFile(io.BytesIO(z)).extractall(out / lab / ymd[:4])
        rows = sheets.build(d)[0]
        counts = sheets.data_counts(rows)
        counts["process_manual"] = sum(p["Source"] == "manual" and str(p["Value"]).strip() != "" for p in rows["Parameter"])
        levels = collections.Counter(f["level"] for f in findings)
        sets.append({"@id": f"aeod:{exp_id}", "experimentId": exp_id, "path": path, "chemdxId": r["id"], "group": group,
                     "counts": counts, "findings": levels})
        totals[group].update(counts)
        totals[group].update(sets=1, sets_with_findings=bool(findings), **{f"findings_{k}": n for k, n in levels.items()})

    manifest = {"@context": CONTEXT, "@id": f"urn:sdl-solar-chemdx-library:build:{out.name}", "@type": ["dcat:Dataset", "prov:Entity"],
                "source": str(snap), "sourceManifestSha256": hashlib.sha256((snap / "manifest.json").read_bytes()).hexdigest(),
                "years": years or "all", "code": commit(HERE), "sdlPrefill": commit(PREFILL),
                "registryVersion": REGISTRY_VERSION, "templateVersion": sheets.TEMPLATE_VERSION,
                "recipe": f"{convert.LAB} {convert.RECIPE}", "totals": totals, "sets": sets, "skipped": skipped}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))

    lines = [f"# 정량지표 — {out.name}", "",
             f"원본 `{snap.name}` · 코드 `{manifest['code']}` · sdl-prefill `{manifest['sdlPrefill']}` · registry {REGISTRY_VERSION} · "
             f"template {sheets.TEMPLATE_VERSION} · 골격 {manifest['recipe']}", "",
             "| 구분 | 세트 | 조성 | 구조 | 공정 | 분석 | 합계 | 공정 중 manual | 알림 남은 세트 | 오류 · 미입력 · 확인 | 건너뜀 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|"]
    for g, t in sorted(totals.items()):
        lines.append(f"| {g} | {t['sets']} | " + " | ".join(f"{t[c]:,}" for c in COLS) + f" | {sum(t[c] for c in COLS):,} | "
                     f"{t['process_manual']:,} | {t['sets_with_findings']} | {t['findings_error']} · {t['findings_miss']} · {t['findings_warn']} | {t['skipped']:,} |")
    why = collections.Counter((x["group"], x["reason"]) for x in skipped)
    if why:
        lines += ["", "건너뛴 레코드(골격 밖 — manifest `skipped`):", ""] + [
            f"- {g} · {n:,} · {reason}" for (g, reason), n in why.most_common(SKIP_HEAD)] + (
            [f"- 그 밖 {len(why) - SKIP_HEAD}가지 이유 · {sum(n for _, n in why.most_common()[SKIP_HEAD:]):,}건"] if len(why) > SKIP_HEAD else [])
    report = HERE.parent / "reports" / f"indicator-{out.name}.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve(), sys.argv[3:])
