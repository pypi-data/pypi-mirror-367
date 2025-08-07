import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Tuple, Callable
from uuid import uuid4

from fastapi import HTTPException, Request, APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.runnables import RunnableConfig
from langgraph.graph.graph import CompiledGraph

from .schema import (
    ChatMessage,
    StreamInput,
    InvokeInput,
)
from veri_agents_api.threads_util import ThreadInfo, ThreadsCheckpointerUtil
from veri_agents_api.util.awaitable import as_awaitable, MaybeAwaitable

log = logging.getLogger(__name__)

class TokenQueueStreamingHandler(AsyncCallbackHandler):
    """LangChain callback handler for streaming LLM tokens to an asyncio queue."""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        if token:
            await self.queue.put(token)

def create_thread_router(
    get_graph: Callable[[Request], MaybeAwaitable[CompiledGraph]],
    get_thread_id: Callable[[Request], MaybeAwaitable[str]],
    allow_access_thread: Callable[[str, ThreadInfo | None, Request], MaybeAwaitable[bool]] = lambda thread_id, thread_info, request: True,
    allow_invoke_thread: Callable[[str, ThreadInfo | None, InvokeInput, Request], MaybeAwaitable[bool]] = lambda thread_id, thread_info, invoke_input, request: True,
    invoke_runnable_config: Callable[[str, ThreadInfo | None, InvokeInput, Request], MaybeAwaitable[RunnableConfig | None]] = lambda thread_id, thread_info, invoke_input, request: None,
    on_invoke_thread: Callable[[str, ThreadInfo | None, InvokeInput, Request], MaybeAwaitable[None]] = lambda thread_id, thread_info, invoke_input, request: None,
    # InvokeInputCls: Type[InvokeInput] = InvokeInput,
    **router_kwargs
):
    """
    POST /invoke
    POST /stream
    GET /history
    GET /feedback
    POST /feedback
    """

    router = APIRouter(**router_kwargs)

    def _parse_input(user_input: InvokeInput, thread_id: str, invoke_recvd_runnable_config: RunnableConfig | None) -> Tuple[Dict[str, Any], str]:
        run_id = uuid4()
        input_message = ChatMessage(type="human", content=user_input.message)

        runnable_config = invoke_recvd_runnable_config or RunnableConfig()

        runnable_config["configurable"] = {
            **{
                # used by checkpointer
                "thread_id": thread_id,

                "_has_threadinfo": True,

                # "args": user_input.args,
            }, 
            **(runnable_config.get("configurable", {}))
        }

        kwargs = dict(
            input={"messages": [input_message.to_langchain()]},
            config=runnable_config
        )
        return kwargs, str(run_id)

    @router.post("/invoke")
    async def invoke(invoke_input: InvokeInput, request: Request) -> ChatMessage:
        """
        Invoke the agent with user input to retrieve a final response.

        Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
        is also attached to messages for recording feedback.
        """

        graph = await as_awaitable(get_graph(request))
        thread_id = await as_awaitable(get_thread_id(request))
        

        thread_info = await ThreadsCheckpointerUtil.get_thread_info(thread_id, graph.checkpointer)

        if not await as_awaitable(allow_invoke_thread(thread_id, thread_info, invoke_input, request)):
            raise HTTPException(status_code=403, detail="Forbidden")
        
        invoke_recvd_runnable_config = await as_awaitable(invoke_runnable_config(thread_id, thread_info, invoke_input, request))

        kwargs, run_id = _parse_input(invoke_input, thread_id, invoke_recvd_runnable_config)

        # # store this thread in the database if a new one
        # if user_input.thread_id not in router.state.threads:
        #     thread_info = ThreadInfo(
        #         thread_id=user_input.thread_id,
        #         user=principal,
        #         workflow_id=user_input.workflow,
        #         name=user_input.message[:50],
        #         metadata={"router": user_input.router},
        #     )
        #     router.state.threads[user_input.thread_id] = thread_info
        #     await graph.checkpointer.aput_thread(thread_info)

        await as_awaitable(on_invoke_thread(thread_id, thread_info, invoke_input, request))

        # langfuse_handler = CallbackHandler(
        #     public_key=router.state.cfg.logging.langfuse.public_key,
        #     secret_key=router.state.cfg.logging.langfuse.secret_key,
        #     host=router.state.cfg.logging.langfuse.host,
        #     # user_id=principal,
        #     session_id=user_input.thread_id,
        #     trace_name=user_input.message[:50],
        # )
        kwargs["config"]["callbacks"] = [] # was [langfuse_handler]
        # kwargs["config"]["configurable"]["workflow_id"] = user_input.workflow
        try:
            response = await graph.ainvoke(**kwargs)
            output = ChatMessage.from_langchain(response["messages"][-1])
            output.run_id = str(run_id)
            return output
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/stream")
    async def stream_agent(stream_input: StreamInput, request: Request):
        """
        Stream the agent's response to a user input, including intermediate messages and tokens.

        Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
        is also attached to all messages for recording feedback.
        """

        graph = await as_awaitable(get_graph(request))
        thread_id = await as_awaitable(get_thread_id(request))

        thread_info = await ThreadsCheckpointerUtil.get_thread_info(thread_id, graph.checkpointer)

        if not await as_awaitable(allow_invoke_thread(thread_id, thread_info, stream_input, request)):
            raise HTTPException(status_code=403, detail="Forbidden")
        
        invoke_recvd_runnable_config = await as_awaitable(invoke_runnable_config(thread_id, thread_info, stream_input, request))

        async def message_generator() -> AsyncGenerator[str, None]:
            """
            Generate a stream of messages from the agent.

            This is the workhorse method for the /stream endpoint.
            """
            kwargs, run_id = _parse_input(stream_input, thread_id, invoke_recvd_runnable_config)

            await as_awaitable(on_invoke_thread(thread_id, thread_info, stream_input, request))

            # # store this thread in the database if a new one
            # if user_input.thread_id not in router.state.threads:
            #     thread_info = ThreadInfo(
            #         thread_id=user_input.thread_id,
            #         user=principal,
            #         workflow_id=user_input.workflow,
            #         name=user_input.message[:50],
            #         metadata={"router": user_input.router},
            #     )
            #     router.state.threads[user_input.thread_id] = thread_info
            #     await graph.checkpointer.aput_thread(thread_info)

            # Use an asyncio queue to process both messages and tokens in
            # chronological order, so we can easily yield them to the client.
            output_queue = asyncio.Queue(maxsize=10)

            # langfuse_handler = CallbackHandler(
            #     public_key=router.state.cfg.logging.langfuse.public_key,
            #     secret_key=router.state.cfg.logging.langfuse.secret_key,
            #     host=router.state.cfg.logging.langfuse.host,
            #     user_id=principal,
            #     session_id=user_input.thread_id,
            #     trace_name=user_input.message[:50],
            # )
            if stream_input.stream_tokens:
                kwargs["config"]["callbacks"] = [
                    TokenQueueStreamingHandler(queue=output_queue),
                    # langfuse_handler,
                ]
            # kwargs["config"]["configurable"]["workflow_id"] = stream_input.workflow

            # Pass the agent's stream of messages to the queue in a separate task, so
            # we can yield the messages to the client in the main thread.
            async def run_agent_stream():
                async for s in graph.astream(**kwargs, stream_mode="updates"):
                    await output_queue.put(s)
                await output_queue.put(None)

            stream_task = asyncio.create_task(run_agent_stream())

            # Process the queue and yield messages over the SSE stream.
            while s := await output_queue.get():
                log.info("Got from queue: %s: %s", type(s), s)
                if isinstance(s, str):
                    # str is an LLM token
                    yield f"data: {json.dumps({'type': 'token', 'content': s})}\n\n"
                    continue

                # Otherwise, s should be a dict of state updates for each node in the graph.
                # s could have updates for multiple nodes, so check each for messages.
                new_messages = []
                for _, state in s.items():
                    new_messages.extend(state["messages"])
                for message in new_messages:
                    try:
                        chat_message = ChatMessage.from_langchain(message)
                        chat_message.run_id = str(run_id)
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'error', 'content': f'Error parsing message: {e}'})}\n\n"
                        continue
                    # LangGraph re-sends the input message, which feels weird, so drop it
                    if (
                        chat_message.type == "human"
                        and chat_message.content == stream_input.message
                    ):
                        continue
                    yield f"data: {json.dumps({'type': 'message', 'content': chat_message.dict()})}\n\n"

            await stream_task
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            message_generator(),
            media_type="text/event-stream",
        )

    @router.get("/history")
    async def get_history(request: Request) -> List[ChatMessage]:
        """
        Get the history of a thread.
        """

        graph = await as_awaitable(get_graph(request))
        thread_id = await as_awaitable(get_thread_id(request))

        thread_info = await ThreadsCheckpointerUtil.get_thread_info(thread_id, graph.checkpointer)

        if not await as_awaitable(allow_access_thread(thread_id, thread_info, request)):
            raise HTTPException(status_code=403, detail="Forbidden")

        # agent: CompiledGraph = router.state.workflows[workflow].get_graph()
        config = RunnableConfig(configurable={
            # used by checkpointer
            "thread_id": thread_id,
        })
        state = await graph.aget_state(config)
        messages = state.values.get("messages", [])

        converted_messages: List[ChatMessage] = []
        for message in messages:
            try:
                chat_message = ChatMessage.from_langchain(message)
                converted_messages.append(chat_message)
            except Exception as e:
                log.error(f"Error parsing message: {e}")
                continue
        return converted_messages

    # @router.get("/feedback")
    # async def get_feedback(request: Request, thread_id: str):
    #     """Get all feedback for a thread.
    #
    #     Arguments:
    #         thread_id: The ID of the thread to get feedback for.
    #     """
    #     # if thread_id not in router.state.threads:
    #     #     raise HTTPException(status_code=404, detail=f"Unknown thread: {thread_id}")
    #     # assert_viewer_can_assume_identity(
    #     #     request, principal=router.state.threads[thread_id].user
    #     # )
    #     feedback = [
    #         f.model_dump(mode="json")
    #         async for f in graph.checkpointer.alist_feedback(thread_id=thread_id)
    #     ]
    #     return feedback
    #
    # @router.post("/feedback")
    # async def feedback(feedback: Feedback, request: Request):
    #     """
    #     Record feedback for a run of the agent.
    #
    #     Arguments:
    #         feedback: The feedback to record.
    #     """
    #     if feedback.thread_id not in router.state.threads:
    #         raise HTTPException(
    #             status_code=404, detail=f"Unknown thread: {feedback.thread_id}"
    #         )
    #     assert_viewer_can_assume_identity(
    #         request, principal=router.state.threads[feedback.thread_id].user
    #     )
    #
    #     # store in database
    #     try:
    #         await graph.checkpointer.aput_feedback(feedback)
    #         db_status = "success"
    #     except Exception as e:
    #         log.error(f"Error storing feedback in database: {e}")
    #         db_status = "error"
    #
    #     ## Also store in Langfuse
    #     ## We don't have the run_id, but need it for Langfuse
    #     ## The run_id is currently not store in the database.
    #     # try:
    #     #     langfuse = Langfuse(
    #     #         public_key=router.state.cfg.logging.langfuse.public_key,
    #     #         secret_key=router.state.cfg.logging.langfuse.secret_key,
    #     #         host=router.state.cfg.logging.langfuse.host,
    #     #     )
    #     #     langfuse.score(
    #     #         trace_id=feedback.run_id,
    #     #         name=feedback.key,
    #     #         value=feedback.score,
    #     #         comment=feedback.kwargs.get("comment", ""),
    #     #     )
    #     #     langfuse_status = "success"
    #     # except Exception as e:
    #     #     log.error(f"Error storing feedback in Langfuse: {e}")
    #     #     langfuse_status = "error"
    #
    #     langfuse_status = "not implemented"
    #
    #     return {"db_status": db_status, "langfuse_status": langfuse_status}

    return router
