import logging
from typing import Callable, cast, Type, Awaitable

from fastapi import HTTPException, Request, APIRouter
from langgraph.graph.graph import CompiledGraph

from veri_agents_api.fastapi.thread import (
    create_thread_router as create_thread_router, InvokeInput
)
from veri_agents_api.threads_util import ThreadsCheckpointerUtil, ThreadInfo
from veri_agents_api.util.awaitable import MaybeAwaitable, as_awaitable

log = logging.getLogger(__name__)


def create_threads_router(
    get_graph: Callable[[Request], MaybeAwaitable[CompiledGraph]],
    allow_access_thread: Callable[[str, ThreadInfo | None, Request], MaybeAwaitable[bool]] = lambda thread_id, thread_info, request: True,
    allow_invoke_thread: Callable[[str, ThreadInfo | None, InvokeInput, Request], MaybeAwaitable[bool]] = lambda thread_id, thread_info, invoke_input, request: True,
    on_invoke_thread: Callable[[str, ThreadInfo | None, InvokeInput, Request], MaybeAwaitable[None]] = lambda thread_id, thread_info, invoke_input, request: None,
    # InvokeInputCls: Type[InvokeInput] = InvokeInput,
    **router_kwargs
):
    router = APIRouter(prefix="/threads", **router_kwargs)

    thread_router = create_thread_router(
        # derive thread id from /thread/{thread_id} path param
        get_thread_id=lambda req: req.path_params["thread_id"],

        # arg passthrough - TODO: make more elegant
        get_graph=get_graph,
        allow_access_thread=allow_access_thread,
        allow_invoke_thread=allow_invoke_thread,
        on_invoke_thread=on_invoke_thread,

        # InvokeInputCls=InvokeInputCls
    )

    @router.get("/")
    async def get_threads(request: Request):
        """Get all threads the user has access to."""

        graph = await as_awaitable(get_graph(request))

        all_thread_info = await ThreadsCheckpointerUtil.list_threads(graph.checkpointer)

        accessible_thread_info: list[ThreadInfo] = []
        for thread_info in all_thread_info:
            if allow_access_thread(thread_info.thread_id, thread_info, request):
                accessible_thread_info.append(thread_info)

        return accessible_thread_info

    @router.get("/{thread_id}/info")
    async def get_thread_by_id(thread_id: str, request: Request):
        """Get a thread by its ID.

        Arguments:
            thread_id: The ID of the thread to get.
        """
        graph = await as_awaitable(get_graph(request))

        thread_info = await ThreadsCheckpointerUtil.get_thread_info(thread_id, graph.checkpointer)

        if not allow_access_thread(thread_id, thread_info, request):
            raise HTTPException(status_code=403, detail="Forbidden")

        try:
            return thread_info
        except:
            raise HTTPException(status_code=404, detail="Thread not found")

    router.include_router(thread_router, prefix="/{thread_id}")

    return router
