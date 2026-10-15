"""라이브러리 빌드 둘 비교(T3.5 재현성 — 10-15 사용자): 같은 파일 목록 · xlsx 는 셀 내용 · 나머지는 바이트 · manifest 는 빌드 이름(@id) 빼고.
xlsx 바이트는 작성 시각(openpyxl) 때문에 매번 다르다 — 정본은 JSON-LD(docs/intent/json-ld.md)라 셀 내용이 같으면 재현으로 본다.

사용: python3 -I scripts/compare_builds.py <빌드 A> <빌드 B> [하위 폴더 예: PSC/2026]   (하위 폴더를 주면 manifest 는 안 봄)
같으면 종료 코드 0, 다르면 다른 파일 목록과 1.
"""
import json, pathlib, sys

import openpyxl


def cells(p):
    return [(ws.title, list(ws.iter_rows(values_only=True))) for ws in openpyxl.load_workbook(p, read_only=True).worksheets]


def manifest(p):
    m = json.loads(p.read_text())
    m.pop("@id", None)
    return m


def main(a, b, sub=""):
    ra, rb = a / sub, b / sub
    fa = {p.relative_to(ra) for p in ra.rglob("*") if p.is_file()}
    fb = {p.relative_to(rb) for p in rb.rglob("*") if p.is_file()}
    diff = sorted(f"{x} — 한쪽에만" for x in fa ^ fb)
    for f in sorted(fa & fb):
        same = (cells(ra / f) == cells(rb / f) if f.suffix == ".xlsx" else
                manifest(ra / f) == manifest(rb / f) if f.name == "manifest.json" and not sub else
                (ra / f).read_bytes() == (rb / f).read_bytes())
        if not same:
            diff.append(str(f))
    print(f"{len(fa & fb)} 파일 비교 · 다름 {len(diff)}", *diff[:20], sep="\n")
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), *sys.argv[3:4]))
