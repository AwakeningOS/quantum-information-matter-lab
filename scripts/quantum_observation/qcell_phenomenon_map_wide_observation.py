#!/usr/bin/env python3
"""Q-cell phenomenon map wide observation.

OBSERVATION_LOG only. This is separate from v2 witness, noise-margin, and
QPU-ready work; it records broad intervention responses without PASS/FAIL.
"""
from __future__ import annotations

import argparse, csv, json, math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

N=4; D=16
ROLES={"M":0,"C":1,"R":2,"W":3}; NAMES=["M","C","R","W"]
LINK_NAMES=[("M","C"),("C","R"),("R","W")]
COUPLINGS=["field_only","no_entangle","direct_chain","dephased_chain","broken_middle_link","ring_coupled"]
INTERVENTIONS=["ry_touch","rz_phase_kick","x_flip_touch","z_dephase_patch","weak_measurement_patch","reset_patch","echo_reversal","saturation_drive"]
TARGETS=["M","C","R","W","MC","CR","RW"]
INTENSITIES=[0.25,0.50,1.00,1.50]
PHASES=[0.0,math.pi/2]
LAYERS=6
I=np.eye(2,dtype=complex)
X=np.array([[0,1],[1,0]],dtype=complex)
Y=np.array([[0,-1j],[1j,0]],dtype=complex)
Z=np.array([[1,0],[0,-1]],dtype=complex)

def jf(x: Any, n:int=12)->float: return round(float(np.real(x)),n)
def kron(ops):
    out=np.array([[1]],dtype=complex)
    for op in ops: out=np.kron(out,op)
    return out

def one(op,q): return kron([op if i==q else I for i in range(N)])
def two(a,i,b,j): return kron([a if k==i else b if k==j else I for k in range(N)])
def ry(t): return np.array([[math.cos(t/2),-math.sin(t/2)],[math.sin(t/2),math.cos(t/2)]],dtype=complex)
def rz(t): return np.array([[np.exp(-1j*t/2),0],[0,np.exp(1j*t/2)]],dtype=complex)
def rx(t): return math.cos(t/2)*I-1j*math.sin(t/2)*X
ZF=[one(Z,i) for i in range(N)]; XF=[one(X,i) for i in range(N)]; YF=[one(Y,i) for i in range(N)]
XX={(i,j):two(X,i,X,j) for i,j in [(0,1),(1,2),(2,3),(3,0)]}
ZZ={(i,j):two(Z,i,Z,j) for i,j in [(0,1),(1,2),(2,3),(3,0)]}
def expP(p,t): return math.cos(t/2)*np.eye(D,dtype=complex)-1j*math.sin(t/2)*p
def U(r,u): return u@r@u.conj().T
def oneU(r,op,t): return U(r,one(op,ROLES[t]))
def dephase(r,t,p):
    q=ROLES[t]; return (1-p)*r+p*(ZF[q]@r@ZF[q])
def depol(r,t,p):
    q=ROLES[t]; return (1-p)*r+(p/3)*(XF[q]@r@XF[q]+YF[q]@r@YF[q]+ZF[q]@r@ZF[q])
def reset(r,t,g):
    e0=np.array([[1,0],[0,math.sqrt(max(0,1-g))]],dtype=complex); e1=np.array([[0,math.sqrt(max(0,g))],[0,0]],dtype=complex)
    k0=one(e0,ROLES[t]); k1=one(e1,ROLES[t]); return k0@r@k0.conj().T+k1@r@k1.conj().T

def reduce(r,keep):
    drop=[i for i in range(N) if i not in keep]; out=np.zeros((2**len(keep),2**len(keep)),dtype=complex)
    for a in range(D):
        ba=[(a>>(N-1-i))&1 for i in range(N)]; ia=sum(ba[k]<<(len(keep)-1-j) for j,k in enumerate(keep))
        for b in range(D):
            bb=[(b>>(N-1-i))&1 for i in range(N)]
            if all(ba[t]==bb[t] for t in drop):
                ib=sum(bb[k]<<(len(keep)-1-j) for j,k in enumerate(keep)); out[ia,ib]+=r[a,b]
    return out

def neg2(r2):
    eig=np.linalg.eigvalsh(r2.reshape(2,2,2,2).swapaxes(1,3).reshape(4,4)); return float(np.sum(np.abs(eig[eig<0])))
def entropy(r):
    eig=np.linalg.eigvalsh((r+r.conj().T)/2); eig=eig[eig>1e-12]
    return float(-np.sum(eig*np.log2(eig))) if eig.size else 0.0

def coh(r): return float(np.sum(np.abs(r))-np.sum(np.abs(np.diag(r))))
def p1(r,t): return float(np.real((1-np.trace(r@ZF[ROLES[t]]))/2))
def zz(r,a,b): return float(np.real(np.trace(r@(ZF[ROLES[a]]@ZF[ROLES[b]]))))

def init(phase):
    psi=np.zeros(D,dtype=complex); psi[0]=1; r=np.outer(psi,psi.conj())
    for t,th in zip(NAMES,[1.35,0.82,0.50,0.26]): r=oneU(r,ry(th),t)
    return oneU(r,rz(phase),"M")

def members(targ): return [t for t in NAMES if t in targ]
def intervene(r,name,targ,intensity):
    for t in members(targ):
        if name=="ry_touch": r=oneU(r,ry(.42*intensity),t)
        elif name=="rz_phase_kick": r=oneU(r,rz(.72*intensity),t)
        elif name=="x_flip_touch": r=oneU(r,rx(.55*intensity),t)
        elif name=="z_dephase_patch": r=dephase(r,t,min(.95,.18*intensity))
        elif name=="weak_measurement_patch": r=depol(dephase(r,t,min(.95,.33*intensity)),t,min(.50,.045*intensity))
        elif name=="reset_patch": r=reset(r,t,min(.95,.20*intensity))
        elif name=="echo_reversal":
            th=.50*intensity; r=oneU(oneU(oneU(r,ry(th),t),rz(.35*intensity),t),ry(-th),t)
        elif name=="saturation_drive":
            for _ in range(3): r=oneU(oneU(r,ry(.38*intensity),t),rz(.24*intensity),t)
        else: raise ValueError(name)
    return r

def propagate(r,mode):
    if mode in {"field_only","no_entangle"}:
        for layer in range(LAYERS):
            for i,t in enumerate(NAMES):
                if mode=="field_only": r=oneU(oneU(r,ry(.11+.025*i+.010*layer),t),rz(.025*math.cos(layer+i)),t)
                else: r=oneU(oneU(oneU(r,ry(.13+.025*i),t),rz(.040*math.cos(layer+i)),t),ry(.035*math.sin(layer+1)),t)
        return r
    if mode=="direct_chain": links=[(0,1),(1,2),(2,3)]; dp=0
    elif mode=="dephased_chain": links=[(0,1),(1,2),(2,3)]; dp=.20
    elif mode=="broken_middle_link": links=[(0,1),(2,3)]; dp=0
    elif mode=="ring_coupled": links=[(0,1),(1,2),(2,3),(3,0)]; dp=0
    else: raise ValueError(mode)
    for layer in range(LAYERS):
        for i,j in links:
            r=U(r,expP(XX[(i,j)],1.05+.12*math.sin(layer+i))@expP(ZZ[(i,j)],.28*math.cos(layer+j)))
            r=oneU(r,ry(.62+.04*layer),NAMES[j]); r=oneU(r,rz(.08*math.sin(layer+j)),NAMES[i])
        if dp:
            for t in NAMES: r=dephase(r,t,dp)
    return r

def metrics(r):
    out={"P1_M":p1(r,"M"),"P1_C":p1(r,"C"),"P1_R":p1(r,"R"),"P1_W":p1(r,"W"),"purity":float(np.real(np.trace(r@r))),"entropy_vn":entropy(r),"l1_coherence":coh(r)}
    negs=[]
    for a,b in LINK_NAMES:
        n=neg2(reduce(r,[ROLES[a],ROLES[b]])); negs.append(n); out[f"neg_{a}{b}"]=n; out[f"ZZ_{a}{b}"]=zz(r,a,b)
    out["max_link_negativity"]=max(negs); out["negativity_spread_count"]=float(sum(n>.01 for n in negs)); return out

def label(row):
    out=abs(row["delta_P1_W"]); ng=row["delta_max_link_negativity"]; cd=row["delta_l1_coherence"]; pd=row["delta_purity"]; w="W" in row["target"]
    if out<.015 and abs(ng)<.010 and abs(cd)<.15: return "quiet_or_absorbed"
    if pd<-.20 and cd<-1.00: return "collapse_like_decoherence"
    if ng>.030 and out>=.030: return "entanglement_linked_distal_response"
    if ng>.030: return "entanglement_gain_without_output_shift"
    if out>=.050 and not w: return "distal_output_response"
    if out>=.050 and w: return "direct_output_response"
    if row["delta_P1_W"]<=-.050: return "output_suppression"
    if cd>.75: return "coherence_amplification"
    if cd<-.75: return "coherence_loss"
    return "mixed_small_response"

def summarize(rows,keys):
    groups=defaultdict(list)
    for r in rows: groups[tuple(r[k] for k in keys)].append(r)
    out=[]
    for k,vals in sorted(groups.items()):
        c=Counter(v["phenomenon_label"] for v in vals)
        out.append({**{keys[i]:k[i] for i in range(len(keys))},"n":len(vals),"mean_abs_delta_P1_W":jf(np.mean([abs(v["delta_P1_W"]) for v in vals])),"mean_delta_P1_W":jf(np.mean([v["delta_P1_W"] for v in vals])),"mean_delta_l1_coherence":jf(np.mean([v["delta_l1_coherence"] for v in vals])),"mean_delta_purity":jf(np.mean([v["delta_purity"] for v in vals])),"mean_delta_max_link_negativity":jf(np.mean([v["delta_max_link_negativity"] for v in vals])),"top_label":c.most_common(1)[0][0],"label_counts":dict(c)})
    return out

def write_csv(path,rows,fields=None):
    path.parent.mkdir(parents=True,exist_ok=True); fields=fields or list(rows[0].keys())
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--seed",type=int,default=20260709)
    ap.add_argument("--out-json",type=Path,default=Path("data/quantum_observation/qcell_phenomenon_map_wide_observation_seed20260709.json"))
    ap.add_argument("--detail-csv",type=Path,default=Path("data/quantum_observation/qcell_phenomenon_map_wide_observation_seed20260709_detail.csv"))
    ap.add_argument("--summary-csv",type=Path,default=Path("data/quantum_observation/qcell_phenomenon_map_wide_observation_seed20260709_summary.csv")); args=ap.parse_args()
    np.random.default_rng(args.seed)
    bases={(m,p):metrics(propagate(init(p),m)) for m in COUPLINGS for p in PHASES}; rows=[]
    keys=["P1_M","P1_C","P1_R","P1_W","purity","entropy_vn","l1_coherence","max_link_negativity","negativity_spread_count","neg_MC","neg_CR","neg_RW","ZZ_MC","ZZ_CR","ZZ_RW"]
    for m in COUPLINGS:
        for p in PHASES:
            base=bases[(m,p)]
            for inter in INTERVENTIONS:
                for targ in TARGETS:
                    for inten in INTENSITIES:
                        met=metrics(propagate(intervene(init(p),inter,targ,inten),m)); row={"coupling_mode":m,"phase_context":jf(p),"intervention":inter,"target":targ,"intensity":inten}
                        for k,v in met.items(): row[k]=jf(v)
                        for k in keys: row[f"baseline_{k}"]=jf(base[k]); row[f"delta_{k}"]=jf(met[k]-base[k])
                        row["phenomenon_label"]=label(row); rows.append(row)
    by_c=summarize(rows,["coupling_mode"]); by_i=summarize(rows,["intervention"]); by_ci=summarize(rows,["coupling_mode","intervention"])
    selected=sorted(rows,key=lambda r: abs(r["delta_P1_W"])+abs(r["delta_l1_coherence"])/10+abs(r["delta_max_link_negativity"])*5,reverse=True)[:40]
    result={"experiment":"qcell_phenomenon_map_wide_observation","date":"2026-07-09","layer":"QUANTUM_OBSERVATION","status":"OBSERVATION_LOG","claim_policy":{"purpose":"wide observation map of Q-cell responses to diverse interventions","not_purpose":["v2 witness improvement","noise-margin improvement","QPU-ready conversion","single-hypothesis proof","performance improvement"],"promotion":"no PASS/FAIL claim; labels are mechanical observation tags"},"config":{"seed":args.seed,"n_qubits":N,"roles":ROLES,"layers":LAYERS,"coupling_modes":COUPLINGS,"interventions":INTERVENTIONS,"targets":TARGETS,"intensities":INTENSITIES,"phase_contexts":[jf(p) for p in PHASES],"n_rows":len(rows)},"label_counts":dict(Counter(r["phenomenon_label"] for r in rows)),"summary_by_coupling":by_c,"summary_by_intervention":by_i,"summary_by_coupling_intervention":by_ci,"selected_high_magnitude_observations":selected,"observation_notes":["Observation map only; no winner or PASS/FAIL is promoted.","Baselines are local to coupling_mode and phase_context.","Compact NumPy density-matrix sandbox; not backend-calibrated and not a QPU result.","Independent from v2 witness/noise-margin/QPU-ready code."]}
    args.out_json.parent.mkdir(parents=True,exist_ok=True); args.out_json.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    detail=["coupling_mode","phase_context","intervention","target","intensity","phenomenon_label","P1_M","P1_C","P1_R","P1_W","delta_P1_W","purity","delta_purity","entropy_vn","delta_entropy_vn","l1_coherence","delta_l1_coherence","neg_MC","neg_CR","neg_RW","max_link_negativity","delta_max_link_negativity","ZZ_MC","ZZ_CR","ZZ_RW","delta_ZZ_RW"]
    write_csv(args.detail_csv,rows,detail); write_csv(args.summary_csv,by_ci,["coupling_mode","intervention","n","mean_abs_delta_P1_W","mean_delta_P1_W","mean_delta_l1_coherence","mean_delta_purity","mean_delta_max_link_negativity","top_label","label_counts"])
    print(json.dumps({"experiment":result["experiment"],"status":result["status"],"n_rows":len(rows),"label_counts":result["label_counts"],"out_json":str(args.out_json),"detail_csv":str(args.detail_csv),"summary_csv":str(args.summary_csv)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
