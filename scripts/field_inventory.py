"""T2.1 필드 전수 — 2차 원본 스냅샷을 훑어 필드 경로마다 채워진 레코드 수(연도별) · 값 종류 · 단위 · 값 예를 CSV 로.

사용: python3 scripts/field_inventory.py <2_krict/YYYYMMDD> mapping/fields.csv
경로 = dict 키는 '.', 리스트는 '[]'. ChemDX 의 {"unit", "value"} 꼴은 잎 하나(단위를 따로 센다).
숫자 배열(측정 곡선)도 잎 하나 — 값 예에는 길이만.
"""
import collections, csv, json, pathlib, sys

LEAF_KEYS = {"unit", "value", "datatype"}


def walk(o, path=""):
    """(경로, 값, 단위) 를 낸다."""
    if isinstance(o, dict):
        if "value" in o and set(o) <= LEAF_KEYS:
            yield path, o["value"], o.get("unit")
            return
        for k, v in o.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list) and any(isinstance(x, (dict, list)) for x in o):
        for v in o:
            yield from walk(v, path + "[]")
    else:
        yield path, o, None


def kind(v):
    if v in (None, "", [], {}):
        return "empty"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "num"
    if isinstance(v, list):
        return "num[]" if all(isinstance(x, (int, float)) for x in v) else "list"
    try:
        float(v)
        return "numstr"  # 숫자가 문자열로 — 변환 때 숫자로 바꿔야 함
    except ValueError:
        return "str"


def example(v):
    return f"[{len(v)}]" if isinstance(v, list) else " ".join(str(v).split())[:40]


def fmt(c, top=6):
    return "; ".join(f"{k} ×{n}" for k, n in c.most_common(top))


def main(snap, out):
    stats = collections.defaultdict(lambda: [collections.Counter() for _ in range(4)])  # 연도별 레코드 · 종류 · 단위 · 값 예
    years = collections.Counter()
    for p in sorted(snap.glob("*/*.json")):
        y = p.parent.name
        years[y] += 1
        seen = set()
        for path, v, unit in walk(json.loads(p.read_bytes())):
            recs, kinds, units, ex = stats[path]
            k = kind(v)
            kinds[k] += 1
            if k == "empty":
                continue
            if unit not in (None, ""):
                units[unit] += 1
            ex[example(v)] += 1
            if path not in seen:
                seen.add(path)
                recs[y] += 1

    ys = sorted(years)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:  # 엑셀에서 한글이 깨지지 않게 BOM
        w = csv.writer(f)
        w.writerow(["path", f"all(/{sum(years.values())})", *[f"{y}(/{years[y]})" for y in ys], "kinds", "units", "examples"])
        for path in sorted(stats):
            recs, kinds, units, ex = stats[path]
            w.writerow([path, sum(recs.values()), *[recs[y] for y in ys], fmt(kinds), fmt(units), fmt(ex, 5)])
    print(len(stats), "paths ·", dict(sorted(years.items())))


def _selftest():
    r = {"a": {"unit": "M", "value": "1.5"}, "b": [{"c": {"unit": None, "value": "FA"}}, {"c": {"unit": None, "value": ""}}],
         "V": {"unit": "V", "value": [1, 2]}, "t": []}
    assert list(walk(r)) == [("a", "1.5", "M"), ("b[].c", "FA", None), ("b[].c", "", None), ("V", [1, 2], "V"), ("t", [], None)]
    assert [kind(v) for v in ("1.5", "FA", "", [1, 2], 3, None, False)] == ["numstr", "str", "empty", "num[]", "num", "empty", "bool"]


if __name__ == "__main__":
    _selftest()
    main(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
