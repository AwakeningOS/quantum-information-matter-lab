#!/usr/bin/env python3
"""Export full per-condition Q-cell traces for PR 28.

This is a trace exporter for qcell_phenomenon_map_wide_observation. It does not
add a new experiment. It materializes the 2688-condition observation grid as
split JSONL shards with per-step populations, all pair ZZ correlations,
coherence, purity, operation history, seed, and generation settings.
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

ROLE_NAMES=["M","C","R","W"]
def target_members(target:str)->list[str]: return [r for r in ROLE_NAMES if r in target]
def label_from_delta(delta:dict[str,float],target:str)->str:
    out=abs(delta["P1_W"]); ng=delta["max_link_negativity"]; cd=delta["l1_coherence"]; pd=delta["purity"]; direct_w="W" in target
    if out<.015 and abs(ng)<.010 and abs(cd)<.15: return "quiet_or_absorbed"
    if pd<-.20 and cd<-1.00: return "collapse_like_decoherence"
    if ng>.030 and out>=.030: return "entanglement_linked_distal_response"
    if ng>.030: return "entanglement_gain_without_output_shift"
    if out>=.050 and not direct_w: return "distal_output_response"
    if out>=.050 and direct_w: return "direct_output_response"
    if delta["P1_W"]<=-.050: return "output_suppression"
    if cd>.75: return "coherence_amplification"
    if cd<-.75: return "coherence_loss"
    return "mixed_small_response"

def jf(x:Any,n:int=12)->float: return round(float(np.real(x)),n)
def bitstr(i:int)->str: return format(i,"04b")
def pops(rho:np.ndarray)->dict[str,float]:
    p=np.real(np.diag(rho)).clip(0); p=p/p.sum()
    return {bitstr(i):jf(p[i]) for i in range(16)}
def zz_all(rho:np.ndarray)->dict[str,float]:
    return {f"ZZ_{a}{b}":jf(q.zz_expectation(rho,a,b)) for a,b in PAIRS}
def snap(rho:np.ndarray,idx:int,stage:str,op_count:int,layer:int|None=None)->dict[str,Any]:
    out={"step_index":idx,"stage":stage,"operation_count":op_count,"populations":pops(rho),"pair_correlations_ZZ":zz_all(rho),"l1_coherence":jf(q.l1_coherence(rho)),"purity":jf(np.real(np.trace(rho@rho))),"entropy_vn":jf(q.entropy_vn(rho))}
    if layer is not None: out["layer"]=layer
    return out

def prep_ops(phase:float)->list[dict[str,Any]]:
    ops=[{"stage":"prepare","op":"Ry","target":r,"theta":jf(PREP_RY[r])} for r in ROLE_NAMES]
    ops.append({"stage":"phase_context","op":"Rz","target":"M","theta":jf(phase)})
    return ops

def intervention_ops(name:str,target:str,intensity:float)->list[dict[str,Any]]:
    out=[]
    for r in target_members(target):
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
        for i,r in enumerate(ROLE_NAMES):
            th=.11+.025*i+.010*layer; ph=.025*math.cos(layer+i)
            rho=q.apply_single(q.apply_single(rho,q.ry(th),r),q.rz(ph),r)
            ops.append({"stage":"propagate","layer":layer+1,"op":"field_Ry_Rz","target":r,"theta":jf(th),"phi":jf(ph)})
        return rho,ops
    if mode=="no_entangle":
        for i,r in enumerate(ROLE_NAMES):
            th1=.13+.025*i; ph=.040*math.cos(layer+i); th2=.035*math.sin(layer+1)
            rho=q.apply_single(q.apply_single(q.apply_single(rho,q.ry(th1),r),q.rz(ph),r),q.ry(th2),r)
            ops.append({"stage":"propagate","layer":layer+1,"op":"local_Ry_Rz_Ry","target":r,"theta1":jf(th1),"phi":jf(ph),"theta2":jf(th2)})
        return rho,ops
    links,dp=layer_links(mode)
    for i,j in links:
        th=1.05+.12*math.sin(layer+i); ph=.28*math.cos(layer+j)
        rho=q.apply_u(rho,q.exp_pauli(q.XX[(i,j)],th)@q.exp_pauli(q.ZZ[(i,j)],ph))
        down=.62+.04*layer; up=.08*math.sin(layer+j)
        rho=q.apply_single(rho,q.ry(down),ROLE_NAMES[j]); rho=q.apply_single(rho,q.rz(up),ROLE_NAMES[i])
        ops.append({"stage":"propagate","layer":layer+1,"op":"XX_ZZ_link_then_downstream_Ry_upstream_Rz","link":ROLE_NAMES[i]+ROLE_NAMES[j],"theta_xx":jf(th),"phi_zz":jf(ph),"downstream":ROLE_NAMES[j],"downstream_ry":jf(down),"upstream":ROLE_NAMES[i],"upstream_rz":jf(up)})
    if dp:
        for r in ROLE_NAMES: rho=q.dephase_q(rho,r,dp)
        ops.append({"stage":"propagate","layer":layer+1,"op":"layer_end_all_qubit_Z_dephase","p":jf(dp)})
    return rho,ops

def run_trace(mode:str,phase:float,intervention:str,target:str,intensity:float):
    rho=q.init_qcell(phase); ops=prep_ops(phase); trace=[snap(rho,0,"initial_prepared_state",len(ops))]
    rho=q.apply_intervention(rho,intervention,target,intensity); iops=intervention_ops(intervention,target,intensity); ops+=iops
    trace.append(snap(rho,1,"after_intervention",len(ops)))
    for layer in range(q.LAYERS):
        rho,lops=apply_layer(rho,mode,layer); ops+=lops
        trace.append(snap(rho,layer+2,f"after_propagation_layer_{layer+1}",len(ops),layer+1))
    final=q.metrics(rho)
    return trace,ops,final

def baseline_final(mode:str,phase:float)->dict[str,Any]:
    return q.metrics(q.propagate(q.init_qcell(phase),mode))
def flatten(m:dict[str,Any])->dict[str,float]:
    out={k:v for k,v in m.items() if isinstance(v,(int,float))}
    for k in ["ZZ_MC","ZZ_CR","ZZ_RW","neg_MC","neg_CR","neg_RW"]:
        if k in m: out[k]=m[k]
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--seed",type=int,default=20260709)
    ap.add_argument("--trace-dir",type=Path,default=Path("data/quantum_observation/qcell_phenomenon_map_wide_observation_seed20260709_traces"))
    args=ap.parse_args(); args.trace_dir.mkdir(parents=True,exist_ok=True)
    settings={"n_qubits":4,"roles":q.QUBITS,"prep_ry":PREP_RY,"layers":q.LAYERS,"coupling_modes":q.COUPLING_MODES,"interventions":q.INTERVENTIONS,"targets":q.TARGETS,"intensities":q.INTENSITIES,"phase_contexts":[jf(p) for p in q.PHASE_CONTEXTS],"population_basis":"computational Z basis, bit order M C R W","pair_correlation_basis":"ZZ over all six unordered role pairs"}
    baselines={(m,p):baseline_final(m,p) for m in q.COUPLING_MODES for p in q.PHASE_CONTEXTS}
    files=[]; total=0; cid=0
    for mode in q.COUPLING_MODES:
        for intervention in q.INTERVENTIONS:
            path=args.trace_dir/f"qcell_phenomenon_map_wide_observation_seed{args.seed}_trace_{mode}__{intervention}.jsonl"
            rows=0
            with path.open("w",encoding="utf-8") as f:
                for phase in q.PHASE_CONTEXTS:
                    for target in q.TARGETS:
                        for intensity in q.INTENSITIES:
                            cid+=1; rows+=1; total+=1
                            trace,ops,final=run_trace(mode,phase,intervention,target,intensity)
                            base=baselines[(mode,phase)]; ff=flatten(final); bf=flatten(base)
                            delta={k:jf(ff[k]-bf[k]) for k in ff if k in bf}
                            rec={"experiment":EXPERIMENT,"date":DATE,"status":"OBSERVATION_LOG","seed":args.seed,"generation_settings":settings,"condition":{"condition_id":cid,"coupling_mode":mode,"phase_context":jf(phase),"intervention":intervention,"target":target,"target_members":target_members(target),"intensity":intensity},"baseline_reference":{"coupling_mode":mode,"phase_context":jf(phase),"final_metrics":base},"operation_history":ops,"trace":trace,"final_metrics":final,"delta_vs_local_baseline":delta,"phenomenon_label":label_from_delta(delta,target)}
                            f.write(json.dumps(rec,ensure_ascii=False,separators=(",",":"))+"\n")
            files.append({"path":str(path),"coupling_mode":mode,"intervention":intervention,"rows":rows,"format":"jsonl","contains":["condition settings","per-step populations","all six pair ZZ correlations","coherence","purity","operation history","seed and generation settings"]})
    manifest={"experiment":EXPERIMENT,"date":DATE,"status":"OBSERVATION_LOG","seed":args.seed,"generation_settings":settings,"trace_step_policy":"snapshots after initial preparation, after intervention, and after each of six propagation layers; operation_history records operations inside those snapshots","total_conditions":total,"sharding":"one JSONL per coupling_mode × intervention; 48 shards × 56 rows","files":files}
    mp=args.trace_dir/f"qcell_phenomenon_map_wide_observation_seed{args.seed}_trace_manifest.json"
    mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"experiment":EXPERIMENT,"conditions":total,"trace_files":len(files),"manifest":str(mp)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
