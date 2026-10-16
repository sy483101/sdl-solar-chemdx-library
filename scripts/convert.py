"""ChemDX(KRICT) 레코드 하나 → sdl-prefill draft + 첨부(곡선 csv) — 매핑 = mapping/chemdx_to_psc.csv.

스텝 = **실데이터로 조립**(사용자 10-16 — 레시피는 대표 레시피일 뿐 그 레시피로 했다는 정보가 아니다): 레코드의 층 블록 순서대로
층마다 registry StepType 하나(tco→BOTEL · ETL→CBD/ETL · etl_treatment→ETLSF · perovskite→PVK(+반용매 있으면 ASOL) ·
perovskite_treatment→PVKSF · htl→HTL · anode_metal→TOPEL) + JV. 레시피(PSC-RCP-03)는 JV 결과 정의만 참고 · RecipeCode 는 비운다.
registry 에 그 층·공정의 StepType 이 없으면 레코드째 건너뛴다(이유와 함께 — 조용히 버리지 않는다).
- registry 기본값은 이 실험의 값이 아니므로 지운다 — ChemDX 는 registry 와 따로 만든 실험이라 기록 없는 칸 = 행 없음
  (기본값 행이 있으면 적재기가 실측처럼 싣는다 — 사용자 10-16). ChemDX 값만 manual.
- registry 에 없는 이름·환산 못 한 단위는 버리지 않고 스텝 orphanParams 로(엔진이 Process Note + report.txt 경고로 남긴다).
- 이름은 registry 의 '옛 → 새' 메모·대소문자를 너그럽게 맞추고, 적을 때는 registry 이름을 그대로 쓴다.
엔진(sdl_platform)은 부르는 쪽이 sys.path 에 올린다(build_library.py).
"""
import copy, csv, functools, io, itertools, os, re

from sdl_platform import paths
from sdl_platform.engine import lab_registry
from sdl_platform.v05 import draft as D

LAB, RECIPE = "KRICT-PSC", "PSC-RCP-03"   # 참고 레시피 = JV 결과 정의만(스텝은 실데이터로 조립 — 사용자 10-16)
LAYERS = ("tco", "blocking_buffer_layer", "etl", "etl_treatment", "perovskite", "perovskite_treatment", "htl", "htl_doping",
          "htl_treatment", "anode_metal", "device_type")
ONCE = ("tco", "perovskite", "anode_metal")   # 두 번 나오면 랩 확인(ETL·표면처리·HTL 은 여러 층 허용)
STACK = {"n-i-p": ("tco", "blocking_buffer_layer", "etl", "etl_treatment", "perovskite", "perovskite_treatment", "htl", "htl_doping",
                   "htl_treatment", "anode_metal"),
         "p-i-n": ("tco", "htl", "htl_doping", "htl_treatment", "perovskite", "perovskite_treatment", "etl", "etl_treatment",
                   "blocking_buffer_layer", "anode_metal")}
# 스텝 순서 = 소자 구조의 적층 순서(ChemDX 블록 순서는 표면처리 블록이 맨 뒤에 오기도 한다) · 같은 층 여럿은 레코드 순서
NOSTEP = {"thermal_evaporation": "열증착층", "surface_treatment": "표면처리층"}   # 무엇의 공정인지 불명확한 블록(랩 확인)
PROC = ("spin_coating", "annealing", "module", "condition")   # 층 이름 없이 따로 떨어진 공정 블록 = 바로 앞 층의 공정
UNIT = {"ul": "ul", "µl": "ul", "μl": "ul", "ml": "ml", "m": "min", "min": "min", "s": "s", "h": "h",
        "oc": "c", "℃": "c", "degc": "c", "°c": "c", "um": "um", "µm": "um", "μm": "um",
        "å/s": "å/s", "a/s": "å/s", "utorr": "utorr", "µtorr": "utorr"}   # 증착 속도 'A/s' = Å/s(Å 두 글자 모두 소문자 å)
FACTOR = {("ml", "ul"): 1000, ("ul", "ml"): 0.001, ("s", "min"): 1 / 60, ("min", "s"): 60, ("h", "min"): 60, ("utorr", "torr"): 1e-6}
DOPANT = {"li-tfsi": "dopant1", "co-tfsi": "dopant2", "tbp": "additive"}   # HTL 도핑 = 이름으로 칸을 고른다
MODULE = {"type": "coatingMethod", "gap": "coatingGap", "coating_speed": "coatingSpeed", "feeding_amount": "feedingAmount"}   # 바·슬롯다이 코팅(v0.5.4 — PVK 만 칸 있음)


class Skip(Exception):
    """registry StepType 으로 담을 수 없는 레코드 — 빌드가 이유와 함께 건너뛰고 manifest 에 남긴다(10-15 사용자)."""


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


def coat(step, spins=(), anneals=(), modules=(), first=0):
    """스핀 단계(first = 단계 번호 앞자리 — 0 이면 번호 칸 안 씀) · 열처리 · 바·슬롯다이 코팅 → 칸(없으면 orphan)."""
    for i, sc in enumerate(spins):
        if first:
            put(step, "spinCoatingSpeedStep", first + i, nth=i)
        put(step, "spinCoatingSpeed", *lv(sc, "rpm"), nth=i)
        put(step, "spinCoatingTime", *lv(sc, "time"), nth=i)
        put(step, "spinCoatingMode", *lv(sc, "type"), nth=i)
    for i, an in enumerate(anneals):
        put(step, "thermalAnnealingTemperature", *lv(an, "temperature"), nth=i)
        put(step, "thermalAnnealingTime", *lv(an, "time"), nth=i)
    for i, m in enumerate(modules):                    # 바·슬롯다이 등 코팅(2023~) — PVK 밖은 칸 없음 → orphan
        for k in m:
            put(step, MODULE.get(k, f"module.{k}"), *lv(m, k), nth=i)


def spin_anneal(step, block):
    coat(step, block.get("spin_coating") or [], block.get("annealing") or [], block.get("module") or [])


def mats(items):
    return "+".join(str(lv(t, "material")[0]) for t in items or [] if lv(t, "material")[0] not in (None, ""))


def etl_code(b):
    """ETL 블록 → StepType: ALD · BUFEV(C60 열증착 — PSC-RCP-01 [신규]BUFEV 와 같은 쓰임) · CBD · ETL(그 밖 코팅)."""
    ms = [str(lv(t, "material")[0] or "") for t in b.get("etl") or [{}]]
    m, special = ms[0], [x for x in ms if "/" in x or "ALD" in x or x == "C60"]
    if special and (len(set(ms)) > 1 or "/" in m):
        raise Skip(f"ETL {'+'.join(ms)} — 한 블록에 여러 층(어느 층 값인지 랩 확인)")
    if "ALD" in m:
        return "ALD"
    if m == "C60":                                     # C60 = 열증착 재료(공정 칸이 비어도) · PC60BM 은 용액
        return "BUFEV"
    if b.get("thermal_evaporation"):
        raise Skip(f"ETL {m} 열증착 — 그 재료의 증착 StepType 없음(랩 확인)")
    return "CBD" if m == "SnO2_CBD" or b.get("chemical_bath_deposition") else "ETL"


def evap(step, block):
    """열증착 블록 → 두께·속도·압력(µTorr → Torr)·분위기 칸(없는 칸은 orphan)."""
    te = block.get("thermal_evaporation") or []
    for i, x in enumerate(te if isinstance(te, list) else [te]):
        put(step, "thickness", *lv(x, "vacuum_evaporation_thickness"), nth=i)
        put(step, "depositionRate", *lv(x, "evaporation_rate"), nth=i)
        put(step, "depositionChamberPressure", *lv(x, "vacuum_pressure"), nth=i)
    put(step, "evaporationAtmosphere", *lv(block, "condition"))


@functools.lru_cache(maxsize=1)
def steptypes():
    return frozenset(r.get("StepTypeCode", "") for r in lab_registry.lab_sheets(LAB).get("StepType", []))


def attach(seq, b):
    """층 이름 없는 공정 블록 → 바로 앞 층 블록에 합친 사본(원본은 그대로). PVK 공정 키는 perovskite 안에 있다."""
    i = next((i for i in range(len(seq) - 1, -1, -1) if seq[i][0] not in ("htl_doping", "device_type")), None)
    if i is None:
        return False
    k, host = seq[i][0], dict(seq[i][1])
    tgt = dict(host[k]) if k == "perovskite" else host
    for x in ("spin_coating", "annealing", "module"):
        if b.get(x):
            tgt[x] = (tgt.get(x) or []) + b[x]
    if b.get("condition") and not host.get("condition"):
        host["condition"] = b["condition"]
    if k == "perovskite":
        host[k] = tgt
    seq[i] = (k, host)
    return True


def layers_of(rec):
    """input 블록 → [(층, 블록)](레코드 순서) · 소자 블록 · 따로 떨어진 메모. 담을 수 없으면 Skip(큰 이유부터)."""
    seq, notes, odd = [], [], []
    for b in rec["input"]:
        if not b:
            continue                                   # 빈 블록({}) — 2021~2025 레코드에 흔함
        layers = [k for k in LAYERS if k in b]         # 한 블록에 층 여럿(예: tco + device_type)이면 층마다 · HTL 이 도핑보다 먼저
        if not layers:
            if set(b) == {"note"}:
                notes.append(lv(b, "note")[0])         # 메모만 있는 블록 → 실험 비고
            elif set(b) <= set(PROC):
                if not attach(seq, b):
                    odd.append(f"층 이름 없는 공정 블록이 맨 앞 {list(b)} — 랩 확인")
            elif any(k in NOSTEP for k in b):
                k = next(k for k in b if k in NOSTEP)
                odd.append(f"{NOSTEP[k]}({k}) — registry 에 그 층 StepType 없음")
            else:
                odd.append(f"모르는 input 블록 {list(b)}")
        seq += [(layer, b) for layer in layers]
    dev = next((b for k, b in seq if k == "device_type"), {})
    if lv(dev, "device_type")[0] not in ("n-i-p", "p-i-n"):
        raise Skip(f"소자 구조 {lv(dev, 'device_type')[0]} — 랩 확인")
    seq = [(k, b) for k, b in seq if k != "device_type"]
    for k in ONCE:
        if sum(x == k for x, _ in seq) > 1:
            odd.append(f"같은 층 블록 둘({k}) — 랩 확인")
    if "perovskite" not in (k for k, _ in seq):
        odd.append("PVK 블록 없음 — 랩 확인")
    for k, b in seq:
        if k == "blocking_buffer_layer" and not b.get("thermal_evaporation"):   # PSC 는 BCP 를 스핀(ETLSF) — 공정 값 없으면 모름
            odd.append(f"버퍼층 {mats(b.get(k))} 공정 값 없음 — 스핀(ETLSF)·증착(BUFEV) 중 무엇인지 랩 확인")
    if odd:
        raise Skip(odd[0])
    order = STACK[lv(dev, "device_type")[0]]
    seq.sort(key=lambda kb: order.index(kb[0]))     # 안정 정렬 — 같은 층은 레코드 순서 그대로
    pvk = next(b for k, b in seq if k == "perovskite")["perovskite"]
    if pvk.get("thermal_evaporation"):
        raise Skip("PVK 진공 증착 — registry PVK StepType 은 용액 공정")
    for k, b in seq:
        if k == "etl":
            etl_code(b)
    return seq, dev, notes


def convert(rec, seq_no):
    """→ (draft, blobs{file id: bytes})."""
    layers, dev, notes = layers_of(rec)
    meta = {"date": rec["created_at"][:10], "seq": f"{seq_no:03d}"}
    ref = D.from_recipe(LAB, RECIPE, meta)              # 참고 = JV 결과 정의
    jv_ref = next(s for s in ref["steps"] if norm(s["code"]) == "jv")
    note = lv(dev, "note")[0]
    d = {"meta": dict(ref["meta"], recipeCode="",       # 레시피 코드 비움 — 그 레시피로 했다는 정보가 아님(사용자 10-16)
                      title=" ".join(x for x in (lv(dev, "device_type")[0], {"unit_cell": "단위셀", "module": "모듈"}.get(lv(dev, "type")[0], lv(dev, "type")[0]), "(ChemDX)") if x),
                      note=" · ".join(str(x) for x in (f"ChemDX {rec['id']}", f"author {rec['author']}", note, *notes) if x)),
         "entities": [], "steps": []}

    def entity(name, **kw):
        e = D.new_entity(f"e{len(d['entities']) + 1}", name, **kw)
        d["entities"].append(e)
        return e

    def step(code, out_name):
        """스텝 하나 — 투입 = 지금 적층체 · 산출 = 새 적층체(이름 = 앞 이름 + 이 층)."""
        nonlocal cur
        if code not in steptypes():
            raise Skip(f"{code} — registry {paths.REGISTRY_VERSION} 에 그 StepType 없음")
        s = D.new_step(LAB, code, f"s{len(d['steps']) + 1}")
        s["orphanParams"] = {}
        out = entity(out_name)
        s["inputs"] = [{"entity": cur["key"], "amount": "", "unit": ""}]
        s["outputs"] = [{"entity": out["key"]}]
        d["steps"].append(s)
        cur = out
        return s

    tco = next((lv(b, "tco")[0] for k, b in layers if k == "tco"), None)
    cur = entity(f"bare_{tco}전극" if tco else "기판", note=f"ChemDX tco: {tco}" if tco else "ChemDX 에 기판 정보 없음")   # 원료 — 정체 한 줄
    htl_step = None
    for k, b in layers:
        if k == "tco":
            s = step("BOTEL", f"clean_{tco}전극")
            put(s, "material", tco)
            put(s, "atmosphere", *lv(b, "condition"))                  # 칸 없음 → orphan
        elif k == "etl":
            code, m = etl_code(b), lv((b.get("etl") or [{}])[0], "material")[0]
            s = step(code, f"{cur['name']}/{mats(b.get('etl')) or 'ETL'}")
            put(s, "material", m)
            if code in ("BUFEV", "ALD"):
                evap(s, b)                             # ALD 는 두께만 칸(ChemDX 가 증착 칸에 적음) — 나머지 orphan
            else:
                put(s, "cbdAtmosphere" if code == "CBD" else "spinCoatinglabAtmosphere", *lv(b, "condition"))   # ETL = 기존 칸
                for i, t in enumerate(b.get("etl") or []):
                    put(s, "concentration", lv(t, "concentration")[0], lv(t, "conc_unit")[0], nth=i)
                    put(s, "spinCoatingVolume", *lv(t, "quantity"), nth=i)
                for i, x in enumerate((b.get("chemical_bath_deposition") or {}).get("bath_annealing") or []):
                    put(s, "immersionTemperature", *lv(x, "temperature"), nth=i)   # CBD 욕조 온도·담금 시간(확인 대상)
                    put(s, "immersionTime", *lv(x, "time"), nth=i)
                for i, x in enumerate(b.get("etl_doping") or []):   # 'Ce 200mg/mL' — 이름·농도가 부피 칸에(ChemDX 입력 그대로)
                    raw = str(lv(x, "volume")[0] or "")
                    hit = re.match(r"^\s*(\S+)\s+([0-9.]+)\s*(mg/ml)\s*$", raw, re.I)
                    if hit:
                        put(s, "dopant1Name", hit[1], nth=i)
                        put(s, "dopant1Concentration", hit[2], hit[3], nth=i)
                    else:
                        put(s, "dopant", raw, nth=i)
            spin_anneal(s, b)
        elif k == "blocking_buffer_layer":           # 공정 값 있는 버퍼층(BCP 열증착)만 — 없는 것은 layers_of 가 건너뜀
            s = step("BUFEV", f"{cur['name']}/{mats(b.get(k)) or '버퍼층'}")
            for i, t in enumerate(b.get(k) or []):
                put(s, "material", *lv(t, "material"), nth=i)
            evap(s, b)
            spin_anneal(s, b)
        elif k == "htl_treatment":                   # SAM 등 HTL 위 용매 세척(에탄올) — 층이 아니라 처리
            s = step("HTLSF", f"{cur['name']}·{mats(b.get(k)) or ''} 처리")
            for i, t in enumerate(b.get(k) or []):
                put(s, "solvent", *lv(t, "material"), nth=i)
                put(s, "spinCoatingVolume", *lv(t, "quantity"), nth=i)
            spin_anneal(s, b)
        elif k in ("etl_treatment", "perovskite_treatment"):
            s = step("ETLSF" if k == "etl_treatment" else "PVKSF", f"{cur['name']}/{mats(b.get(k)) or k}")
            for t in b.get(k) or []:
                put(s, "material", *lv(t, "material"))
                put(s, "concentration", lv(t, "concentration")[0], lv(t, "conc_unit")[0])
                put(s, "spinCoatingVolume", *lv(t, "quantity"))
            put(s, "atmosphere" if k == "etl_treatment" else "spinCoatingAtmosphere", *lv(b, "condition"))   # ETLSF = 칸 없음 → orphan
            spin_anneal(s, b)
        elif k == "perovskite":
            pvk, base = b["perovskite"], cur["name"]
            spins, asol = pvk.get("spin_coating") or [], bool(pvk.get("antisolvent"))
            s = step("PVK", f"{base}/PVK 전구체막" if asol else f"{base}/PVK")
            put(s, "precursorMolarity", *lv(pvk, "molarity"))
            for i, x in enumerate(pvk.get("solvent") or []):
                put(s, f"solvent{i + 1}", *lv(x, "material"))
                put(s, f"solvent{i + 1}Volume", *lv(x, "volume"))
            for i, x in enumerate(pvk.get("additive") or []):
                put(s, "additive", *lv(x, "material"), nth=i)
                put(s, "additiveMolarRatio", *lv(x, "quantity"), nth=i)
                put(s, "additiveConcentration", lv(x, "concentration")[0], lv(x, "conc_unit")[0], nth=i)  # 확인 대상
            for i, x in enumerate(pvk.get("vacuum_suction") or []):    # 진공 흡입(2025)
                put(s, "vacuumSuctionTime", x.get("value"), x.get("unit") or "", nth=i)
            # 스핀 단계: PVK 칸 2벌 · 반용매가 있으면 셋째 단계부터·반용매·열처리 = ASOL(registry 칸 그대로), 없으면 PVK(→ orphan)
            coat(s, spins[:2] if asol else spins, [] if asol else pvk.get("annealing") or [], pvk.get("module") or [], first=1)
            put(s, "spinCoatingAtmosphere", *lv(b, "condition"))
            put(s, "laboratoryTemperature", *lv(dev, "temperature"))   # 실험실 온습도 = PVK(확인 대상)
            put(s, "laboratoryRelativeHumidity", *lv(dev, "humidity"))
            if asol:
                s = step("ASOL", f"{base}/PVK")
                for i, x in enumerate(pvk["antisolvent"]):
                    put(s, "antiSolvent", *lv(x, "material"), nth=i)
                    put(s, "antiSolventDrippingVolume", *lv(x, "quantity"), nth=i)
                    put(s, "antiSolventDrippingTiming", *lv(x, "dripping_time"), nth=i)
                coat(s, spins[2:], pvk.get("annealing") or [], first=3)
            # PVK 산출 = 적층체 + 페로브스카이트 재료(화학식은 재료에 — 사용자 10-14). PartOf 행은 엔진이 아직 안 써서 Note 로(prefill 7-2)
            mat = entity("페로브스카이트", formula=formula(pvk), note=f"{cur['name']} 의 PVK 층 재료")
            s["outputs"].append({"entity": mat["key"]})
        elif k == "htl":
            htl_step = s = step("HTL", f"{cur['name']}/{mats(b.get('htl')) or 'HTL'}")
            for t in b["htl"]:
                put(s, "holeTransportMaterial", *lv(t, "material"))
                put(s, "holeTransportMaterialConcentration", lv(t, "concentration")[0], lv(t, "conc_unit")[0])
                put(s, "spinCoatingVolume", *lv(t, "quantity"))
            for t in b.get("solvent") or []:
                put(s, "solvent", *lv(t, "material"))
                put(s, "solventVolume", *lv(t, "volume"))
            put(s, "spinCoatingAtmosphere", *lv(b, "condition"))
            spin_anneal(s, b)
        elif k == "htl_doping":                        # 같은 블록 안 · 따로 떨어진 블록 둘 다 이 차례에 한 번
            if htl_step is None:
                raise Skip("HTL 도핑 블록이 HTL 보다 앞 — 랩 확인")
            for t in b.get("htl_doping") or []:
                name, slot = lv(t, "material")[0], DOPANT.get(str(lv(t, "material")[0]).lower())
                if slot is None:
                    put(htl_step, f"dopant:{name}", *lv(t, "volume"))
                    continue
                put(htl_step, slot if slot == "additive" else f"{slot}Name", name)
                put(htl_step, f"{slot}Volume", *lv(t, "volume"))
        elif k == "anode_metal":
            s = step("TOPEL", f"{cur['name']}/{lv(b, 'anode_metal')[0]}")
            put(s, "material", *lv(b, "anode_metal"))
            put(s, "evaporationAtmosphere", *lv(b, "condition"))
    stack = cur["name"]
    area = lv(dev, "cell_dimension")[0]
    cur.update(name="완성소자", note=" · ".join(x for x in (f"적층 {stack}", f"ChemDX 소자 cell_dimension {area} cm2" if area not in (None, "") else "") if x))
    for s in d["steps"]:                                  # registry 기본값 지움 → 기록 없는 칸은 행 없음
        for p in s["params"]:
            p["default"] = ""

    # JV — (스캔 방향, 셀 면적, 측정 조건)별 스텝 하나, 스텝 안 반복 = 곡선(셀) 하나. 파라미터 행엔 RepeatNo 가 없어
    # 곡선마다 다른 조건은 스텝을 나눠야 적힌다(사용자 10-14). 면적 = 곡선 값(Jsc = Isc/면적 이 이 값으로 계산됨).
    tmpl = D.new_step(LAB, "JV", f"s{len(d['steps']) + 1}")
    tmpl["orphanParams"], tmpl["inputs"] = {}, [{"entity": cur["key"], "amount": "", "unit": ""}]
    tmpl["results"] = [copy.deepcopy(r) for r in jv_ref["results"] if r["name"] not in ("Image", "remark")]   # ChemDX 에 없음
    for p in tmpl["params"]:
        p["default"] = ""
    blobs = {}
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
            d["steps"].append(s)
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
    V = lambda x, u="": {"value": x, "unit": u}                        # 스텝 조립: 층 순서 · 반용매 → ASOL(셋째 스핀·열처리) · 도핑 블록 따로
    rec = {"id": "T-1", "author": 1, "created_at": "2026-01-01", "fileinfo": [], "analysis": {"JV": [
        {"measurement_conditions": {"sweep_direction": V("Forward")}, "pv_cell_parameters": {"efficiency": V(20, "%"), "cell_dimension": V(0.09)}}]},
        "input": [{"tco": V("ITO"), "device_type": V("n-i-p"), "type": V("unit_cell")}, {"etl": [{"material": V("SnO2_CBD")}]},
                  {"perovskite": {"a_site": [{"material": V("FA"), "ratio": V(1)}], "b_site": [{"material": V("Pb"), "ratio": V(1)}],
                                  "x_site": [{"material": V("I"), "ratio": V(1)}], "antisolvent": [{"material": V("DEE")}],
                                  "spin_coating": [{"rpm": V(1000)}, {"rpm": V(3000)}, {"rpm": V(5000)}], "annealing": [{"temperature": V(100, "oC")}]}},
                  {"htl": [{"material": V("Spiro-OMeTAD")}]}, {"htl_doping": [{"material": V("Li-TFSI"), "volume": V(20, "ul")}]},
                  {"annealing": [{"temperature": V(70, "oC")}]}, {"note": V("memo")},
                  {"anode_metal": V("Au")}, {}]}
    d, _ = convert(rec, 1)
    st = {s["code"]: s for s in d["steps"]}
    got = lambda c, n: [p["value"] for p in st[c]["params"] if p["name"] == n and p["use"]]
    assert [s["code"] for s in d["steps"]] == ["BOTEL", "CBD", "PVK", "ASOL", "HTL", "TOPEL", "JV"] and d["meta"]["recipeCode"] == ""
    assert got("PVK", "spinCoatingSpeed") == ["1000", "3000"] and got("ASOL", "spinCoatingSpeedStep") == ["3"] and got("ASOL", "spinCoatingSpeed") == ["5000"]
    assert got("ASOL", "thermalAnnealingTemperature") == ["100"] and got("ASOL", "antiSolvent") == ["DEE"] and got("HTL", "dopant1Name") == ["Li-TFSI"]
    assert got("HTL", "thermalAnnealingTemperature") == ["70"] and d["meta"]["note"].endswith("memo")   # 떨어진 공정 블록 = 앞 층
    assert not any(s["orphanParams"] for s in d["steps"]) and not any(p["default"] for s in d["steps"] for p in s["params"])
    assert [e["name"] for e in d["entities"]][:3] == ["bare_ITO전극", "clean_ITO전극", "clean_ITO전극/SnO2_CBD"] and d["entities"][-1]["name"] == "완성소자"
    assert [etl_code({"etl": [{"material": V(x)}]}) for x in ("C60", "SnO2_ALD", "PC60BM", "SnO2_CBD")] == ["BUFEV", "ALD", "ETL", "CBD"]
    assert to_unit("0.1", "A/s", "\u212b/s") == "0.1" and to_unit("5", "uTorr", "Torr") == "5e-06"
    for bad, why in (({"etl": [{"material": V("C60/SnO2")}]}, "여러 층"), ({"etl": [{"material": V("PCBM")}], "thermal_evaporation": [{}]}, "증착"),
                     ({"blocking_buffer_layer": [{"material": V("BCP")}]}, "공정 값 없음")):
        try:
            convert(dict(rec, input=rec["input"][:2] + [bad] + rec["input"][2:]), 1)
            raise AssertionError(why)
        except Skip as e:
            assert why in str(e), e


_selftest()
