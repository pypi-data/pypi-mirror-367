from typing import Any, Callable, Union, Sequence
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.llm_service import FunctionCallParams


def append_message_history_to_function(
    handler: Callable[[FunctionCallParams], Any],
    ctx_or_list: Union[OpenAILLMContext, Sequence[dict]],
):
    """
    Return a wrapper that adds live history to every function call.

    • If `ctx_or_list` is an OpenAILLMContext, uses `ctx_or_list.messages`.
    • If it's a plain list, uses it directly.
    • Otherwise assumes no prior history.
    """

    async def _wrapper(params: FunctionCallParams):
        # figure out where our history is coming from
        if hasattr(ctx_or_list, "messages"):
            # ctx is an OpenAILLMContext
            raw = ctx_or_list.messages
        elif isinstance(ctx_or_list, Sequence):
            # ctx is already a list of message dicts
            raw = ctx_or_list
        else:
            raw = []

        # deep‐copy each message so handlers can mutate safely
        live_history = [m.copy() for m in raw]

        # replace params.arguments in-place if they asked for history
        params.arguments = dict(params.arguments)
        if "messages_history" in params.arguments:
            params.arguments["messages_history"] = live_history

        return await handler(params)

    return _wrapper