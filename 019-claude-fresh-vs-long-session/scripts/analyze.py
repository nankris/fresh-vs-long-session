"""Per-turn cost: in a resumed session Claude Code's total_cost_usd is CUMULATIVE for the session,
while `usage` is per turn. So per-turn est. $ = difference of consecutive cumulative costs (long arm)."""
import csv, os, json
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(f"{D}/results/runs.csv")))
out=[]
for cond in ("long","fresh"):
    for rep in sorted({r["rep"] for r in rows if r["cond"]==cond}):
        rs=sorted([r for r in rows if r["cond"]==cond and r["rep"]==rep], key=lambda r:int(r["start_epoch"]))
        prev=0.0; cum=0.0
        for i,r in enumerate(rs,1):
            c=float(r["est_cost_usd"])
            turn = c-prev if cond=="long" else c
            prev = c if cond=="long" else 0.0
            cum += turn
            out.append(dict(cond=cond,rep=rep,turn=i,task=r["task"],passed=r["passed"],input_tokens=r["input_tokens"],cache_creation=r["cache_creation_tokens"],
                cache_read=r["cache_read_tokens"],output_tokens=r["output_tokens"],total_tokens=r["total_tokens"],first_call_prompt=int(r["first_call_input"] or 0)+int(r["first_call_cache_creation"] or 0)+int(r["first_call_cache_read"] or 0),
                turn_cost=round(turn,5),cum_cost=round(cum,5),num_turns=r["num_turns"],tool_calls=r["tool_calls"],wall_s=r["wall_s"]))
w=csv.DictWriter(open(f"{D}/results/per_turn.csv","w"),fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
summ=[]
for cond in ("long","fresh"):
    for rep in sorted({o["rep"] for o in out if o["cond"]==cond}):
        rs=[o for o in out if o["cond"]==cond and o["rep"]==rep]
        summ.append(dict(cond=cond,rep=rep,tasks=len(rs),passed=sum(o["passed"]=="True" for o in rs),total_tokens=sum(int(o["total_tokens"]) for o in rs),
             output_tokens=sum(int(o["output_tokens"]) for o in rs),cache_creation=sum(int(o["cache_creation"]) for o in rs),cache_read=sum(int(o["cache_read"]) for o in rs),
             est_cost=round(sum(o["turn_cost"] for o in rs),4),last_turn_prompt=rs[-1]["first_call_prompt"],wall_s=round(sum(float(o["wall_s"]) for o in rs),1)))
w=csv.DictWriter(open(f"{D}/results/summary.csv","w"),fieldnames=list(summ[0])); w.writeheader(); w.writerows(summ)
for s in summ: print(s)
fig,ax=plt.subplots(1,2,figsize=(13,4.6))
for cond,col in (("long","#d17b4a"),("fresh","#4a7bd1")):
    for rep in sorted({o["rep"] for o in out if o["cond"]==cond}):
        rs=[o for o in out if o["cond"]==cond and o["rep"]==rep]
        ax[0].plot([o["turn"] for o in rs],[o["first_call_prompt"] for o in rs],"o-",color=col,label=f"{cond} r{rep}")
        ax[1].plot([o["turn"] for o in rs],[o["cum_cost"] for o in rs],"o-",color=col,label=f"{cond} r{rep}")
ax[0].set_title("Prompt size at the start of each task (tokens)"); ax[0].set_xlabel("task # in sequence"); ax[0].legend(fontsize=8)
ax[1].set_title("Cumulative API-equivalent est. $"); ax[1].set_xlabel("task # in sequence"); ax[1].legend(fontsize=8)
plt.suptitle("#019 Claude Code: 10 tasks in one resumed session vs a fresh session per task",fontsize=11)
plt.tight_layout(); plt.savefig(f"{D}/results/chart.png",dpi=110)
