#!/usr/bin/env python3
"""Untuned Q-cell situation observation: no PASS/FAIL, no roles, no witness."""
from __future__ import annotations
import argparse,csv,itertools,json,math
from pathlib import Path
from typing import Any
import numpy as np
EXPERIMENT="qcell_untamed_situation_observation_v0"; DATE="2026-07-09"; PARTS=list("ABCD"); N=4; D=16
I=np.eye(2,dtype=complex); X=np.array([[0,1],[1,0]],complex); Y=np.array([[0,-1j],[1j,0]],complex); Z=np.array([[1,0],[0,-1]],complex)
def jf(x:Any,n:int=12)->float: return round(float(np.real(x)),n)
def kron(ops):
    o=np.array([[1]],complex)
    for a in ops:o=np.kron(o,a)
    return o
def one(op,q): return kron([op if i==q else I for i in range(N)])
def two(a,i,b,j): return kron([a if k==i else b if k==j else I for k in range(N)])
def ry(t): return np.array([[math.cos(t/2),-math.sin(t/2)],[math.sin(t/2),math.cos(t/2)]],complex)
def rz(t): return np.array([[np.exp(-1j*t/2),0],[0,np.exp(1j*t/2)]],complex)
def rx(t): return math.cos(t/2)*I-1j*math.sin(t/2)*X
ZF=[one(Z,i) for i in range(N)]; XF=[one(X,i) for i in range(N)]; YF=[one(Y,i) for i in range(N)]
def U(r,u): return u@r@u.conj().T
def single(r,g,p): return U(r,one(g,PARTS.index(p)))
def expP(op,t): return math.cos(t/2)*np.eye(D,dtype=complex)-1j*math.sin(t/2)*op
def link(r,i,j,th,ph): return U(r,expP(two(X,i,X,j),th)@expP(two(Z,i,Z,j),ph))
def dephase(r,p,prob): z=ZF[PARTS.index(p)]; return (1-prob)*r+prob*(z@r@z)
def depol(r,p,prob):
    q=PARTS.index(p); return (1-prob)*r+(prob/3)*(XF[q]@r@XF[q]+YF[q]@r@YF[q]+ZF[q]@r@ZF[q])
def reset0(r,p,g):
    e0=np.array([[1,0],[0,math.sqrt(max(0,1-g))]],complex); e1=np.array([[0,math.sqrt(max(0,g))],[0,0]],complex)
    k0=one(e0,PARTS.index(p)); k1=one(e1,PARTS.index(p)); return k0@r@k0.conj().T+k1@r@k1.conj().T
def red(r,keep):
    drop=[i for i in range(N) if i not in keep]; out=np.zeros((2**len(keep),2**len(keep)),complex)
    for a in range(D):
        ba=[(a>>(N-1-i))&1 for i in range(N)]; ia=sum(ba[k]<<(len(keep)-1-j) for j,k in enumerate(keep))
        for b in range(D):
            bb=[(b>>(N-1-i))&1 for i in range(N)]
            if all(ba[t]==bb[t] for t in drop): out[ia,sum(bb[k]<<(len(keep)-1-j) for j,k in enumerate(keep))]+=r[a,b]
    return out
def neg(r,a,b):
    m=red(r,[PARTS.index(a),PARTS.index(b)]).reshape(2,2,2,2).swapaxes(1,3).reshape(4,4)
    e=np.linalg.eigvalsh(m); return float(np.sum(np.abs(e[e<0])))
def entropy(r):
    e=np.linalg.eigvalsh((r+r.conj().T)/2); e=e[e>1e-12]; return float(-np.sum(e*np.log2(e))) if e.size else 0.0
def coh(r): return float(np.sum(np.abs(r))-np.sum(np.abs(np.diag(r))))
def p1(r,p): return float(np.real((1-np.trace(r@ZF[PARTS.index(p)]))/2))
def zz(r,a,b): return float(np.real(np.trace(r@(ZF[PARTS.index(a)]@ZF[PARTS.index(b)]))))
def pop(r):
    p=np.real(np.diag(r)).clip(0); p=p/p.sum(); return {format(i,"04b"):jf(p[i]) for i in range(D)}
def cinit(kind,rng):
    return {"empty":np.zeros(4),"biased_left":np.linspace(.85,.15,4),"biased_right":np.linspace(.15,.85,4),"alternating":np.array([.85,.2,.85,.2]),"mixed":np.full(4,.5)}.get(kind,rng.uniform(.1,.9,4) if kind=="random_product" else np.linspace(.25,.65,4)).astype(float)
def qinit(kind,rng):
    psi=np.zeros(D,complex); psi[0]=1; r=np.outer(psi,psi.conj())
    angles={"empty":[0,0,0,0],"biased_left":[1.25,.45,.18,.05],"biased_right":[.05,.18,.45,1.25],"alternating":[1.1,.25,1.1,.25]}.get(kind,[.72,.83,.94,1.05])
    if kind=="random_product": angles=list(rng.uniform(.05,1.35,4))
    for p,t in zip(PARTS,angles): r=single(r,ry(float(t)),p)
    if kind=="seed_entangled": r=link(r,0,1,1.15,.25)
    if kind=="mixed":
        for p in PARTS: r=depol(r,p,.18)
    return r
def csnap(v,links):
    c=v-v.mean(); pair={PARTS[i]+PARTS[j]:jf(c[i]*c[j]) for i,j in itertools.combinations(range(4),2)}; p=v.clip(1e-9,1-1e-9)
    return {"part_values":{PARTS[i]:jf(v[i]) for i in range(4)},"pair_centered_product":pair,"bit_entropy_mean":jf(np.mean(-(p*np.log2(p)+(1-p)*np.log2(1-p)))),"active_links":[PARTS[i]+PARTS[j] for i,j in links]}
def snap(r,v,links,stage,step,op):
    pairs=list(itertools.combinations(PARTS,2))
    return {"step":step,"stage":stage,"operation":op,"part_P1":{p:jf(p1(r,p)) for p in PARTS},"population":pop(r),"pair_ZZ":{a+b:jf(zz(r,a,b)) for a,b in pairs},"pair_negativity":{a+b:jf(neg(r,a,b)) for a,b in pairs},"l1_coherence":jf(coh(r)),"purity":jf(np.real(np.trace(r@r))),"entropy_vn":jf(entropy(r)),"classical_parallel":csnap(v,links)}
def prop(r,links,layer,field=0,dephase_p=0):
    for i,j in links:
        r=link(r,i,j,.62+.15*math.sin(layer+.7*i)+field,.18*math.cos(layer+j)); r=single(r,ry(.18+.02*layer),PARTS[j]); r=single(r,rz(.05*math.sin(layer+j)),PARTS[i])
    for p in PARTS:
        if dephase_p: r=dephase(r,p,dephase_p)
    return r
def cprop(v,links,field=0,leak=.03):
    n=v.copy()
    for i,j in links:
        flow=.17*(v[i]-v[j])+field*.05; n[j]+=flow; n[i]-=.35*flow
    return np.clip((1-leak)*n+leak*.5,0,1)
def specs():
    out=[]; sid=0
    for order in itertools.permutations(PARTS):
        sid+=1; acts=[]
        for p in order: acts += [{"op":"touch","part":p,"strength":.75},{"op":"propagate","layers":1}]
        out.append({"scenario_id":sid,"family":"all_24_touch_orders","initial":"default","links":[(0,1),(1,2),(2,3)],"pattern":"".join(order),"actions":acts})
    patterns=[]; patterns.append(("fast_repeat_A",[{"op":"touch","part":"A","strength":.5},{"op":"propagate","layers":1}]*16)); patterns.append(("slow_repeat_A",[{"op":"touch","part":"A","strength":.5},{"op":"propagate","layers":3},{"op":"idle","leak":.03}]*8))
    irr=[]
    for p,s,l in [("A",.4,1),("C",1.2,2),("B",.7,1),("D",1.5,3),("A",.2,1),("B",1.4,2),("D",.4,1),("C",.9,2)]: irr += [{"op":"touch","part":p,"strength":s},{"op":"propagate","layers":l}]
    patterns.append(("irregular_ABCD",irr)); patterns.append(("burst_then_idle",[{"op":"touch","part":"B","strength":.35},{"op":"propagate","layers":1}]*5+[{"op":"touch","part":"B","strength":2.0},{"op":"propagate","layers":4}]+[{"op":"idle","dephase_p":.04},{"op":"propagate","layers":1}]*5)); patterns.append(("stop_then_reverse_phase",[{"op":"touch","part":"A","strength":.8},{"op":"propagate","layers":2},{"op":"touch","part":"B","strength":.8},{"op":"propagate","layers":2},{"op":"idle"},{"op":"idle"},{"op":"phase","part":"B","strength":-1},{"op":"phase","part":"A","strength":-1},{"op":"propagate","layers":4}]))
    for name,acts in patterns: sid+=1; out.append({"scenario_id":sid,"family":"rhythm_stop_burst","initial":"default","links":[(0,1),(1,2),(2,3)],"pattern":name,"actions":acts})
    for name,acts in [("delete_A_then_run",[{"op":"reset","part":"A","gamma":.95},{"op":"propagate","layers":10}]),("delete_B_then_run",[{"op":"reset","part":"B","gamma":.95},{"op":"propagate","layers":10}]),("delete_C_then_run",[{"op":"reset","part":"C","gamma":.95},{"op":"propagate","layers":10}]),("delete_D_then_run",[{"op":"reset","part":"D","gamma":.95},{"op":"propagate","layers":10}]),("damage_B_restore_B",[{"op":"depolarize","parts":["B"],"p":.55},{"op":"propagate","layers":4},{"op":"restore","part":"B","strength":.85},{"op":"propagate","layers":8}]),("damage_C_restore_A",[{"op":"depolarize","parts":["C"],"p":.55},{"op":"propagate","layers":4},{"op":"restore","part":"A","strength":.85},{"op":"propagate","layers":8}]),("swap_A_D_midrun",[{"op":"touch","part":"A","strength":1.1},{"op":"propagate","layers":3},{"op":"swap","a":"A","b":"D"},{"op":"propagate","layers":7}]),("cut_middle_then_reconnect",[{"op":"set_links","links":[["A","B"],["C","D"]]},{"op":"touch","part":"B","strength":1.2},{"op":"propagate","layers":5},{"op":"set_links","links":[["A","B"],["B","C"],["C","D"]]},{"op":"propagate","layers":6}])]: sid+=1; out.append({"scenario_id":sid,"family":"damage_restore_rewire","initial":"default","links":[(0,1),(1,2),(2,3)],"pattern":name,"actions":acts})
    for name,lks in [("ring",[["A","B"],["B","C"],["C","D"],["D","A"]]),("cross",[["A","C"],["B","D"]]),("long_plus_chain",[["A","B"],["B","C"],["C","D"],["A","D"]]),("star_B",[["B","A"],["B","C"],["B","D"]]),("single_AD",[["A","D"]])]: sid+=1; out.append({"scenario_id":sid,"family":"topology_mutation","initial":"default","links":[(0,1),(1,2),(2,3)],"pattern":name,"actions":[{"op":"set_links","links":lks},{"op":"touch","part":"A","strength":.8},{"op":"touch","part":"D","strength":.8},{"op":"propagate","layers":10,"field":.02}]})
    for kind in ["empty","biased_left","biased_right","alternating","random_product","mixed","seed_entangled"]: sid+=1; out.append({"scenario_id":sid,"family":"initial_environment_variation","initial":kind,"links":[(0,1),(1,2),(2,3)],"pattern":kind,"actions":[{"op":"touch","part":"B","strength":.9},{"op":"propagate","layers":5,"field":.08},{"op":"dephase","parts":["A","D"],"p":.18},{"op":"propagate","layers":5,"field":-.04}]})
    cell1=[["A","B"]]; cell2=[["C","D"]]
    for name,acts in [("touch_A_contact_BC",[{"op":"set_links","links":cell1+cell2},{"op":"touch","part":"A","strength":1},{"op":"propagate","layers":4},{"op":"set_links","links":cell1+cell2+[["B","C"]]},{"op":"propagate","layers":8}]),("separate_recontact",[{"op":"set_links","links":cell1+cell2+[["B","C"]]},{"op":"touch","part":"A","strength":.8},{"op":"propagate","layers":3},{"op":"set_links","links":cell1+cell2},{"op":"propagate","layers":3},{"op":"set_links","links":cell1+cell2+[["B","C"]]},{"op":"propagate","layers":6}]),("cross_contact",[{"op":"set_links","links":cell1+cell2+[["A","D"],["B","C"]]},{"op":"touch","part":"A","strength":.7},{"op":"touch","part":"D","strength":.7},{"op":"propagate","layers":8}]),("damage_left_cell_then_contact",[{"op":"depolarize","parts":["A","B"],"p":.5},{"op":"set_links","links":cell1+cell2+[["B","C"]]},{"op":"propagate","layers":10}]),("shared_noise_then_contact",[{"op":"dephase","parts":PARTS,"p":.1},{"op":"set_links","links":cell1+cell2+[["B","C"]]},{"op":"touch","part":"C","strength":1.2},{"op":"propagate","layers":8}])]: sid+=1; out.append({"scenario_id":sid,"family":"two_cell_contact","initial":"default","links":[(0,1),(2,3)],"pattern":name,"actions":acts})
    return out
def run(spec,seed):
    rng=np.random.default_rng(seed+spec["scenario_id"]); r=qinit(spec.get("initial","default"),rng); v=cinit(spec.get("initial","default"),rng); links=list(spec.get("links",[(0,1),(1,2),(2,3)])); trace=[snap(r,v,links,"initial",0,"initial_state")]; hist=[]; step=0
    for a in spec["actions"]:
        step+=1; op=a["op"]
        if op=="touch": r=single(single(r,ry(.45*a.get("strength",1)),a["part"]),rz(.25*a.get("strength",1)),a["part"]); v[PARTS.index(a["part"])] = np.clip(v[PARTS.index(a["part"])] + .35*a.get("strength",1),0,1)
        elif op=="phase": r=single(r,rz(.8*a.get("strength",1)),a["part"])
        elif op=="dephase":
            for p in a.get("parts",PARTS): r=dephase(r,p,a.get("p",.2))
            v=(1-a.get("p",.2))*v+a.get("p",.2)*.5
        elif op=="depolarize":
            for p in a.get("parts",PARTS): r=depol(r,p,a.get("p",.1))
            v=(1-a.get("p",.1))*v+a.get("p",.1)*rng.uniform(.35,.65,4)
        elif op=="reset": r=reset0(r,a["part"],a.get("gamma",.8)); v[PARTS.index(a["part"])]*=1-a.get("gamma",.8)
        elif op=="restore": r=single(r,ry(a.get("strength",.5)),a["part"]); v[PARTS.index(a["part"])] = .5*v[PARTS.index(a["part"])] + .5
        elif op=="swap": r=link(r,PARTS.index(a["a"]),PARTS.index(a["b"]),1,.2); ia,ib=PARTS.index(a["a"]),PARTS.index(a["b"]); v[ia],v[ib]=v[ib],v[ia]
        elif op=="set_links": links=[(PARTS.index(x),PARTS.index(y)) for x,y in a["links"]]
        elif op=="propagate":
            for k in range(a.get("layers",1)): r=prop(r,links,step+k,a.get("field",0),a.get("dephase_p",0)); v=cprop(v,links,a.get("field",0),a.get("leak",.03))
        elif op=="idle":
            v=(1-a.get("leak",.02))*v+a.get("leak",.02)*.5
            for p in PARTS:
                if a.get("dephase_p",0): r=dephase(r,p,a["dephase_p"])
        hist.append(a); trace.append(snap(r,v,links,a.get("stage",op),step,json.dumps(a,sort_keys=True)))
    return {"experiment":EXPERIMENT,"date":DATE,"status":"OBSERVATION_LOG","seed":seed,"scenario":{k:v for k,v in spec.items() if k!="actions"},"generation_settings":{"parts_are_unassigned":True,"part_names":PARTS,"no_pass_fail":True,"no_witness_promotion":True,"classical_parallel_is_reference_context_not_winner":True},"operation_history":hist,"trace":trace}
def summarize(rec):
    f,l=rec["trace"][0],rec["trace"][-1]
    pd={p:jf(l["part_P1"][p]-f["part_P1"][p]) for p in PARTS}; zd={k:jf(l["pair_ZZ"][k]-f["pair_ZZ"][k]) for k in l["pair_ZZ"]}; nd={k:jf(l["pair_negativity"][k]-f["pair_negativity"][k]) for k in l["pair_negativity"]}
    return {"scenario_id":rec["scenario"]["scenario_id"],"family":rec["scenario"].get("family",""),"pattern":rec["scenario"].get("pattern",""),"n_steps":len(rec["trace"]),"delta_l1_coherence":jf(l["l1_coherence"]-f["l1_coherence"]),"delta_purity":jf(l["purity"]-f["purity"]),"max_abs_part_P1_delta":jf(max(abs(x) for x in pd.values())),"max_abs_ZZ_delta":jf(max(abs(x) for x in zd.values())),"max_abs_negativity_delta":jf(max(abs(x) for x in nd.values())),"part_P1_delta_json":json.dumps(pd,sort_keys=True),"pair_ZZ_delta_json":json.dumps(zd,sort_keys=True),"pair_negativity_delta_json":json.dumps(nd,sort_keys=True)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--seed",type=int,default=20260709); ap.add_argument("--out-jsonl",type=Path,default=Path("data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709.jsonl")); ap.add_argument("--summary-csv",type=Path,default=Path("data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709_summary.csv")); ap.add_argument("--manifest",type=Path,default=Path("data/quantum_observation/qcell_untamed_situation_observation_v0_seed20260709_manifest.json")); a=ap.parse_args(); rows=[]; ss=specs(); a.out_jsonl.parent.mkdir(parents=True,exist_ok=True)
    with a.out_jsonl.open("w",encoding="utf-8") as f:
        for s in ss:
            r=run(s,a.seed); rows.append(summarize(r)); f.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
    with a.summary_csv.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    a.manifest.write_text(json.dumps({"experiment":EXPERIMENT,"date":DATE,"status":"OBSERVATION_LOG","seed":a.seed,"n_scenarios":len(ss),"families":sorted({s["family"] for s in ss}),"policy":{"no_pass_fail":True,"no_ranking":True,"no_single_witness":True,"no_qpu_ready_claim":True,"parts_A_B_C_D_have_no_preassigned_roles":True},"contents_per_scenario":["condition/situation settings","operation history","full quantum trajectory snapshots","population for all basis states","all pair ZZ correlations","all pair negativity values","coherence","purity","entropy","classical parallel trajectory"]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"experiment":EXPERIMENT,"n_scenarios":len(ss),"jsonl":str(a.out_jsonl),"summary_csv":str(a.summary_csv),"manifest":str(a.manifest)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
