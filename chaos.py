"""Start a workflow, then repeatedly SIGKILL the worker at random moments and restart it."""
import subprocess, time, random, os, sys, signal, json
WID, KILLS, TIMEOUT, SEED = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
HB = sys.argv[5] if len(sys.argv) > 5 else "0"
random.seed(SEED)
env = dict(os.environ, STEP_SECONDS="3")
def spawn():
    return subprocess.Popen([".venv/bin/python", "wf.py", "worker"], env=env,
                            stdout=open(f"worker_{WID}.log", "a"), stderr=subprocess.STDOUT)
def status():
    r = subprocess.run(["temporal", "workflow", "describe", "--workflow-id", WID, "-o", "json"],
                       capture_output=True, text=True)
    try: return json.loads(r.stdout)["workflowExecutionInfo"]["status"]
    except Exception: return "?"
events = []
w = spawn(); time.sleep(2.5)
t0 = time.time()
subprocess.run([".venv/bin/python", "wf.py", "start", WID, TIMEOUT, HB], check=True)
events.append(dict(t=time.time(), what="workflow started"))
for k in range(KILLS):
    time.sleep(random.uniform(2.0, 6.0))
    if "COMPLETED" in status(): break
    w.send_signal(signal.SIGKILL); w.wait()
    events.append(dict(t=time.time(), what=f"SIGKILL worker {w.pid}"))
    w = spawn()
    events.append(dict(t=time.time(), what=f"new worker {w.pid}"))
while "COMPLETED" not in status():
    time.sleep(0.5)
events.append(dict(t=time.time(), what="workflow COMPLETED"))
w.send_signal(signal.SIGKILL); w.wait()
json.dump(dict(t0=t0, events=events), open(f"chaos_{WID}.json", "w"), indent=1)
print(f"{WID}: {sum(1 for e in events if 'SIGKILL' in e['what'])} kills, "
      f"completed in {events[-1]['t']-t0:.1f}s")
