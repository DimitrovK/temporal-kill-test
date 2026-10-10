"""Replay chaos-1's real history against changed versions of the workflow."""
import asyncio
from temporalio.client import Client
from temporalio.worker import Replayer
from temporalio.client import WorkflowHistory
import os
from variants import Original, InsertedStep, ReversedOrder, ChangedArguments, OneStepFewer, ChangedTimeout

async def main():
    if os.path.exists("data/chaos-1-history.json"):
        # replay the recorded history from disk: no Temporal server needed
        hist = WorkflowHistory.from_json("chaos-1", open("data/chaos-1-history.json").read())
    else:
        c = await Client.connect("127.0.0.1:7233")
        hist = await c.get_workflow_handle("chaos-1").fetch_history()
    print(f"history: {len(hist.events)} events\n")
    for cls, what in [(Original,"unchanged code"),(InsertedStep,"new activity inserted before step 1"),
                      (ReversedOrder,"same 10 steps, reverse order"),(ChangedArguments,"different arguments to every step"),
                      (OneStepFewer,"loop runs 9 steps instead of 10"),(ChangedTimeout,"timeout 10 s changed to 999 s")]:
        try:
            r = await Replayer(workflows=[cls]).replay_workflow(hist, raise_on_replay_failure=True)
            print(f"  ACCEPTED  {what}")
        except Exception as e:
            msg = str(e).replace("\n"," ")
            print(f"  REJECTED  {what}\n            {type(e).__name__}: {msg[:230]}")
if __name__ == "__main__":
    asyncio.run(main())
