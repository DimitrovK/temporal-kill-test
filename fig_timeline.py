import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
SURF="#1a1a19"; T1="#ffffff"; T2="#c3c2b7"; GRID="#2e2d2a"; FIRST="#3987e5"; RETRY="#d95926"
plt.rcParams.update({"figure.facecolor":SURF,"axes.facecolor":SURF,"text.color":T1,"axes.labelcolor":T2,
  "xtick.color":T2,"ytick.color":T2,"axes.edgecolor":GRID,"font.size":11,"font.family":"DejaVu Sans"})
d=json.load(open("data/chaos_chaos-1.json")); t0=d["t0"]
kills=[e["t"]-t0 for e in d["events"] if "SIGKILL" in e["what"]]
done=[e["t"]-t0 for e in d["events"] if "COMPLETED" in e["what"]][0]
fx=[]
for l in open("data/sidefx.log"):
    if "order=chaos-1 " not in l: continue
    p=l.split(); kv=dict(x.split("=",1) for x in p[1:] if "=" in x)
    fx.append((float(p[0])-t0,int(kv["step"]),int(kv["attempt"])))
fig,ax=plt.subplots(figsize=(13,6.4))
for k in kills: ax.axvline(k,color=T2,ls=":",lw=1.1,alpha=.75)
for t,s,a in fx:
    c=FIRST if a==1 else RETRY
    end=min([t+3]+[k for k in kills if k>t])          # work stops at the next kill, if any
    ax.plot([t,end],[s,s],color=c,lw=3,solid_capstyle="butt",alpha=.85)
    ax.plot(t,s,"o",color=c,ms=8,mec=SURF,mew=1.5,zorder=5)   # the moment the side effect happened
    if s==1: ax.text(t+0.6,s-0.42,f"attempt {a}",va="center",fontsize=9.5,color=T1)
s1=sorted(t for t,s,a in fx if s==1)
for (a,b),lab in zip(zip(s1,s1[1:]),["10 s timeout + 1 s","10 s timeout + 2 s","10 s timeout + 4 s"]):
    ax.annotate("",xy=(b,1.45),xytext=(a,1.45),arrowprops=dict(arrowstyle="<->",color=T2,lw=1))
    ax.text((a+b)/2,1.72,lab,ha="center",va="center",fontsize=9.2,color=T2)
ax.axvline(done,color=T1,lw=1.2); ax.text(done-0.6,1.0,"workflow\ncompleted",ha="right",fontsize=9.5,color=T1,va="center")
ax.set_ylim(10.8,0.2); ax.set_yticks(range(1,11)); ax.set_yticklabels([f"step {i}" for i in range(1,11)])
ax.set_xlim(-1,73); ax.set_xlabel("seconds after the workflow started")
ax.grid(axis="x",color=GRID,lw=.7); ax.set_axisbelow(True)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
h=[Line2D([0],[0],color=FIRST,lw=3,marker="o",ms=8,label="side effect, first attempt"),
   Line2D([0],[0],color=RETRY,lw=3,marker="o",ms=8,label="side effect, repeated by a retry"),
   Line2D([0],[0],color=T2,ls=":",lw=1.2,label="worker killed with SIGKILL")]
ax.legend(handles=h,loc="upper right",bbox_to_anchor=(0.86,0.98),frameon=False,labelcolor=T2,fontsize=10)
ax.set_title("8 kills, 1 completed workflow, and step 1's side effect happened 4 times",loc="left",fontsize=13.5,color=T1,pad=12)
fig.subplots_adjust(left=0.08,right=0.98,top=0.9,bottom=0.1)
fig.savefig("fig_timeline.png",dpi=130)
