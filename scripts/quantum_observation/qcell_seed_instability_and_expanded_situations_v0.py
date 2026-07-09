#!/usr/bin/env python3
"""Seed-instability and expanded situation sweep for untamed Q-cell v0.

OBSERVATION_LOG only. The seed sweep is used to find situations whose
trajectories vary across seeds, not to certify reproducibility.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
from typing import Any
import numpy as np
import qcell_untamed_situation_observation_v0 as base
EXPERIMENT="qcell_seed_instability_and_expanded_situations_v0"; DATE="2026-07-09"; SEEDS=list(range(20260710,20260720))
def jf(x:Any,n:int=12)->float: return round(float(x),n)
def _seeded_qinit(kind,rng):
    psi=np.zeros(base.D,dtype=complex); psi[0]=1.0; r=np.outer(psi,psi.conj())
    if kind=="empty": angles=[0,0,0,0]
    elif kind=="biased_left": angles=[1.25,.45,.18,.05]
    elif kind=="biased_right": angles=[.05,.18,.45,1.25]
    elif kind=="alternating": angles=[1.1,.25,1.1,.25]
    elif kind=="random_product": angles=list(rng.uniform(.05,1.35,4))
    else: angles=[.72,.83,.94,1.05]
    angles=[float(a+rng.normal(0,.025)) for a in angles]
    for p,t in zip(base.PARTS,angles): r=base.single(r,base.ry(t),p)
    if kind=="seed_entangled": r=base.link(r,0,1,1.15+rng.normal(0,.03),.25+rng.normal(0,.02))
    if kind=="mixed":
        for p in base.PARTS: r=base.depol(r,p,.18)
    return r
base.qinit=_seeded_qinit

def periodic_actions(part,period,cycles,amp,tox=0.0):
    out=[]
    for k in range(cycles):
        s=amp*math.sin(2*math.pi*k/max(1,period))
        if abs(s)>1e-9: out.append({"op":"phase","part":part,"strength":s})
        if tox: out.append({"op":"dephase","parts":[part],"p":min(.6,tox*abs(s))})
        out.append({"op":"propagate","layers":1,"field":.04*s})
    return out

def square_actions(parts,period,cycles,amp,tox=0.0):
    out=[]
    for k in range(cycles):
        s=amp*(1 if (k//max(1,period//2))%2==0 else -1)
        for p in parts: out.append({"op":"phase","part":p,"strength":s})
        if tox: out.append({"op":"dephase","parts":parts,"p":min(.6,tox*abs(s))})
        out.append({"op":"propagate","layers":1,"field":.04*s})
    return out

def burst_actions(parts,cycles,amp,steps):
    out=[]
    for k in range(cycles):
        if k in steps:
            for p in parts: out.append({"op":"touch","part":p,"strength":amp})
            out.append({"op":"dephase","parts":parts,"p":.12})
        out.append({"op":"propagate","layers":1,"field":.02 if k in steps else 0})
    return out

def expanded_specs(start_id=1000):
    out=[]; sid=start_id
    def add(fam,pat,links,actions,initial="default"):
        nonlocal sid; sid+=1
        out.append({"scenario_id":sid,"family":fam,"pattern":pat,"initial":initial,"links":links,"actions":actions,"scope":"expanded_axes"})
    chain=[["A","B"],["B","C"],["C","D"]]
    add("external_periodic_drive","sin_A_period2",chain,periodic_actions("A",2,18,.8))
    add("external_periodic_drive","sin_A_period5",chain,periodic_actions("A",5,18,.8))
    add("external_periodic_drive","sin_C_period9",chain,periodic_actions("C",9,18,1.0))
    add("external_periodic_drive","square_all_fast_toxic",chain,square_actions(list("ABCD"),2,18,.55,.25))
    add("external_periodic_drive","burst_shock_all",chain,burst_actions(list("ABCD"),18,1.6,[3,9,14]))
    slow=[]
    for k in range(10):
        slow += [{"op":"phase","part":"B","strength":k/10},{"op":"dephase","parts":["A","D"],"p":.02*k},{"op":"propagate","layers":1,"field":.02*k}]
    add("external_periodic_drive","slow_ramp_pressure",chain,slow)
    add("multi_cell_chain_ring","three_node_chain_AB_BC",[["A","B"],["B","C"]],[{"op":"touch","part":"A","strength":1.0},{"op":"propagate","layers":8},{"op":"touch","part":"C","strength":.8},{"op":"propagate","layers":8}])
    add("multi_cell_chain_ring","three_node_ring_ABC",[["A","B"],["B","C"],["C","A"]],[{"op":"touch","part":"A","strength":1.0},{"op":"propagate","layers":8},{"op":"touch","part":"B","strength":.8},{"op":"propagate","layers":8}])
    add("multi_cell_chain_ring","four_node_chain_ABCD",chain,[{"op":"touch","part":"A","strength":.9},{"op":"propagate","layers":8},{"op":"touch","part":"D","strength":.9},{"op":"propagate","layers":8}])
    add("multi_cell_chain_ring","four_node_ring_ABCD",[["A","B"],["B","C"],["C","D"],["D","A"]],[{"op":"touch","part":"A","strength":.9},{"op":"touch","part":"C","strength":1.1},{"op":"propagate","layers":12}])
    add("multi_cell_chain_ring","four_node_two_contacts",[["A","B"],["C","D"],["A","C"],["B","D"]],[{"op":"touch","part":"A","strength":.8},{"op":"touch","part":"D","strength":.8},{"op":"propagate","layers":10}])
    add("measurement_timing_intervention","measure_A_each_step",chain,sum(([{"op":"dephase","parts":["A"],"p":1.0},{"op":"propagate","layers":1}] for _ in range(12)),[]))
    add("measurement_timing_intervention","measure_rotating_ABCD",chain,sum(([{"op":"dephase","parts":[p],"p":1.0},{"op":"propagate","layers":1}] for p in list("ABCD")*3),[]))
    add("measurement_timing_intervention","measure_middle_after_touch",chain,[{"op":"touch","part":"A","strength":1.0},{"op":"propagate","layers":2},{"op":"dephase","parts":["B","C"],"p":1.0},{"op":"propagate","layers":8}])
    add("measurement_timing_intervention","late_measure_all_then_continue",chain,[{"op":"touch","part":"D","strength":1.2},{"op":"propagate","layers":8},{"op":"dephase","parts":list("ABCD"),"p":1.0},{"op":"propagate","layers":6}])
    add("measurement_timing_intervention","sparse_edge_measure",chain,[{"op":"touch","part":"B","strength":.9},{"op":"propagate","layers":3},{"op":"dephase","parts":["A"],"p":1.0},{"op":"propagate","layers":3},{"op":"dephase","parts":["D"],"p":1.0},{"op":"propagate","layers":3}])
    add("duplication_asymmetry","A_and_D_duplicate_like_parallel",[["A","B"],["D","B"],["B","C"]],[{"op":"touch","part":"A","strength":.9},{"op":"touch","part":"D","strength":.9},{"op":"propagate","layers":12}])
    add("duplication_asymmetry","A_D_duplicate_like_unequal",[["A","B"],["D","B"],["B","C"]],[{"op":"touch","part":"A","strength":1.4},{"op":"touch","part":"D","strength":.35},{"op":"propagate","layers":12}])
    add("duplication_asymmetry","one_part_overdriven_B",chain,[{"op":"touch","part":"B","strength":2.1},{"op":"propagate","layers":5},{"op":"touch","part":"B","strength":1.7},{"op":"propagate","layers":7}])
    add("duplication_asymmetry","one_part_suppressed_C",chain,[{"op":"reset","part":"C","gamma":.75},{"op":"touch","part":"A","strength":1.0},{"op":"touch","part":"D","strength":1.0},{"op":"propagate","layers":10}])
    add("duplication_asymmetry","asymmetric_long_link_AD",[["A","B"],["B","C"],["C","D"],["A","D"]],[{"op":"touch","part":"A","strength":1.2},{"op":"propagate","layers":4},{"op":"touch","part":"D","strength":.4},{"op":"propagate","layers":8}])
    return out

def normalize_spec(s):
    s=dict(s)
    if "scope" not in s: s["scope"]="original_54"
    if s.get("links") and isinstance(s["links"][0][0],str): s["links"]=[(base.PARTS.index(a),base.PARTS.index(b)) for a,b in s["links"]]
    return s

def summarize(rec):
    row=base.summarize(rec); sc=rec["scenario"]
    row["seed"]=rec["seed"]; row["scope"]=sc.get("scope","original_54"); row["scenario_id"]=sc["scenario_id"]; row["family"]=sc.get("family",""); row["pattern"]=sc.get("pattern","")
    return row

def volatility(rows):
    groups={}
    for r in rows: groups.setdefault(int(r["scenario_id"]),[]).append(r)
    metrics=["delta_l1_coherence","delta_purity","max_abs_part_P1_delta","max_abs_ZZ_delta","max_abs_negativity_delta"]
    out=[]
    for sid,rs in sorted(groups.items()):
        b={"scenario_id":sid,"scope":rs[0]["scope"],"family":rs[0]["family"],"pattern":rs[0]["pattern"],"n_seeds":len(rs)}; score=0.0
        for m in metrics:
            a=np.array([float(r[m]) for r in rs]); b[m+"_min"]=jf(a.min()); b[m+"_max"]=jf(a.max()); b[m+"_range"]=jf(a.max()-a.min()); b[m+"_std"]=jf(a.std()); score=max(score,(a.max()-a.min())/(5 if m=="delta_l1_coherence" else 1))
        coh=np.array([float(r["delta_l1_coherence"]) for r in rs]); b["coherence_signs"]="+%d/-%d/0%d"%((coh>0).sum(),(coh<0).sum(),(coh==0).sum()); b["seed_instability_score"]=jf(score); out.append(b)
    return sorted(out,key=lambda r:r["seed_instability_score"],reverse=True)

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out-jsonl",type=Path,default=Path("data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719.jsonl")); ap.add_argument("--summary-csv",type=Path,default=Path("data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_summary.csv")); ap.add_argument("--volatility-csv",type=Path,default=Path("data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_seed_volatility.csv")); ap.add_argument("--manifest",type=Path,default=Path("data/quantum_observation/qcell_seed_instability_and_expanded_situations_v0_seed20260710_20260719_manifest.json")); a=ap.parse_args()
    specs=[normalize_spec(s) for s in (base.specs()+expanded_specs())]; rows=[]; a.out_jsonl.parent.mkdir(parents=True,exist_ok=True)
    with a.out_jsonl.open("w",encoding="utf-8") as f:
        for seed in SEEDS:
            for spec in specs:
                rec=base.run(spec,seed); rows.append(summarize(rec)); f.write(json.dumps(rec,ensure_ascii=False,separators=(",",":"))+"\n")
    vol=volatility(rows); write_csv(a.summary_csv,rows); write_csv(a.volatility_csv,vol); fam={}
    for s in specs: fam[s["family"]]=fam.get(s["family"],0)+1
    a.manifest.write_text(json.dumps({"experiment":EXPERIMENT,"date":DATE,"status":"OBSERVATION_LOG","seed_range":SEEDS,"n_macro_situations":len(specs),"n_original_54_situations":54,"n_expanded_situations":len(specs)-54,"n_records":len(rows),"families":fam,"policy":{"no_pass_fail":True,"no_ranking":True,"no_single_witness":True,"no_qpu_ready_claim":True,"parts_A_B_C_D_have_no_preassigned_roles":True,"seed_sweep_purpose":"find situations that vary across seeds, not certify reproducibility","seed_controls":"microscopic preparation jitter plus existing random-product/depolarize randomness"},"added_axes":["external periodic/burst drive","three/four node chain/ring contact","measurement timing as intervention","duplication-like/asymmetric situations"],"outputs":{"jsonl":str(a.out_jsonl),"summary_csv":str(a.summary_csv),"volatility_csv":str(a.volatility_csv)}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"experiment":EXPERIMENT,"records":len(rows),"macro_situations":len(specs),"expanded_situations":len(specs)-54,"top_seed_instability":vol[:8],"out_jsonl":str(a.out_jsonl),"summary_csv":str(a.summary_csv),"volatility_csv":str(a.volatility_csv),"manifest":str(a.manifest)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
