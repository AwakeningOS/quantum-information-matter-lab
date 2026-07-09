#!/usr/bin/env python3
"""Temporal, free-run, contact-scan, and metric-mask Q-cell observation.

OBSERVATION_LOG only. This script records when trajectories branch, reverse, or
stall; what remains after operations are removed; broad two-body contact scans;
and how observation signatures change when metrics are hidden.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
from typing import Any
import numpy as np
import qcell_untamed_situation_observation_v0 as base
EXPERIMENT="qcell_temporal_free_contact_mask_observation_v0"; DATE="2026-07-09"; SEEDS=list(range(20260710,20260720))
PARTS=base.PARTS; PAIRS=[a+b for i,a in enumerate(PARTS) for b in PARTS[i+1:]]
def jf(x:Any,n:int=12)->float: return round(float(x),n)
def one_layer(n,field=0.0,dephase_p=0.0): return [{"op":"propagate","layers":1,"field":field,"dephase_p":dephase_p} for _ in range(n)]
def free_layers(n): return [{"op":"propagate","layers":1,"field":0.0,"stage":"free_after_release"} for _ in range(n)]
def hard_idle(n): return [{"op":"idle","leak":0.0,"stage":"hard_idle_no_dynamics"} for _ in range(n)]
def sin_drive(part,period,steps,amp):
    out=[]
    for k in range(steps):
        s=amp*math.sin(2*math.pi*k/period)
        out += [{"op":"phase","part":part,"strength":s,"stage":"periodic_drive"},{"op":"propagate","layers":1,"field":0.04*s,"stage":"after_drive_step"}]
    return out
def specs():
    out=[]; sid=2000
    def add(fam,pat,actions,links=None,initial="default"):
        nonlocal sid; sid+=1
        out.append({"scenario_id":sid,"scope":"temporal_free_contact_mask_v0","family":fam,"pattern":pat,"initial":initial,"links":links or [(0,1),(1,2),(2,3)],"actions":actions})
    # 1. time-resolution expansion: actions are deliberately one-step-grained.
    add("time_resolution_expansion","ABCD_touch_one_layer",sum(([{"op":"touch","part":p,"strength":.75,"stage":"touch"}]+one_layer(1) for p in "ABCD"),[]))
    add("time_resolution_expansion","DCBA_touch_one_layer",sum(([{"op":"touch","part":p,"strength":.75,"stage":"touch"}]+one_layer(1) for p in "DCBA"),[]))
    add("time_resolution_expansion","burst_B_then_small_A_steps",[{"op":"touch","part":"B","strength":1.8,"stage":"burst"}]+one_layer(2)+[{"op":"touch","part":"A","strength":.25,"stage":"small_touch"}]+one_layer(10))
    add("time_resolution_expansion","reverse_phase_midway",[{"op":"touch","part":"A","strength":.9,"stage":"touch"}]+one_layer(4)+[{"op":"phase","part":"A","strength":-1.2,"stage":"phase_reverse"}]+one_layer(8))
    add("time_resolution_expansion","sin_A_period3_layerwise",sin_drive("A",3,18,.9))
    add("time_resolution_expansion","sin_C_period7_layerwise",sin_drive("C",7,21,1.0))
    add("time_resolution_expansion","measure_rotating_each_step",sum(([{"op":"dephase","parts":[p],"p":1.0,"stage":"rotating_measure"}]+one_layer(1) for p in "ABCDABCDABCD"),[]))
    add("time_resolution_expansion","toxicity_pulse_then_layerwise",[{"op":"dephase","parts":list("ABCD"),"p":.35,"stage":"toxicity_pulse"}]+one_layer(16))
    # 2. free observation after operations are removed.
    add("free_observation_after_release","touch_A_then_free24",[{"op":"touch","part":"A","strength":1.0,"stage":"stimulus"}]+one_layer(3)+free_layers(24))
    add("free_observation_after_release","burst_all_then_free24",[{"op":"touch","part":p,"strength":1.2,"stage":"burst"} for p in PARTS]+one_layer(2)+free_layers(24))
    add("free_observation_after_release","middle_dephase_then_free24",[{"op":"dephase","parts":["B","C"],"p":.55,"stage":"disturbance"}]+one_layer(2)+free_layers(24))
    add("free_observation_after_release","contact_BC_release_then_free24",[{"op":"set_links","links":[["A","B"],["C","D"],["B","C"]],"stage":"contact_on"},{"op":"touch","part":"A","strength":1.0,"stage":"stimulus"}]+one_layer(6)+[{"op":"set_links","links":[["A","B"],["C","D"]],"stage":"contact_off"}]+free_layers(24),links=[(0,1),(2,3)])
    add("free_observation_after_release","reverse_then_free24",[{"op":"touch","part":"D","strength":1.1,"stage":"stimulus"}]+one_layer(3)+[{"op":"phase","part":"D","strength":-1.3,"stage":"reverse"}]+one_layer(2)+free_layers(24))
    add("free_observation_after_release","hard_idle_after_touch",[{"op":"touch","part":"B","strength":1.0,"stage":"stimulus"}]+one_layer(2)+hard_idle(20))
    # 3. broad two-body contact scan: contact point × duration × strength × release/free.
    contact_pairs=[("A","C"),("A","D"),("B","C"),("B","D")]
    for a,b in contact_pairs:
        for dur in [1,4,8]:
            for strength in [.4,1.1]:
                for release_free in [0,8]:
                    actions=[{"op":"set_links","links":[["A","B"],["C","D"]],"stage":"separate"},{"op":"touch","part":a,"strength":strength,"stage":"pre_contact_stimulus_left"},{"op":"touch","part":b,"strength":strength,"stage":"pre_contact_stimulus_right"},{"op":"set_links","links":[["A","B"],["C","D"],[a,b]],"stage":"contact_on"}]
                    actions += one_layer(dur,field=.02*strength)
                    if release_free:
                        actions += [{"op":"set_links","links":[["A","B"],["C","D"]],"stage":"contact_off"}] + free_layers(release_free)
                    add("two_body_contact_wide_scan",f"contact_{a}{b}_dur{dur}_str{strength}_free{release_free}",actions,links=[(0,1),(2,3)])
    return out
def vals(trace,field): return np.array([float(t[field]) for t in trace])
def max_part_delta(t,init): return max(abs(float(t["part_P1"][p])-float(init["part_P1"][p])) for p in PARTS)
def max_zz_delta(t,init): return max(abs(float(t["pair_ZZ"][k])-float(init["pair_ZZ"][k])) for k in PAIRS)
def max_neg_delta(t,init): return max(abs(float(t["pair_negativity"][k])-float(init["pair_negativity"][k])) for k in PAIRS)
def first_cross(xs,thr):
    for i,x in enumerate(xs):
        if abs(float(x))>=thr: return i
    return None
def sign_changes(xs,eps=1e-9):
    d=np.diff(xs); s=np.sign([x if abs(x)>eps else 0 for x in d]); nz=[x for x in s if x!=0]
    return int(sum(1 for a,b in zip(nz,nz[1:]) if a*b<0))
def first_stall(trace,window=4,eps=.015):
    mags=[]
    for a,b in zip(trace,trace[1:]):
        dp=max(abs(float(b["part_P1"][p])-float(a["part_P1"][p])) for p in PARTS)
        dz=max(abs(float(b["pair_ZZ"][k])-float(a["pair_ZZ"][k])) for k in PAIRS)
        dc=abs(float(b["l1_coherence"])-float(a["l1_coherence"]))
        mags.append(max(dp,dz,dc/10))
    for i in range(0,max(0,len(mags)-window+1)):
        if max(mags[i:i+window])<eps: return i+1
    return None
def record_events(rec):
    tr=rec["trace"]; init=tr[0]; final=tr[-1]
    part_path=np.array([max_part_delta(t,init) for t in tr]); zz_path=np.array([max_zz_delta(t,init) for t in tr]); neg_path=np.array([max_neg_delta(t,init) for t in tr]); coh=vals(tr,"l1_coherence"); pur=vals(tr,"purity")
    contact_off=None
    for t in tr:
        if "contact_off" in t.get("stage","") or "contact_off" in t.get("operation",""): contact_off=int(t["step"])
    off_idx=None
    if contact_off is not None:
        for i,t in enumerate(tr):
            if int(t["step"])==contact_off: off_idx=i; break
    residual={}
    if off_idx is not None and off_idx<len(tr)-1:
        residual={"post_release_len":len(tr)-1-off_idx,"post_release_final_part_shift":jf(max(abs(float(final["part_P1"][p])-float(tr[off_idx]["part_P1"][p])) for p in PARTS)),"post_release_final_ZZ_shift":jf(max(abs(float(final["pair_ZZ"][k])-float(tr[off_idx]["pair_ZZ"][k])) for k in PAIRS)),"post_release_final_coherence_shift":jf(float(final["l1_coherence"])-float(tr[off_idx]["l1_coherence"]))}
    else:
        residual={"post_release_len":0,"post_release_final_part_shift":0.0,"post_release_final_ZZ_shift":0.0,"post_release_final_coherence_shift":0.0}
    sc=rec["scenario"]
    return {"seed":rec["seed"],"scenario_id":sc["scenario_id"],"family":sc.get("family",""),"pattern":sc.get("pattern",""),"n_steps":len(tr),"first_branch_step_part025":first_cross(part_path,.25),"first_branch_step_ZZ035":first_cross(zz_path,.35),"first_branch_step_neg010":first_cross(neg_path,.10),"coherence_reversal_count":sign_changes(coh),"purity_reversal_count":sign_changes(pur),"ZZ_path_reversal_count":sign_changes(zz_path),"stall_start_step":first_stall(tr),"final_max_part_delta":jf(part_path[-1]),"final_max_ZZ_delta":jf(zz_path[-1]),"final_max_neg_delta":jf(neg_path[-1]),"final_delta_coherence":jf(coh[-1]-coh[0]),"final_delta_purity":jf(pur[-1]-pur[0]),**residual}
def sig(row,mask):
    parts=[]
    if "population" not in mask:
        if row["final_max_part_delta"]>=.50: parts.append("P_hi")
        elif row["final_max_part_delta"]>=.25: parts.append("P_mid")
    if "ZZ" not in mask:
        if row["final_max_ZZ_delta"]>=.80: parts.append("ZZ_hi")
        elif row["final_max_ZZ_delta"]>=.35: parts.append("ZZ_mid")
    if "negativity" not in mask:
        if row["final_max_neg_delta"]>=.20: parts.append("N_hi")
        elif row["final_max_neg_delta"]>=.10: parts.append("N_mid")
    if "coherence" not in mask:
        if row["final_delta_coherence"]>=2.0: parts.append("C_up")
        elif row["final_delta_coherence"]<=-2.0: parts.append("C_down")
    if "purity" not in mask:
        if row["final_delta_purity"]<=-.20: parts.append("Pur_down")
    if row["stall_start_step"] is not None: parts.append("stall")
    return "+".join(parts) if parts else "low_visible_change"
def mask_rows(summary):
    masks=["full","hide_negativity","hide_classical","hide_population","hide_ZZ","hide_coherence","hide_purity","hide_negativity_and_classical"]
    masksets={"full":set(),"hide_negativity":{"negativity"},"hide_classical":{"classical"},"hide_population":{"population"},"hide_ZZ":{"ZZ"},"hide_coherence":{"coherence"},"hide_purity":{"purity"},"hide_negativity_and_classical":{"negativity","classical"}}
    out=[]
    for r in summary:
        sigs={m:sig(r,masksets[m]) for m in masks}
        diff=sum(1 for m in masks if sigs[m]!=sigs["full"])
        out.append({"seed":r["seed"],"scenario_id":r["scenario_id"],"family":r["family"],"pattern":r["pattern"],"full_signature":sigs["full"],"hide_negativity":sigs["hide_negativity"],"hide_classical":sigs["hide_classical"],"hide_population":sigs["hide_population"],"hide_ZZ":sigs["hide_ZZ"],"hide_coherence":sigs["hide_coherence"],"hide_purity":sigs["hide_purity"],"hide_negativity_and_classical":sigs["hide_negativity_and_classical"],"n_mask_differences_vs_full":diff})
    return out
def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out-jsonl",type=Path,default=Path("data/quantum_observation/qcell_temporal_free_contact_mask_observation_v0_seed20260710_20260719.jsonl")); ap.add_argument("--events-csv",type=Path,default=Path("data/quantum_observation/qcell_temporal_free_contact_mask_observation_v0_seed20260710_20260719_events.csv")); ap.add_argument("--mask-csv",type=Path,default=Path("data/quantum_observation/qcell_temporal_free_contact_mask_observation_v0_seed20260710_20260719_metric_masks.csv")); ap.add_argument("--manifest",type=Path,default=Path("data/quantum_observation/qcell_temporal_free_contact_mask_observation_v0_seed20260710_20260719_manifest.json")); a=ap.parse_args(); ss=specs(); rows=[]; a.out_jsonl.parent.mkdir(parents=True,exist_ok=True)
    with a.out_jsonl.open("w",encoding="utf-8") as f:
        for seed in SEEDS:
            for s in ss:
                rec=base.run(s,seed); rows.append(record_events(rec)); f.write(json.dumps(rec,ensure_ascii=False,separators=(",",":"))+"\n")
    masks=mask_rows(rows); write_csv(a.events_csv,rows); write_csv(a.mask_csv,masks)
    fam={}
    for s in ss: fam[s["family"]]=fam.get(s["family"],0)+1
    a.manifest.write_text(json.dumps({"experiment":EXPERIMENT,"date":DATE,"status":"OBSERVATION_LOG","seed_range":SEEDS,"n_macro_situations":len(ss),"n_records":len(rows),"families":fam,"policy":{"no_pass_fail":True,"no_ranking":True,"no_witness_promotion":True,"no_qpu_ready_claim":True,"parts_A_B_C_D_have_no_preassigned_roles":True},"axes":["time-resolution event detection","free observation after operation release","wide two-body contact scan","metric masking of observation quantities"],"outputs":{"jsonl":str(a.out_jsonl),"events_csv":str(a.events_csv),"mask_csv":str(a.mask_csv)}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"experiment":EXPERIMENT,"macro_situations":len(ss),"records":len(rows),"families":fam,"out_jsonl":str(a.out_jsonl),"events_csv":str(a.events_csv),"mask_csv":str(a.mask_csv),"manifest":str(a.manifest)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
