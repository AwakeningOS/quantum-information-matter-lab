#!/usr/bin/env python3
"""Export full per-condition Q-cell traces for PR 28.

This materializes the existing 2688-condition observation grid as split JSONL
shards. It is not a new experiment and does not touch the v2 witness/noise/QPU
line.
"""
from __future__ import annotations

import argparse, json, math
from pathlib import Path
from typing import Any

import numpy as np
import qcell_phenomenon_map_wide_observation as q

EXPERIMENT="qcell_phenomenon_map_wide_observation"
DATE="2026-07-09"
PAIRS=[("M","C"),("M","R"),("M","W"),("C","R"),("C","W"),("R","W")]
PREP_RY={"M":1.35,"C":0.82,"R":0.50,"W":0.26}

def jf(x:Any,n:int=12)->float: return round(float(np.real(x)),n)
def bitstr(i:int)->str: return format(i,"04b")
def pops(rho:np.ndarray)->dict[str,float]:
    p=np.real(np.diag(rho)).clip(0); p=p/p.sum()
    return {bitstr(i):jf(p[i]) for i in range(16)}
def zz_all(rho:np.ndarray)->dict[str,float]:
    return {f"ZZ_{a}{b}":jf(q.zz(rho,a,b)) for a,b in PAIRS}
def snap(rho:np.ndarray,idx:int,stage:str,op_count:int,layer:int|None=None)->dict[str,Any]:
    out={"step_index":idx,"stage":stage,"operation_count":op_count,"populations":pops(rho),"pair_correlations_ZZ":zz_all(rho),"l1_coherence":jf(q.coh(rho)),"purity":jf(np.real(np.trace(rho@rho))),"entropy_vn":jf(q.entropy(rho))}
    if layer is not None: out["layer"]=layer
    return out

def prep_ops(phase:float)->list[dict[str,Any]]:
    ops=[{"stage":"prepare","op":"Ry","target":r,"theta":jf(PREP_RY[r])} for r in q.NAMES]
    ops.append({"stage":"phase_context","op":"Rz","target":"M","theta":jf(phase)})
    return ops

def intervention_ops(name:str,target:str,intensity:float)->list[dict[str,Any]]:
    out=[]
    for r in q.members(target):
        if name=="ry_touch": out.append({"stage":"intervention","family":name,"op":"Ry","target":r,"theta":jf(.42*intensity)})
        elif name=="rz_phase_kick": out.append({"stage":"intervention","family":name,"op":"Rz","target":r,"theta":jf(.72*intensity)})
        elif name=="x_flip_touch": out.append({"stage":"intervention","family":name,"op":"Rx","target":r,"theta":jf(.55*intensity)})
        elif name=="z_dephase_patch": out.append({"stage":"intervention","family":name,"op":"Z_dephase","target":r,"p":jf(min(.95,.18*intensity))})
        elif name=="weak_measurement_patch": out.append({"stage":"intervention","family":name,"op":"Z_dephase_then_depolarize","target":r,"p_dephase":jf(min(.95,.33*intensity)),"p_depolarize":jf(min(.50,.045*intensity))})
        elif name=="reset_patch": out.append({"stage":"intervention","family":name,"op":"amplitude_reset_to_zero","target":r,"gamma":jf(min(.95,.20*intensity))})
        elif name=="echo_reversal": out.append({"stage":"intervention","family":name,"op":"Ry_Rz_Ry_inverse","target":r,"theta":jf(.50*intensity),"phi":jf(.35*intensity)})
        elif name=="saturation_drive": out.append({"stage":"intervention","family":name,"op":"3x_Ry_Rz_drive","target":r,"theta":jf(.38*intensity),"phi":jf(.24*intensity),"repeats":3})
        else: raise ValueError(name)
    return out

def layer_links(mode:str):
    if mode=="direct_chain": return [(0,1),(1,2),(2,3)],0.0
    if mode=="dephased_chain": return [(0,1),(1,2),(2,3)],.20
    if mode=="broken_middle_link": return [(0,1),(2,3)],0.0
    if mode=="ring_coupled": return [(0,1),(1,2),(2,3),(3,0)],0.0
    raise ValueError(mode)

def apply_layer(rho:np.ndarray,mode:str,layer:int)->tuple[np.ndarray,list[dict[str,Any]]]:
    ops=[]
    if mode=="field_only":
        for i,r in enumerate(q.NAMES):
            th=.11+.025*i+.010*layer; ph=.025*math.cos(layer+i)
            rho=q.oneU(q.oneU(rho,q.ry(th),r),q.rz(ph),r)
            ops.append({"stage":"propagate","layer":layer+1,"op":"field_Ry_Rz","target":r,"theta":jf(th),"phi":jf(ph)})
        return rho,ops
    if mode=="no_entangle":
        for i,r in enumerate(q.NAMES):
            th1=.13+.025*i; ph=.040*math.cos(layer+i); th2=.035*math.sin(layer+1)
            rho=q.oneU(q.oneU(q.oneU(rho,q.ry(th1),r),q.rz(ph),r),q.ry(th2),r)
            ops.append({"stage":"propagate","layer":layer+1,"op":"local_Ry_Rz_Ry","target":r,"theta1":jf(th1),"phi":jf(ph),"theta2":jf(th2)})
        return rho,ops
    links,dp=layer_links(mode)
    for i,j in links:
        th=1.05+.12*math.sin(layer+i); ph=.28*math.cos(layer+j)
        rho=q.U(rho,q.expP(q.XX[(i,j)],th)@q.expP(q.ZZ[(i,j)],ph))
        down=.62+.04*layer; up=.08*math.sin(layer+j)
        rho=q.oneU(rho,q.ry(down),q.NAMES[j]); rho=q.oneU(rho,q.rz(up),q.NAMES[i])
        ops.append({"stage":"propagate","layer":layer+1,"op":"XX_ZZ_link_then_downstream_Ry_upstream_Rz","link":q.NAMES[i]+q.NAMES[j],"theta_xx":jf(th),"phi_zz":jf(ph),"downstream":q.NAMES[j],"downstream_ry":jf(down),"upstream":q.NAMES[i],"upstream_rz":jf(up)})
    if dp:
        for r in q.NAMES: rho=q.dephase(r,r,dp) if False else rho
        for r in q.NAMES: rho=q.dephase(rho,r,dp)
        ops.append({"stage":"propagate","layer":layer+1,"op":"layer_end_all_qubit_Z_dephase","p":jf(dp)})
    return rho,ops

def run_trace(mode:str,phase:float,intervention:str,target:str,intensity:float):
    rho=q.init(phase); ops=prep_ops(phase); trace=[snap(rho,0,"initial_prepared_state",len(ops))]
    rho=q.intervene(rho,intervention,target,intensity); ops+=intervention_ops(intervention,target,intensity)
    trace.append(snap(rho,1,"after_intervention",len(ops)))
    for layer in range(q.LAYERS):
        rho,lops=apply_layer(rho,mode,layer); ops+=lops
        trace.append(snap(rho,layer+2,f"after_propagation_layer_{layer+1}",len(ops),layer+1))
    final=q.metrics(rho)
    return trace,ops,final

def flatten(m:dict[str,Any])->dict[str,float]:
    return {k:v for k,v in m.items() if isinstance(v,(int,float))}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--seed",type=int,default=20260709)
    ap.add_argument("--trace-dir",type=Path,default=Path("data/quantum_observation/qcell_phenomenon_map_wide_observation_seed20260709_traces"))
    args=ap.parse_args(); args.trace_dir.mkdir(parents=True,exist_ok=True)
    settings={"n_qubits":4,"roles":q.ROLES,"prep_ry":PREP_RY,"layers":q.LAYERS,"coupling_modes":q.COUPLINGS,"interventions":q.INTERVENTIONS,"targets":q.TARGETS,"intensities":q.INTENSITIES,"phase_contexts":[jf(p) for p in q.PHASES],"population_basis":"computational Z basis, bit order M C R W","pair_correlation_basis":"ZZ over all six unordered role pairs"}
    baselines={(m,p):q.metrics(q.propagate(q.init(p),m)) for m in q.COUPLINGS for p in q.PHASES}
    files=[]; total=0; cid=0
    for mode in q.COUPLINGS:
        for intervention in q.INTERVENTIONS:
            path=args.trace_dir/f"qcell_phenomenon_map_wide_observation_seed{args.seed}_trace_{mode}__{intervention}.jsonl"
            rows=0
            with path.open("w",encoding="utf-8") as f:
                for phase in q.PHASES:
                    for target in q.TARGETS:
                        for intensity in q.INTENSITIES:
                            cid+=1; rows+=1; total+=1
                            trace,ops,final=run_trace(mode,phase,intervention,target,intensity)
                            base=baselines[(mode,phase)]; ff=flatten(final); bf=flatten(base)
                            delta={k:jf(ff[k]-bf[k]) for k in ff if k in bf}
                            rec={"experiment":EXPERIMENT,"date":DATE,"status":"OBSERVATION_LOG","seed":args.seed,"generation_settings":settings,"condition":{"condition_id":cid,"coupling_mode":mode,"phase_context":jf(phase),"intervention":intervention,"target":target,"target_members":q.members(target),"intensity":intensity},"baseline_reference":{"coupling_mode":mode,"phase_context":jf(phase),"final_metrics":base},"operation_history":ops,"trace":trace,"final_metrics":final,"delta_vs_local_baseline":delta,"phenomenon_label":q.label({"delta_P1_W":delta["P1_W"],"delta_max_link_negativity":delta["max_link_negativity"],"delta_l1_coherence":delta["l1_coherence"],"delta_purity":delta["purity"],"target":target})}
                            f.write(json.dumps(rec,ensure_ascii=False,separators=(",",":"))+"\n")
            files.append({"path":str(path),"coupling_mode":mode,"intervention":intervention,"rows":rows,"format":"jsonl","contains":["condition settings","per-step populations","all six pair ZZ correlations","coherence","purity","operation history","seed and generation settings"]})
    manifest={"experiment":EXPERIMENT,"date":DATE,"status":"OBSERVATION_LOG","seed":args.seed,"generation_settings":settings,"trace_step_policy":"snapshots after initial preparation, after intervention, and after each of six propagation layers; operation_history records operations inside those snapshots","total_conditions":total,"sharding":"one JSONL per coupling_mode × intervention; 48 shards × 56 rows","files":files}
    mp=args.trace_dir/f"qcell_phenomenon_map_wide_observation_seed{args.seed}_trace_manifest.json"
    mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"experiment":EXPERIMENT,"conditions":total,"trace_files":len(files),"manifest":str(mp)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
