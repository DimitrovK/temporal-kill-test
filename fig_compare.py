import json, collections, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
SURF="#1a1a19"; T1="#ffffff"; T2="#c3c2b7"; GRID="#2e2d2a"; A="#3987e5"; B="#d95926"
plt.rcParams.update({"figure.facecolor":SURF,"axes.facecolor":SURF,"text.color":T1,"axes.labelcolor":T2,
  "xtick.color":T2,"ytick.color":T2,"axes.edgecolor":GRID,"font.size":11,"font.family":"DejaVu Sans"})
pairs=[("chaos-1","chaos-hb"),("to-s2","hb-s2"),("to-s3","hb-s3"),("to-s4","hb-s4")]
lines=open("data/sidefx.log").read().splitlines()
def dup(w):
    c=collections.Counter(dict(x.split("=",1) for x in l.split()[1:] if "=" in x)["step"] for l in lines if f"order={w} " in l)
    return sum(v-1 for v in c.values())
def dur(w):
    d=json.load(open(f"data/chaos_{w}.json")); return d["events"][-1]["t"]-d["t0"]
fig,axes=plt.subplots(1,2,figsize=(13,5.2))
x=range(len(pairs)); w=0.36
for ax,(fn,ylab,fmt) in zip(axes,[(dup,"duplicate side effects","{:.0f}"),(dur,"seconds to complete","{:.0f}")]):
    va=[fn(a) for a,b in pairs]; vb=[fn(b) for a,b in pairs]
    ax.bar([i-w/2-0.01 for i in x],va,w,color=A,label="activity timeout only (10 s)")
    ax.bar([i+w/2+0.01 for i in x],vb,w,color=B,label="heartbeat timeout (2 s)")
    for i,(p,q) in enumerate(zip(va,vb)):
        ax.text(i-w/2-0.01,p,fmt.format(p),ha="center",va="bottom",fontsize=10,color=T1)
        ax.text(i+w/2+0.01,q,fmt.format(q),ha="center",va="bottom",fontsize=10,color=T1)
    ax.set_xticks(list(x)); ax.set_xticklabels([f"kill schedule {i+1}" for i in x],fontsize=10)
    ax.set_ylabel(ylab); ax.grid(axis="y",color=GRID,lw=.7); ax.set_axisbelow(True)
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    ax.set_ylim(0,max(va+vb)*1.2)
axes[0].set_title("More duplicates in every run",loc="left",fontsize=12,color=T1,pad=8)
axes[1].set_title("And not faster overall",loc="left",fontsize=12,color=T1,pad=8)
axes[0].legend(frameon=False,labelcolor=T2,fontsize=10,loc="upper right")
fig.suptitle("Same 8 kills at the same moments, with and without heartbeating",x=0.06,ha="left",fontsize=14,y=0.99,color=T1)
fig.subplots_adjust(left=0.07,right=0.98,top=0.83,bottom=0.12,wspace=0.22)
fig.savefig("fig_compare.png",dpi=130)
