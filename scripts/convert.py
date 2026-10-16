"""ChemDX(KRICT) 레코드 하나 → sdl-prefill draft + 첨부(곡선 csv) — 매핑 = mapping/chemdx_to_psc.csv.

웹에서 연구자가 하는 순서 그대로: PSC 표준 레시피(PSC-RCP-03)를 불러와 → ChemDX 에 없는 스텝을 빼고 → 레코드 값을 적는다.
- 레시피 표준값·registry 기본값은 이 실험의 값이 아니므로 지운다 — ChemDX 는 registry 와 따로 만든 실험이라 기록 없는 칸 = 빈칸
  (기본값 행이 있으면 적재기가 실측처럼 싣는다 — 사용자 10-16). ChemDX 값만 manual.
- registry 에 없는 이름·환산 못 한 단위는 버리지 않고 스텝 orphanParams 로(엔진이 Process Note + report.txt 경고로 남긴다).
- 이름은 registry 의 '옛 → 새' 메모·대소문자를 너그럽게 맞추고, 적을 때는 registry 이름을 그대로 쓴다.
엔진(sdl_platform)은 부르는 쪽이 sys.path 에 올린다(build_library.py).
"""
import copy, csv, io, itertools, os

from sdl_platform.v05 import draft as D

LAB, RECIPE = "KRICT-PSC", "PSC-RCP-03"   # 2026 ChemDX = n-i-p 단위셀 = PSC-RCP-03 골격(T2.2)
LAYERS = ("tco", "etl", "etl_treatment", "perovskite", "perovskite_treatment", "htl", "anode_metal", "device_type")
UNIT = {"ul": "ul", "µl": "ul", "μl": "ul", "ml": "ml", "m": "min", "min": "min", "s": "s", "h": "h",
        "oc": "c", "℃": "c", "degc": "c", "°c": "c", "um": "um", "µm": "um", "μm": "um"}
FACTOR = {("ml", "ul"): 1000, ("ul", "ml"): 0.001, ("s", "min"): 1 / 60, ("min", "s"): 60, ("h", "min"): 60}
DOPANT = {"li-tfsi": "dopant1", "co-tfsi": "dopant2", "tbp": "additive"}   # HTL 도핑 = 이름으로 칸을 고른다
ETL_DROP = {"SnO2_CBD": "ETL", "SnO2_NP": "CBD"}   # ETL 재료 → PSC-RCP-03 에서 뺄 SnO2 스텝(남는 쪽이 그 공정)
MODULE = {"type": "coatingMethod", "gap": "coatingGap", "coating_speed": "coatingSpeed", "feeding_amount": "feedingAmount"}   # 바·슬롯다이 코팅(v0.5.4 — PVK 만 칸 있음)


class Skip(Exception):
    """PSC-RCP-03(n-i-p 단위셀 SnO2) 골격에 맞지 않는 레코드 — 빌드가 이유와 함께 건너뛰고 manifest 에 남긴다(10-15 사용자)."""


def fmt(x):
    return f"{x:.10g}"   # 부동소수 잡음 제거(0.045200000000000004 → 0.0452)


def lv(d, k):
    """ChemDX {unit, value} 잎 → (값, 단위). 없으면 (None, '')."""
    v = d.get(k) if isinstance(d, dict) else None
    if isinstance(v, dict):
        return v.get("value"), v.get("unit") or ""
    return v, ""


def norm(name):
    return str(name).split("→")[-1].strip().lower()


def to_unit(value, src, dst):
    """→ dst 단위 값 문자열, 환산 못 하면 None. 원본 단위가 없으면 대상 단위로 본다."""
    s, d = (UNIT.get(u.strip().lower(), u.strip().lower()) for u in (src or "", dst or ""))
    if not s or not d or d == "-" or s == d:
        return value
    try:
        return fmt(float(value) * FACTOR[(s, d)])
    except (KeyError, ValueError):
        return None


def put(step, name, value, unit="", nth=0):
    """파라미터 name 의 nth 번째 칸에 manual 값. 칸이 없거나 환산 못 하거나 숫자 칸에 글자면(엔진 검증 규칙) orphanParams."""
    if value in (None, ""):
        return
    value = fmt(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else str(value).strip()
    hits = [p for p in step["params"] if norm(p["name"]) == norm(name)]
    if nth < len(hits):
        p = hits[nth]
        v = to_unit(value, unit, p["unit"])
        if v is not None and (p["unit"] in ("", "-") or D._NUM.match(v)):
            p["value"], p["use"] = v, True
            return
    step["orphanParams"][name if nth == 0 else f"{name}#{nth + 1}"] = f"{value} {unit}".strip()


def formula(pvk):
    """a/b/x_site 비율(%) → ABX3 조성식, 예: FA0.99MA0.01PbI2.97Br0.03 (사이트마다 합으로 나눔)."""
    out = ""
    for site, n in (("a_site", 1), ("b_site", 1), ("x_site", 3)):
        rows = [(lv(r, "material")[0], float(lv(r, "ratio")[0])) for r in pvk.get(site) or []]
        total = sum(r for _, r in rows)
        out += "".join(m + ("" if r * n == total else fmt(r * n / total)) for m, r in rows)
    return out


def curve_csv(c):
    """JV 곡선 하나 → csv 바이트(열 = 숫자 배열 잎, 머리 = '이름 [단위]')."""
    cols = [(k, v) for k, v in c.items() if isinstance(v, dict) and isinstance(v.get("value"), list)]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([f"{k} [{v.get('unit', '')}]" for k, v in cols])
    w.writerows(itertools.zip_longest(*(v["value"] for _, v in cols), fillvalue=""))
    return buf.getvalue().encode()


def drop_step(d, code):
    """스텝 삭제 — 산출 개체를 쓰던 뒤 스텝은 삭제된 스텝의 투입 개체로 다시 잇는다."""
    s = step_of(d, code)
    d["steps"].remove(s)
    if s["outputs"]:
        old, new = s["outputs"][0]["entity"], s["inputs"][0]["entity"]
        for t in d["steps"]:
            for m in t["inputs"]:
                if m["entity"] == old:
                    m["entity"] = new
    used = {m["entity"] for t in d["steps"] for m in t["inputs"] + t["outputs"]}   # 지운 산출 · 아무도 안 쓰는 투입(예: SUBST 유리기판)
    d["entities"] = [e for e in d["entities"] if e["key"] in used]


def step_of(d, code):
    return next(s for s in d["steps"] if norm(s["code"]) == code.lower())


def spin_anneal(step, block):
    for i, sc in enumerate(block.get("spin_coating") or []):
        put(step, "spinCoatingSpeed", *lv(sc, "rpm"), nth=i)
        put(step, "spinCoatingTime", *lv(sc, "time"), nth=i)
        put(step, "spinCoatingMode", *lv(sc, "type"), nth=i)
    for i, an in enumerate(block.get("annealing") or []):
        put(step, "thermalAnnealingTemperature", *lv(an, "temperature"), nth=i)
        put(step, "thermalAnnealingTime", *lv(an, "time"), nth=i)
    for i, m in enumerate(block.get("module") or []):  # 바·슬롯다이 등 코팅(2023~) — PVK 밖은 칸 없음 → orphan
        for k in m:
            put(step, MODULE.get(k, f"module.{k}"), *lv(m, k), nth=i)


def convert(rec, seq):
    """→ (draft, blobs{file id: bytes})."""
    # 골격 밖이면 레코드째 건너뛰고 이유를 남긴다(조용히 버리지 않는다). 이유는 큰 것부터: 구조 → 모듈 → ETL → 블록 모양.
    blocks, odd = {}, []
    for b in rec["input"]:
        if not b:
            continue                                   # 빈 블록({}) — 2021~2025 레코드에 흔함
        layers = [k for k in b if k in LAYERS]         # 한 블록에 층 여럿(예: tco + device_type)이면 층마다
        if not layers:
            odd.append(f"모르는 input 블록 {list(b)}")
        for layer in layers:
            if layer in blocks:
                odd.append(f"같은 층 블록 둘({layer}) — 이중층·나눠 적은 블록(랩 확인)")
            blocks.setdefault(layer, b)
    dev = blocks.get("device_type") or {}
    if lv(dev, "device_type")[0] == "p-i-n":
        raise Skip("p-i-n — PSC-RCP-01(p-i-n) 골격의 [신규] 스텝 = PSC 회신 대기")
    if lv(dev, "device_type")[0] != "n-i-p":
        raise Skip(f"소자 구조 {lv(dev, 'device_type')[0]} — 랩 확인")
    if lv(dev, "type")[0] == "module":
        raise Skip("n-i-p 모듈 — PSC-RCP-02 골격의 [신규] 스텝 = PSC 회신 대기")
    etl = lv(((blocks.get("etl") or {}).get("etl") or [{}])[0], "material")[0]
    if etl not in ETL_DROP:
        raise Skip(f"ETL {etl} — PSC-RCP-03 에 그 공정 스텝 없음(랩 확인)")
    missing = [k for k in ("tco", "perovskite", "htl") if k not in blocks]
    if missing or odd:
        raise Skip(odd[0] if odd else f"필수 층 블록 없음 {missing} — 랩 확인")
    if blocks["perovskite"]["perovskite"].get("thermal_evaporation"):
        raise Skip("PVK 진공 증착 — PSC-RCP-03 PVK(용액 공정) 스텝과 다름(랩 확인)")

    d = D.from_recipe(LAB, RECIPE, {"date": rec["created_at"][:10], "seq": f"{seq:03d}"})
    for s in d["steps"]:                                  # 레시피 표준값·registry 기본값 지움 → 기록 없는 칸은 행 없음
        s["orphanParams"] = {}
        for p in s["params"]:
            p["value"], p["use"], p["default"] = "", False, ""
    for code in ("SUBST", "EQE", "IMAGE", "THICK"):       # ChemDX 에 없는 스텝(유리 기판 · 측정)
        drop_step(d, code)
    drop_step(d, ETL_DROP[etl])
    ents = {e["name"]: e for e in d["entities"]}

    note = lv(dev, "note")[0]
    d["meta"].update(title=f"{lv(dev, 'device_type')[0]} {'단위셀' if lv(dev, 'type')[0] == 'unit_cell' else lv(dev, 'type')[0]} (ChemDX)",
                     note=" · ".join(str(x) for x in (f"ChemDX {rec['id']}", f"author {rec['author']}", note) if x))

    s = step_of(d, "BOTEL")
    put(s, "material", *lv(blocks["tco"], "tco"))
    put(s, "atmosphere", *lv(blocks["tco"], "condition"))             # 칸 없음 → orphan
    ents["bare_FTO전극"]["note"] = f"ChemDX tco: {lv(blocks['tco'], 'tco')[0]}"   # 원료 — 정체 한 줄(검증 miss 방지)

    s = step_of(d, "CBD" if etl == "SnO2_CBD" else "ETL")
    if etl == "SnO2_NP":
        put(s, "material", etl)
    put(s, "cbdAtmosphere" if etl == "SnO2_CBD" else "spinCoatinglabAtmosphere", *lv(blocks["etl"], "condition"))   # ETL = 기존 칸(확인)
    for i, t in enumerate(blocks["etl"]["etl"]):
        put(s, "concentration", lv(t, "concentration")[0], lv(t, "conc_unit")[0], nth=i)
        put(s, "spinCoatingVolume", *lv(t, "quantity"), nth=i)
    for i, x in enumerate((blocks["etl"].get("chemical_bath_deposition") or {}).get("bath_annealing") or []):
        put(s, "immersionTemperature", *lv(x, "temperature"), nth=i)   # CBD 욕조 온도·담금 시간(확인 대상)
        put(s, "immersionTime", *lv(x, "time"), nth=i)
    spin_anneal(s, blocks["etl"])

    if "etl_treatment" in blocks:
        b, s = blocks["etl_treatment"], step_of(d, "ETLSF")
        for t in b["etl_treatment"]:
            put(s, "material", *lv(t, "material"))
            put(s, "concentration", lv(t, "concentration")[0], lv(t, "conc_unit")[0])
            put(s, "spinCoatingVolume", *lv(t, "quantity"))
        put(s, "atmosphere", *lv(b, "condition"))                     # 칸 없음 → orphan
        spin_anneal(s, b)
    else:
        drop_step(d, "ETLSF")

    b, s = blocks["perovskite"], step_of(d, "PVK")
    pvk = b["perovskite"]
    # PVK 산출 = 적층체 + 페로브스카이트 재료(화학식은 재료에 — 사용자 10-14). 둘을 잇는 PartOf 행은 엔진이 아직 안 써서
    # 재료 Note 에 글로(prefill 환류 7-2). 이름은 PSC 회신에 따라 바뀔 수 있다.
    stack = next(e for e in d["entities"] if e["key"] == s["outputs"][0]["entity"])
    mat = D.new_entity("pvk", "페로브스카이트", formula=formula(pvk), note=f"{stack['name']} 의 PVK 층 재료")
    d["entities"].insert(d["entities"].index(stack) + 1, mat)
    s["outputs"].append({"entity": mat["key"]})
    put(s, "precursorMolarity", *lv(pvk, "molarity"))
    for i, x in enumerate(pvk.get("solvent") or []):
        put(s, f"solvent{i + 1}", *lv(x, "material"))
        put(s, f"solvent{i + 1}Volume", *lv(x, "volume"))
    for i, x in enumerate(pvk.get("additive") or []):
        put(s, "additive", *lv(x, "material"), nth=i)
        put(s, "additiveMolarRatio", *lv(x, "quantity"), nth=i)
        put(s, "additiveConcentration", lv(x, "concentration")[0], lv(x, "conc_unit")[0], nth=i)  # 확인 대상
    for i, x in enumerate(pvk.get("vacuum_suction") or []):          # 진공 흡입(2025)
        put(s, "vacuumSuctionTime", x.get("value"), x.get("unit") or "", nth=i)
    for x in pvk.get("antisolvent") or []:
        put(s, "antiSolvent", *lv(x, "material"))
        put(s, "antiSolventDrippingVolume", *lv(x, "quantity"))
        put(s, "antiSolventDrippingTiming", *lv(x, "dripping_time"))
    for i, _ in enumerate(pvk.get("spin_coating") or []):
        put(s, "spinCoatingSpeedStep", i + 1, nth=i)
    spin_anneal(s, pvk)
    put(s, "spinCoatingAtmosphere", *lv(b, "condition"))
    put(s, "laboratoryTemperature", *lv(dev, "temperature"))          # 실험실 온습도 = PVK(확인 대상)
    put(s, "laboratoryRelativeHumidity", *lv(dev, "humidity"))

    if "perovskite_treatment" in blocks:
        b, s = blocks["perovskite_treatment"], step_of(d, "PVKSF")
        for t in b["perovskite_treatment"]:
            put(s, "material", *lv(t, "material"))
            put(s, "concentration", lv(t, "concentration")[0], lv(t, "conc_unit")[0])
            put(s, "spinCoatingVolume", *lv(t, "quantity"))
        put(s, "spinCoatingAtmosphere", *lv(b, "condition"))
        spin_anneal(s, b)
    else:
        drop_step(d, "PVKSF")

    b, s = blocks["htl"], step_of(d, "HTL")
    for t in b["htl"]:
        put(s, "holeTransportMaterial", *lv(t, "material"))
        put(s, "holeTransportMaterialConcentration", lv(t, "concentration")[0], lv(t, "conc_unit")[0])
        put(s, "spinCoatingVolume", *lv(t, "quantity"))
    for t in b.get("htl_doping") or []:
        name, slot = lv(t, "material")[0], DOPANT.get(str(lv(t, "material")[0]).lower())
        if slot is None:
            put(s, f"dopant:{name}", *lv(t, "volume"))
            continue
        put(s, slot if slot == "additive" else f"{slot}Name", name)
        put(s, f"{slot}Volume", *lv(t, "volume"))
    for t in b.get("solvent") or []:
        put(s, "solvent", *lv(t, "material"))
        put(s, "solventVolume", *lv(t, "volume"))
    put(s, "spinCoatingAtmosphere", *lv(b, "condition"))
    spin_anneal(s, b)

    if "anode_metal" in blocks:
        put(step_of(d, "TOPEL"), "material", *lv(blocks["anode_metal"], "anode_metal"))
        put(step_of(d, "TOPEL"), "evaporationAtmosphere", *lv(blocks["anode_metal"], "condition"))

    # JV — (스캔 방향, 셀 면적, 측정 조건)별 스텝 하나, 스텝 안 반복 = 곡선(셀) 하나. 파라미터 행엔 RepeatNo 가 없어
    # 곡선마다 다른 조건은 스텝을 나눠야 적힌다(사용자 10-14). 면적 = 곡선 값(Jsc = Isc/면적 이 이 값으로 계산됨).
    tmpl = step_of(d, "JV")
    at = d["steps"].index(tmpl)
    d["steps"].remove(tmpl)
    tmpl["results"] = [r for r in tmpl["results"] if r["name"] not in ("Image", "remark")]   # ChemDX 에 없음
    blobs = {}
    area = lv(dev, "cell_dimension")[0]
    if area not in (None, ""):                         # 소자 블록 면적(설계값) — 곡선 값과 다를 수 있어 소자 개체에 남김
        next(e for e in d["entities"] if e["key"] == tmpl["inputs"][0]["entity"])["note"] = f"ChemDX 소자 cell_dimension {area} cm2"
    ar = lv(dev, "ar")[0]
    files = {f["key"]: f["original_name"] for f in rec.get("fileinfo") or []}
    for direction in ("Forward", "Reverse"):
        groups = {}                                    # (면적, 광세기, 안정화 시간, NPLC) → 곡선(처음 나온 순)
        for c in rec["analysis"].get("JV") or []:
            mc, pc = c.get("measurement_conditions"), c.get("pv_cell_parameters")
            if lv(mc, "sweep_direction")[0] == direction:
                key = (lv(pc, "cell_dimension")[0], lv(pc, "irradiance"), lv(mc, "voltage_settling_time"), lv(mc, "nplc"))
                groups.setdefault(key, []).append(c)
        for j, ((a, light, settle, nplc), curves) in enumerate(groups.items(), 1):
            s = copy.deepcopy(tmpl)
            s["key"] = f"{tmpl['key']}{direction[0].lower()}{j}"
            pv = [c.get("pv_cell_parameters") or {} for c in curves]
            put(s, "scanDirection", direction.lower())
            put(s, "activeArea", a if a not in (None, "") else area, "cm2")
            put(s, "incidentLightIntensity", *light)
            put(s, "voltageSettlingTime", *settle)
            put(s, "nplc", *nplc)
            put(s, "antireflectionFilmUsage", {"0": "no", "1": "yes"}.get(str(ar)))   # 0/1 이 숫자·글자 둘 다로 옴
            for r in s["results"]:
                src = {"powerConversionEfficiency": "efficiency", "shortCircuitCurrentDensity": "jsc",
                       "openCircuitVoltage": "voc", "fillFactor": "fill_factor"}.get(r["name"])
                r["values"] = []
                for i, (c, p) in enumerate(zip(curves, pv), 1):
                    if r["name"] == "resultFile":
                        fid, data = f"{s['key']}-{i}", curve_csv(c)
                        blobs[fid] = data
                        # 원본 측정 txt 이름(측정 시각 포함) — 내용은 배열에서 만든 csv 라 확장자만 .csv
                        name = os.path.splitext(files.get(c.get("key"), ""))[0] or c.get("key") or str(i)
                        r["values"].append({"repeatNo": i, "value": "", "unit": "",
                                            "file": {"id": fid, "name": f"{name}.csv", "size": len(data)}})
                    else:
                        v, u = lv(p, src)
                        r["values"].append({"repeatNo": i, "value": "" if v in (None, "") else fmt(v), "unit": u, "file": None})
            d["steps"].insert(at, s)
            at += 1
    return d, blobs


def _selftest():
    assert formula({"a_site": [{"material": {"value": "FA"}, "ratio": {"value": "99"}}, {"material": {"value": "MA"}, "ratio": {"value": 1}}],
                    "b_site": [{"material": {"value": "Pb"}, "ratio": {"value": "100"}}],
                    "x_site": [{"material": {"value": "I"}, "ratio": {"value": "99"}}, {"material": {"value": "Br"}, "ratio": {"value": "1"}}]}
                   ) == "FA0.99MA0.01PbI2.97Br0.03"
    assert [to_unit("0.3", "ml", "µL"), to_unit("20", "m", "min"), to_unit("90", "s", "min"), to_unit("150", "oC", "℃"),
            to_unit("5", "", "s"), to_unit("FTO", "", "-"), to_unit("1", "mg/ml", "mg/mL"), to_unit("2", "kg", "g"), to_unit("0.2", "um", "µm")] == \
        ["300", "20", "1.5", "150", "5", "FTO", "1", None, "0.2"]
    st = {"params": [{"name": "a → thermalAnnealingTIme", "unit": "min", "value": "", "use": False}], "orphanParams": {}}
    put(st, "thermalAnnealingTime", "1", "h"); put(st, "thermalAnnealingTime", "3", "m", nth=1); put(st, "x", "2", "kg")
    assert st["params"][0]["value"] == "60" and st["params"][0]["use"] and st["orphanParams"] == {"thermalAnnealingTime#2": "3 m", "x": "2 kg"}
    put(st, "thermalAnnealingTime", "MeO-PEAI")                        # 숫자 칸에 글자 → 칸은 그대로, orphan
    assert st["params"][0]["value"] == "60" and st["orphanParams"]["thermalAnnealingTime"] == "MeO-PEAI"
    assert curve_csv({"V": {"unit": "V", "value": [1, 2]}, "J": {"unit": "A/cm2", "value": [3]}, "k": "x"}) == b"V [V],J [A/cm2]\r\n1,3\r\n2,\r\n"


_selftest()
