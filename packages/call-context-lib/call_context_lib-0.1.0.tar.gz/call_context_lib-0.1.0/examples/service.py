from libs.call_context_lib.core import CallContext
from .llm_module import call_llm_stream, call_llm, acall_llm_stream, acall_llm
from .experiment_logger import MQExperimentLogger

experiment_id = "search-llm-ab-1"

async def get_root_stream():
    ctx = CallContext(user_id="kim", turn_id="t001")
    ctx.meta["model"] = "gpt-4"
    ctx.meta["experiment_id"] = experiment_id
    ctx.callbacks.append(MQExperimentLogger("experiment-topic"))
    return ctx.astream(acall_llm_stream, "hello", "gpt-4")

async def get_v2_stream():
    ctx = CallContext(user_id="kim", turn_id="t001")
    ctx.meta["model"] = "gpt-4"
    ctx.meta["experiment_id"] = experiment_id
    ctx.callbacks.append(MQExperimentLogger("experiment-topic"))
    return ctx.astream(call_llm_stream, "hello", "gpt-4")

async def get_invoke_data():
    ctx = CallContext(user_id="kim", turn_id="t002")
    ctx.meta["model"] = "gpt-4"
    ctx.meta["experiment_id"] = experiment_id
    ctx.callbacks.append(MQExperimentLogger("experiment-topic"))

    result = await ctx.ainvoke(call_llm, "hello", "gpt-4")
    result2 = await ctx.ainvoke(acall_llm, "hello", "gpt-4")
    return {"result": result, "result2": result2}
