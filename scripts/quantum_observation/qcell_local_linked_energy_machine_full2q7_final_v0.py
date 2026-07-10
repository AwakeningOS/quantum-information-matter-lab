#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-cell local linked energy machine, full 2^7 final v0 runner.

OBSERVATION_LOG only.
No life/metabolism/self-repair/homeostasis/optimization/quantum-advantage claim.

Full cycle Hilbert space:
    R,E,A,B,C,D,W = 7 qubits = 128-dimensional density matrix.

Continuing Q-cell body:
    E,A,B,C,D = 5 qubits = 32-dimensional density matrix.

The body is never reset mid-run. R and W are local ports. At each cycle:
fresh R is prepared by the fixed schedule, W begins empty, local unitaries act,
R/W are recorded into the ledger, then traced out. No global state is read to
choose operations.
"""
from __future__ import annotations

import argparse, csv, gzip, json, math, os, pickle, time
import multiprocessing as mp
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import numpy as np

N_SYS = 5
N_FULL = 7
DIM_SYS = 2 ** N_SYS
DIM_FULL = 2 ** N_FULL
SYS_NAMES = ["E", "A", "B", "C", "D"]
FULL_NAMES = ["R", "E", "A", "B", "C", "D", "W"]
MAIN_SEEDS = list(range(20260710, 20260810))
CHECKPOINTS = [0,1,2,5,10,20,49,50,75,99,100,124,125,149,150,174,175,199,200]

SYS_BITS = np.array([[(i >> (N_SYS - 1 - q)) & 1 for q in range(N_SYS)] for i in range(DIM_SYS)], dtype=np.float64)
I_SYS = np.eye(DIM_SYS, dtype=np.complex128)
MAXMIX_SYS = I_SYS / DIM_SYS
OFFDIAG_SYS = ~np.eye(DIM_SYS, dtype=bool)
PAIR_SYS = [(0,1,"EA"),(1,2,"AB"),(2,3,"BC"),(3,4,"CD"),(1,4,"AD")]
HAMMING_SYS = np.sum(SYS_BITS[:, None, :] != SYS_BITS[None, :, :], axis=2)

EMBED_CACHE: dict[tuple, np.ndarray] = {}

def herm(r): return 0.5 * (r + r.conj().T)

def entropy_vn(rho, base2=True):
    vals = np.linalg.eigvalsh(herm(rho)).real
    vals = np.maximum(vals, 0.0)
    vals = vals[vals > 1e-14]
    if vals.size == 0: return 0.0
    log = np.log2 if base2 else np.log
    return float(-np.sum(vals * log(vals)))

def trace_distance(a,b):
    vals = np.linalg.eigvalsh(herm(a-b)).real
    return float(0.5 * np.sum(np.abs(vals)))

def purity(rho): return float(np.real(np.trace(rho @ rho)))
def l1_coherence(rho): return float(np.sum(np.abs(rho[OFFDIAG_SYS])))
def sys_energy(rho):
    diag = np.real(np.diag(rho))
    return float(diag @ SYS_BITS.sum(axis=1))
def sys_part_energies(rho):
    diag = np.real(np.diag(rho))
    vals = diag @ SYS_BITS
    return {SYS_NAMES[i]: float(vals[i]) for i in range(N_SYS)}

def single_energy(r2): return float(np.real(r2[1,1]))
def free_energy_beta1(r2): return single_energy(r2) - entropy_vn(r2, base2=False)

def pair_zz(rho,i,j):
    diag = np.real(np.diag(rho))
    z = (1 - 2*SYS_BITS[:,i]) * (1 - 2*SYS_BITS[:,j])
    return float(diag @ z)

def reduced_pair(rho,i,j):
    keep = [i, j]
    rest = [q for q in range(N_SYS) if q not in keep]
    axes = keep + rest + [q + N_SYS for q in keep] + [q + N_SYS for q in rest]
    x = rho.reshape([2] * (2 * N_SYS)).transpose(axes).reshape(4, 8, 4, 8)
    return np.einsum("arbr->ab", x, optimize=True)

def pair_negativity(rho,i,j):
    red = reduced_pair(rho,i,j)
    pt = red.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
    vals = np.linalg.eigvalsh(herm(pt)).real
    return float(np.sum(np.abs(vals[vals < 0])))

def pair_mi(rho,i,j):
    red = reduced_pair(rho,i,j)
    R = red.reshape(2,2,2,2)
    ri = np.trace(R, axis1=1, axis2=3)
    rj = np.trace(R, axis1=0, axis2=2)
    return float(entropy_vn(ri) + entropy_vn(rj) - entropy_vn(red))

def exchange2(theta):
    U = np.eye(4, dtype=np.complex128)
    c, s = math.cos(theta), math.sin(theta)
    U[1,1] = c; U[2,2] = c
    U[1,2] = -1j*s; U[2,1] = -1j*s
    return U

def embed_two(U2,n,q1,q2):
    key = ("two",n,q1,q2,round(float(np.real(U2[1,1])),14),round(float(np.imag(U2[1,2])),14))
    if key in EMBED_CACHE: return EMBED_CACHE[key]
    dim = 2 ** n
    U = np.zeros((dim,dim), dtype=np.complex128)
    for x in range(dim):
        bx = [(x >> (n-1-k)) & 1 for k in range(n)]
        idx = (bx[q1] << 1) | bx[q2]
        for out in range(4):
            amp = U2[out,idx]
            if abs(amp) == 0: continue
            b = bx.copy()
            b[q1] = (out >> 1) & 1
            b[q2] = out & 1
            y = 0
            for bit in b: y = (y << 1) | bit
            U[y,x] += amp
    EMBED_CACHE[key] = U
    return U

def embed_single(K,n,q):
    key = ("single",n,q,tuple(np.round(K.flatten(),14)))
    if key in EMBED_CACHE: return EMBED_CACHE[key]
    dim = 2 ** n
    M = np.zeros((dim,dim), dtype=np.complex128)
    for x in range(dim):
        bx = [(x >> (n-1-k)) & 1 for k in range(n)]
        ib = bx[q]
        for ob in (0,1):
            amp = K[ob,ib]
            if abs(amp) == 0: continue
            b = bx.copy(); b[q] = ob
            y = 0
            for bit in b: y = (y << 1) | bit
            M[y,x] += amp
    EMBED_CACHE[key] = M
    return M

def apply_U(rho,U): return U @ rho @ U.conj().T

def apply_two_local(rho, U2, n, q1, q2):
    """Apply a two-qubit unitary without materializing a dense 2^n gate."""
    keep = [q1, q2]
    rest = [q for q in range(n) if q not in keep]
    axes = keep + rest + [q + n for q in keep] + [q + n for q in rest]
    inverse = np.argsort(axes)
    drest = 2 ** (n - 2)
    x = rho.reshape([2] * (2 * n)).transpose(axes).reshape(4, drest, 4, drest)
    y = np.einsum("ai,irjs,bj->arbs", U2, x, U2.conj(), optimize=True)
    return y.reshape([2] * (2 * n)).transpose(inverse).reshape(2**n, 2**n)

def r_state(name):
    if name in ("R0_none","R2_pure_0"):
        return np.array([[1,0],[0,0]], dtype=np.complex128)
    if name == "R1_max_mixed":
        return np.eye(2, dtype=np.complex128)/2
    if name == "R3_pure_1":
        return np.array([[0,0],[0,1]], dtype=np.complex128)
    if name == "R4_plus":
        v = np.array([1,1], dtype=np.complex128)/math.sqrt(2)
        return np.outer(v,v.conj())
    if name.startswith("R5_gibbs_beta_"):
        beta = float(name.split("_")[-1].replace("m","."))
        z = 1 + math.exp(-beta)
        return np.diag([1/z, math.exp(-beta)/z]).astype(np.complex128)
    raise ValueError(name)

def resource_for_cycle(name,cycle,schedule):
    if name == "R0_none" or schedule == "always_off":
        return False, r_state("R2_pure_0"), 0
    if schedule == "constant_on":
        return True, r_state(name), 1
    if 0 <= cycle <= 49: return True, r_state(name), 1
    if 50 <= cycle <= 74: return False, r_state("R2_pure_0"), 0
    if 75 <= cycle <= 124: return True, r_state(name), 1
    if 125 <= cycle <= 149: return True, r_state(name), 2
    if 150 <= cycle <= 174: return (cycle % 2 == 0), r_state(name), 1 if cycle % 2 == 0 else 0
    if 175 <= cycle <= 199: return (cycle % 5 == 0), r_state(name), 2 if cycle % 5 == 0 else 0
    return False, r_state("R2_pure_0"), 0

def full_state(rsys, rR, rW): return np.kron(np.kron(rR, rsys), rW)

def trace_full_to_sys(rfull):
    X = rfull.reshape(2,DIM_SYS,2, 2,DIM_SYS,2)
    out = np.zeros((DIM_SYS,DIM_SYS), dtype=np.complex128)
    for r in range(2):
        for w in range(2):
            out += X[r,:,w, r,:,w]
    return out

def trace_full_single(rfull, target):
    # Axes are (R, SYS, W, R', SYS', W').  Contract the traced bra/ket
    # axes directly in NumPy instead of scanning all 128^2 matrix entries
    # in Python on every cycle.
    x = rfull.reshape(2, DIM_SYS, 2, 2, DIM_SYS, 2)
    if target == "R":
        return np.einsum("abcdbc->ad", x, optimize=True)
    if target == "W":
        return np.einsum("abcabd->cd", x, optimize=True)
    raise ValueError(target)

def dephase_sys(rho,p):
    if p <= 0: return rho
    return rho * ((1-p) ** HAMMING_SYS)

def amp_damp_sys(rho,p):
    if p <= 0: return rho
    K0 = np.array([[1,0],[0,math.sqrt(1-p)]], dtype=np.complex128)
    K1 = np.array([[0,math.sqrt(p)],[0,0]], dtype=np.complex128)
    out = rho
    for q in range(N_SYS):
        A0 = embed_single(K0,N_SYS,q); A1 = embed_single(K1,N_SYS,q)
        out = A0 @ out @ A0.conj().T + A1 @ out @ A1.conj().T
    return out

def apply_noise(rho,noise,p,strong_dephase=False):
    eb = sys_energy(rho)
    out = rho
    if noise == "N0_none": pass
    elif noise == "N1_dephase": out = dephase_sys(out,p)
    elif noise == "N3_amplitude_damping": out = amp_damp_sys(out,p)
    elif noise == "N4_dephase_plus_amplitude_damping":
        out = dephase_sys(out,p); out = amp_damp_sys(out,p)
    else: raise ValueError(noise)
    if strong_dephase: out = dephase_sys(out,1.0)
    return out, eb - sys_energy(out)

def apply_fault(rho,fault):
    if fault in ("none","cut_BC","weaken_AB","close_DW"):
        return rho, 0.0
    eb = sys_energy(rho)
    if fault == "remove_A_excitation":
        q = 1; K0 = np.array([[1,0],[0,0]], dtype=np.complex128); K1 = np.array([[0,1],[0,0]], dtype=np.complex128)
    elif fault == "empty_E":
        q = 0; K0 = np.array([[1,0],[0,0]], dtype=np.complex128); K1 = np.array([[0,1],[0,0]], dtype=np.complex128)
    elif fault == "overexcite_C":
        q = 3; K0 = np.array([[0,0],[0,1]], dtype=np.complex128); K1 = np.array([[0,0],[1,0]], dtype=np.complex128)
    else:
        raise ValueError(fault)
    A0 = embed_single(K0,N_SYS,q); A1 = embed_single(K1,N_SYS,q)
    out = A0 @ rho @ A0.conj().T + A1 @ rho @ A1.conj().T
    return out, sys_energy(out) - eb

@dataclass
class Condition:
    condition_id: str
    variant: str
    resource: str
    noise: str = "N4_dephase_plus_amplitude_damping"
    p: float = 0.06
    g: float = 0.10
    theta: float = 0.20
    fault: str = "none"
    schedule: str = "staged"
    note: str = ""

def conditions(profile="final"):
    out = []
    def add(variant, resource, noise="N4_dephase_plus_amplitude_damping", p=0.06, g=0.10, theta=0.20, fault="none", schedule="staged", note=""):
        out.append(Condition(f"QLLEM7_{len(out)+1:04d}", variant, resource, noise, p, g, theta, fault, schedule, note))
    if profile == "smoke":
        add("ring","R3_pure_1"); add("chain","R3_pure_1"); add("ring","R1_max_mixed"); return out
    for res in ["R3_pure_1","R1_max_mixed","R5_gibbs_beta_0m5","R5_gibbs_beta_1","R5_gibbs_beta_2","R4_plus"]:
        add("ring",res); add("chain",res)
    for var in ["middle_cut","weak_AB","strong_AB","shuffled","coupling_off","converter_off","output_off","strong_dephase","classical_probability_transport","central_control"]:
        add(var,"R3_pure_1")
    for fault in ["remove_A_excitation","overexcite_C","cut_BC","weaken_AB","close_DW","empty_E"]:
        add("ring","R3_pure_1",fault=fault,note="fault_at_cycle_100")
    for g in [0.05,0.20]: add("ring","R3_pure_1",g=g,note="g_sweep")
    for p in [0.01,0.03,0.10,0.18]: add("ring","R3_pure_1",p=p,note="p_sweep")
    for noise in ["N0_none","N1_dephase","N3_amplitude_damping"]:
        add("ring","R3_pure_1",noise=noise,p=0.06,note="noise_type_control")
    return out

def links(cond,cycle):
    g = cond.g
    L = [(0,1,g,"EA"),(1,2,g,"AB"),(2,3,g,"BC"),(3,4,g,"CD")]
    if cond.variant == "ring": L.append((1,4,g,"AD"))
    elif cond.variant == "middle_cut": L = [x for x in L if x[3] != "BC"]
    elif cond.variant == "weak_AB": L = [(a,b,g*0.25 if n=="AB" else w,n) for a,b,w,n in L] + [(1,4,g,"AD")]
    elif cond.variant == "strong_AB": L = [(a,b,g*2 if n=="AB" else w,n) for a,b,w,n in L] + [(1,4,g,"AD")]
    elif cond.variant == "shuffled": L = [(0,3,g,"EC"),(3,1,g,"CA"),(1,4,g,"AD"),(4,2,g,"DB")]
    elif cond.variant == "coupling_off": L = []
    elif cond.variant in ("converter_off","output_off","strong_dephase","classical_probability_transport","central_control"): L.append((1,4,g,"AD"))
    if cycle >= 100:
        if cond.fault == "cut_BC": L = [x for x in L if x[3] != "BC"]
        if cond.fault == "weaken_AB": L = [(a,b,g*0.10 if n=="AB" else w,n) for a,b,w,n in L]
    return L

def classical_transport(rho,cond,cycle):
    diag = np.real(np.diag(rho)).copy()
    alpha = min(0.49, 4*cond.g*cond.g)
    for a,b,w,n in links(cond,cycle):
        new = diag.copy()
        for s in range(DIM_SYS):
            bits = [(s >> (N_SYS-1-k)) & 1 for k in range(N_SYS)]
            if bits[a] != bits[b]:
                tbits = bits.copy(); tbits[a], tbits[b] = tbits[b], tbits[a]
                t = 0
                for bit in tbits: t = (t << 1) | bit
                f = alpha * (diag[s] - diag[t])
                new[s] -= f; new[t] += f
        diag = np.maximum(new,0); diag /= max(np.sum(diag), 1e-300)
    out = np.zeros_like(rho); np.fill_diagonal(out,diag); return out

def apply_internal(rho,cond,cycle):
    flow = {}
    if cond.variant == "classical_probability_transport":
        return classical_transport(rho,cond,cycle), flow
    cur = rho
    for a,b,angle,name in links(cond,cycle):
        before = sys_part_energies(cur)
        cur = apply_two_local(cur, exchange2(angle), N_SYS, a, b)
        after = sys_part_energies(cur)
        flow[f"flow_{name}"] = flow.get(f"flow_{name}",0.0) + after[SYS_NAMES[b]] - before[SYS_NAMES[b]]
    if cond.variant == "central_control":
        before = sys_part_energies(cur)
        cur = apply_two_local(cur, exchange2(cond.g*2.0), N_SYS, 0, 4)
        after = sys_part_energies(cur)
        flow["flow_ED_direct_upper_bound"] = after["D"] - before["D"]
    return cur, flow

def random_product(seed):
    rng = np.random.default_rng(seed)
    psi = np.array([1+0j])
    for _ in range(N_SYS):
        th = rng.uniform(0,np.pi); ph = rng.uniform(0,2*np.pi)
        v = np.array([math.cos(th/2), np.exp(1j*ph)*math.sin(th/2)], dtype=np.complex128)
        psi = np.kron(psi,v)
    return np.outer(psi,psi.conj())

def metrics(rho,cond,seed,cycle,prev):
    row = dict(condition_id=cond.condition_id,variant=cond.variant,resource=cond.resource,noise=cond.noise,p=cond.p,g=cond.g,theta=cond.theta,fault=cond.fault,seed=seed,cycle=cycle)
    row.update(E_internal=sys_energy(rho), purity=purity(rho), entropy=entropy_vn(rho), l1_coherence=l1_coherence(rho), trace_distance_to_maxmixed=trace_distance(rho,MAXMIX_SYS), prev_cycle_trace_distance=trace_distance(rho,prev) if prev is not None else "")
    for k,v in sys_part_energies(rho).items(): row[f"E_{k}"] = v
    diag = np.real(np.diag(rho))
    for i,v in enumerate(diag): row[f"pop_{i:05b}"] = float(v)
    for i,j,name in PAIR_SYS:
        row[f"ZZ_{name}"] = pair_zz(rho,i,j)
        row[f"MI_{name}"] = pair_mi(rho,i,j)
        row[f"negativity_{name}"] = pair_negativity(rho,i,j)
    return row

def run_one(task):
    cond, seed, save_states = task
    rho = random_product(seed)
    mets, ledg, flows, states = [], [], [], {}
    mets.append(metrics(rho,cond,seed,0,None))
    if save_states: states[f"{cond.condition_id}_seed{seed}_cycle000"] = rho.astype(np.complex64)
    for cycle in range(200):
        prev = rho.copy()
        estart = sys_energy(rho)
        wext = 0.0
        if cycle == 100:
            rho, wf = apply_fault(rho,cond.fault); wext += wf
        interact, rs, mult = resource_for_cycle(cond.resource,cycle,cond.schedule)
        if cond.variant == "converter_off": interact = False
        rin = rout = fcons = sent = 0.0
        if interact:
            for _ in range(mult):
                rin += single_energy(rs); fin = free_energy_beta1(rs)
                full = full_state(rho,rs,r_state("R2_pure_0"))
                full = apply_two_local(full, exchange2(cond.theta), N_FULL, 0, 1)
                rred = trace_full_single(full,"R")
                rho = trace_full_to_sys(full)
                rout += single_energy(rred)
                fcons += fin - free_energy_beta1(rred)
                sent += entropy_vn(rred)
        rho, linkflow = apply_internal(rho,cond,cycle)
        wout = 0.0
        open_output = cond.variant != "output_off"
        if cond.fault == "close_DW" and 100 <= cycle < 120: open_output = False
        if open_output:
            full = full_state(rho,r_state("R2_pure_0"),r_state("R2_pure_0"))
            full = apply_two_local(full, exchange2(cond.theta), N_FULL, 5, 6)
            wred = trace_full_single(full,"W")
            wout = single_energy(wred)
            rho = trace_full_to_sys(full)
        rho, qnoise = apply_noise(rho,cond.noise,cond.p,strong_dephase=(cond.variant in ("strong_dephase","classical_probability_transport")))
        dE = sys_energy(rho) - estart
        resid = rin + wext - (dE + rout + wout + qnoise)
        ledg.append(dict(condition_id=cond.condition_id,variant=cond.variant,resource=cond.resource,noise=cond.noise,p=cond.p,g=cond.g,theta=cond.theta,fault=cond.fault,seed=seed,cycle=cycle+1,E_R_in=rin,E_R_out=rout,Delta_E_Qcell=dE,E_W_out=wout,Q_noise=qnoise,W_external=wext,energy_balance_residual=resid,resource_free_energy_consumed=fcons,entropy_exported_to_R=sent,E_internal_start=estart,E_internal_end=sys_energy(rho)))
        fr = dict(condition_id=cond.condition_id,variant=cond.variant,resource=cond.resource,noise=cond.noise,p=cond.p,g=cond.g,theta=cond.theta,fault=cond.fault,seed=seed,cycle=cycle+1,R_in_energy=rin,R_spent_energy=rout,W_out_energy=wout)
        fr.update(linkflow); flows.append(fr)
        mets.append(metrics(rho,cond,seed,cycle+1,prev))
        if save_states and (cycle+1) in CHECKPOINTS:
            states[f"{cond.condition_id}_seed{seed}_cycle{cycle+1:03d}"] = rho.astype(np.complex64)
        vals = np.linalg.eigvalsh(herm(rho)).real
        if abs(np.trace(rho).real - 1) > 1e-7 or vals.min() < -1e-7:
            raise RuntimeError(f"invalid density {cond.condition_id} {seed} cycle {cycle+1}")
    return mets, ledg, flows, states

def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8"); return
    keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="qcell_local_linked_energy_machine_full2q7_final_v0_outputs")
    ap.add_argument("--profile", choices=["smoke","final"], default="final")
    ap.add_argument("--n-seeds", type=int, default=100)
    ap.add_argument("--max-conditions", type=int, default=0)
    ap.add_argument("--processes", type=int, default=min(6, os.cpu_count() or 1))
    ap.add_argument("--progress-every", type=int, default=10)
    args = ap.parse_args()
    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    conds = conditions(args.profile)
    if args.max_conditions: conds = conds[:args.max_conditions]
    seeds = MAIN_SEEDS[:args.n_seeds]
    save_ids = {c.condition_id for c in conds if c.resource in ("R3_pure_1","R4_plus","R1_max_mixed") and c.variant in ("ring","chain","middle_cut","coupling_off","converter_off")}
    tasks = [(c,s,c.condition_id in save_ids) for c in conds for s in seeds]
    t0 = time.time()
    allm=[]; alll=[]; allf=[]; states={}
    if args.processes <= 1:
        iterator = map(run_one,tasks)
    else:
        pool = mp.Pool(args.processes)
        iterator = pool.imap_unordered(run_one,tasks, chunksize=1)
    for n,res in enumerate(iterator,1):
        m,l,f,st = res
        allm.extend(m); alll.extend(l); allf.extend(f); states.update(st)
        if n % args.progress_every == 0:
            print(f"completed {n}/{len(tasks)} elapsed={time.time()-t0:.1f}s", flush=True)
    if args.processes > 1:
        pool.close(); pool.join()
    write_csv(out/"qcell_local_linked_energy_machine_full2q7_final_v0_cyclewise_state_metrics.csv", allm)
    write_csv(out/"qcell_local_linked_energy_machine_full2q7_final_v0_thermodynamic_ledger.csv", alll)
    write_csv(out/"qcell_local_linked_energy_machine_full2q7_final_v0_linkwise_energy_flow.csv", allf)
    if states:
        np.savez_compressed(out/"qcell_local_linked_energy_machine_full2q7_final_v0_checkpoint_density_matrices.npz", **states)
    with gzip.open(out/"qcell_local_linked_energy_machine_full2q7_final_v0_all_conditions.jsonl.gz","wt",encoding="utf-8") as f:
        for c in conds: f.write(json.dumps(asdict(c),ensure_ascii=False)+"\n")
    manifest = dict(experiment="qcell_local_linked_energy_machine_full2q7_final_v0",status="OBSERVATION_LOG",hilbert_space="full 7-qubit during cycle: R,E,A,B,C,D,W",qcell_body="E,A,B,C,D",n_conditions=len(conds),n_seeds=len(seeds),cycles=200,metric_rows=len(allm),ledger_rows=len(alll),flow_rows=len(allf),checkpoint_density_arrays=len(states),profile=args.profile,processes=args.processes,wall_seconds=time.time()-t0,resource_note="R3 |1> is battery-energy main; R4 |+> is coherence-injecting comparison")
    (out/"qcell_local_linked_energy_machine_full2q7_final_v0_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"regenerate_command.txt").write_text("python qcell_local_linked_energy_machine_full2q7_final_v0.py --profile final --n-seeds 100 --processes 6 --outdir qcell_local_linked_energy_machine_full2q7_final_v0_outputs\n",encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__ == "__main__":
    main()
