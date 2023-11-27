import asyncio
import sys
import threading
import inspect
from functools import wraps


def safe_serialize_arg(arg):
    # Serialize various types of arguments
    if isinstance(arg, (str, int, float, bool, type(None))):
        return arg
    elif isinstance(arg, (list, tuple, set, frozenset)):
        return [safe_serialize_arg(item) for item in arg]
    elif isinstance(arg, dict):
        return {k: safe_serialize_arg(v) for k, v in arg.items()}
    else:
        # For complex types, return a string indicating the type instead of deep serialization
        return f"<{type(arg).__name__}>"


def trace_calls(frame, event, arg):
    if event != "call":
        return
    co = frame.f_code
    func_name = co.co_name
    filename = co.co_filename
    line_no = frame.f_lineno
    arg_info = inspect.getargvalues(frame)
    arg_values = {key: frame.f_locals[key] for key in arg_info.args}
    serialized_args = {k: safe_serialize_arg(v) for k, v in arg_values.items()}
    print(f"Trace: {func_name} in {filename}:{line_no} args={serialized_args}")


def set_trace_for_all_threads():
    threading.settrace(trace_calls)
    sys.settrace(trace_calls)
    for thread in threading.enumerate():
        if thread is not threading.main_thread():
            sys.settrace(trace_calls)


def unset_trace_for_all_threads():
    threading.settrace(None)
    sys.settrace(None)


def wrap_coroutine_function(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        return result
    return wrapper


def trace_async_calls(loop):
    orig_create_task = loop.create_task

    @wraps(orig_create_task)
    def create_task_wrapper(coro, **kwargs):
        if asyncio.iscoroutine(coro) and hasattr(coro, 'cr_code') and 'autogen' in coro.cr_code.co_filename:
            coro = wrap_coroutine_function(coro)
        return orig_create_task(coro, **kwargs)

    loop.create_task = create_task_wrapper


async def sample_async_function(x, y):
    return x + y


async def main():
    set_trace_for_all_threads()
    loop = asyncio.get_event_loop()
    trace_async_calls(loop)

    DISCORD_BOT.run(BOT_TOKEN)

    unset_trace_for_all_threads()

if __name__ == "__main__":
    asyncio.run(main())
