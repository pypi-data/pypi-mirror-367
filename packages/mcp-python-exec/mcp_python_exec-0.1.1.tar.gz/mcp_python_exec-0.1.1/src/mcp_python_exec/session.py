import uuid

from mcp.shared.context import RequestContext
from starlette.requests import Request


_STDIO_SESSION_ID = None


# https://github.com/modelcontextprotocol/python-sdk/issues/986#issuecomment-2991865237
def get_session_id(ctx: RequestContext) -> str:
    global _STDIO_SESSION_ID

    if isinstance(ctx.request, Request):
        return (
            # sse
            ctx.request.query_params.get("session_id")
            # streamable http
            or ctx.request.headers.get("mcp-session-id")
        )
    else:
        # stdio
        if _STDIO_SESSION_ID is None:
            _STDIO_SESSION_ID = str(uuid.uuid4())
        return _STDIO_SESSION_ID
