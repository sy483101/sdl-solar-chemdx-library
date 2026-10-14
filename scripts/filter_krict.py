"""1차 원본(run 폴더)에서 KRICT 레코드만 골라 2차 `2_krict/<스냅샷>/<등록연도>/` 로 복사 — 파일 바이트 그대로.

사용: python3 scripts/filter_krict.py <1_full/downloads/run-…> <2_krict/YYYYMMDD>
읽는 것 = run 폴더의 `N/N/<ID>.json`(= N.zip 내용과 바이트 동일, records.json 과 같은 레코드).
"""
import collections, hashlib, json, pathlib, subprocess, sys

KRICT_GROUP = 2  # ChemDX 그룹 번호 — 수집 로그 "group 2 (KRICT)"(2026-10-14)
YEAR_FIELD = "created_at"  # ChemDX 등록일 — 사용자 결정(2026-10-14)


def main(run, out):
    out.mkdir(parents=True)  # 이미 있으면 멈춤 — 기존 스냅샷을 덮어쓰지 않는다
    files, years = {}, collections.Counter()
    for src in sorted(run.glob("*/*/*.json")):
        b = src.read_bytes()
        r = json.loads(b)
        if r["group"] != KRICT_GROUP:
            continue
        assert r["id"].startswith("KRICT-SC-") and src.stem == r["id"], src
        y = r[YEAR_FIELD][:4]
        rel = f"{y}/{src.name}"
        assert rel not in files, f"중복 {rel}"
        (out / y).mkdir(exist_ok=True)
        (out / rel).write_bytes(b)
        files[rel] = hashlib.sha256(b).hexdigest()
        years[y] += 1

    code = subprocess.run(["git", "-C", str(pathlib.Path(__file__).parent), "describe", "--always", "--dirty"],
                          capture_output=True, text=True).stdout.strip()
    manifest = {"source": str(run), "rule": {"group": KRICT_GROUP, "year_field": YEAR_FIELD}, "code": code,
                "counts": dict(sorted(years.items())), "total": len(files), "files": files}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))

    # 검사: 복사본을 다시 읽어 해시 대조
    bad = [p for p, h in files.items() if hashlib.sha256((out / p).read_bytes()).hexdigest() != h]
    assert not bad, bad
    print("code", code, "counts", manifest["counts"], "total", len(files))


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve())
