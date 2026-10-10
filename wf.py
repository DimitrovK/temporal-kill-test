import asyncio, os, sys, time, sqlite3
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.common import RetryPolicy

SIDEFX = os.path.abspath("sidefx.log")
STEP_SECONDS = float(os.environ.get("STEP_SECONDS", "3"))
IDEMPOTENT = os.environ.get("IDEMPOTENT") == "1"
CHARGES_DB = os.path.abspath("charges.db")

@activity.defn
async def step(order: str, n: int) -> str:
    info = activity.info()
    # the side effect happens FIRST, like charging a card before doing the slow bookkeeping
    applied = "n/a"
    if IDEMPOTENT:
        # the key is identical on every retry of this step, so the database refuses a second charge
        key = f"{info.workflow_id}:{info.activity_id}"
        con = sqlite3.connect(CHARGES_DB)
        con.execute("create table if not exists charges(key text primary key, ts real)")
        applied = "applied" if con.execute("insert or ignore into charges values (?, ?)", (key, time.time())).rowcount == 1 else "skipped"
        con.commit(); con.close()
    with open(SIDEFX, "a") as f:
        f.write(f"{time.time():.3f} order={order} step={n} attempt={info.attempt} pid={os.getpid()} charge={applied}\n")
    # heartbeat while working, so the server can notice a dead worker quickly
    end = time.time() + STEP_SECONDS
    while time.time() < end:
        activity.heartbeat()
        await asyncio.sleep(0.5)
    return f"step {n} done"

@workflow.defn
class Order:
    @workflow.run
    async def run(self, order: str, timeout_s: float = 10.0, heartbeat_s: float = 0.0) -> list[str]:
        out = []
        for n in range(1, 11):
            out.append(await workflow.execute_activity(
                step, args=[order, n],
                start_to_close_timeout=timedelta(seconds=timeout_s),
                heartbeat_timeout=timedelta(seconds=heartbeat_s) if heartbeat_s else None,
                retry_policy=RetryPolicy(initial_interval=timedelta(seconds=1), maximum_attempts=0)))
        return out

async def run_worker():
    c = await Client.connect("127.0.0.1:7233")
    async with Worker(c, task_queue="orders", workflows=[Order], activities=[step]):
        print(f"worker {os.getpid()} up", flush=True)
        await asyncio.Event().wait()

async def start(wid: str, timeout_s: float = 10.0, heartbeat_s: float = 0.0):
    c = await Client.connect("127.0.0.1:7233")
    h = await c.start_workflow(Order.run, args=[wid, timeout_s, heartbeat_s], id=wid, task_queue="orders")
    print("started", h.id, flush=True)

async def wait(wid: str):
    c = await Client.connect("127.0.0.1:7233")
    print("RESULT", await c.get_workflow_handle(wid).result(), flush=True)

if __name__ == "__main__":
    asyncio.run({"worker": run_worker, "start": lambda: start(sys.argv[2], float(sys.argv[3]) if len(sys.argv)>3 else 10.0, float(sys.argv[4]) if len(sys.argv)>4 else 0.0), "wait": lambda: wait(sys.argv[2])}[sys.argv[1]]())
