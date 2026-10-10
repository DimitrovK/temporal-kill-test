"""Changed versions of the Order workflow, for replay tests."""
import asyncio
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from wf import step

def opts(t):
    return dict(start_to_close_timeout=timedelta(seconds=t), retry_policy=RetryPolicy(initial_interval=timedelta(seconds=1), maximum_attempts=0))

@activity.defn
async def validate(order: str) -> str: return "ok"

@workflow.defn(name="Order")
class Original:
    @workflow.run
    async def run(self, order: str, timeout_s: float = 10.0, heartbeat_s: float = 0.0):
        return [await workflow.execute_activity(step, args=[order, n], **opts(timeout_s)) for n in range(1, 11)]

@workflow.defn(name="Order")
class InsertedStep:
    @workflow.run
    async def run(self, order: str, timeout_s: float = 10.0, heartbeat_s: float = 0.0):
        await workflow.execute_activity(validate, args=[order], **opts(timeout_s))
        return [await workflow.execute_activity(step, args=[order, n], **opts(timeout_s)) for n in range(1, 11)]

@workflow.defn(name="Order")
class ReversedOrder:
    @workflow.run
    async def run(self, order: str, timeout_s: float = 10.0, heartbeat_s: float = 0.0):
        return [await workflow.execute_activity(step, args=[order, n], **opts(timeout_s)) for n in range(10, 0, -1)]

@workflow.defn(name="Order")
class ChangedArguments:
    @workflow.run
    async def run(self, order: str, timeout_s: float = 10.0, heartbeat_s: float = 0.0):
        return [await workflow.execute_activity(step, args=["SOMEONE-ELSE", n * 100], **opts(timeout_s)) for n in range(1, 11)]

@workflow.defn(name="Order")
class OneStepFewer:
    @workflow.run
    async def run(self, order: str, timeout_s: float = 10.0, heartbeat_s: float = 0.0):
        return [await workflow.execute_activity(step, args=[order, n], **opts(timeout_s)) for n in range(1, 10)]

@workflow.defn(name="Order")
class ChangedTimeout:
    @workflow.run
    async def run(self, order: str, timeout_s: float = 10.0, heartbeat_s: float = 0.0):
        return [await workflow.execute_activity(step, args=[order, n], **opts(999)) for n in range(1, 11)]

