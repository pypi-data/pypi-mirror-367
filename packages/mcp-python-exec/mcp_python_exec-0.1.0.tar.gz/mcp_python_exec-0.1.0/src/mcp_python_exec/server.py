import base64
import io

from mcp.server.fastmcp import FastMCP
import mcp.types as types
from PIL import Image

from .executor import ChrootExecutor
from .session import get_session_id


app = FastMCP(name="Python Execution Server", port=8011, host="0.0.0.0")


@app.tool(structured_output=False)
async def exec_python(python_code: str, requirements: list[str] | None = None) -> list[types.TextContent | types.ImageContent]:
    """Execute Python code in a chroot environment with `uv`.
    
    Args:
        python_code: The Python code to execute
        requirements: Optional list of package names to install via uv
        
    Returns:
        List of results containing text output and images saved to `img/`
    """
    # or displayed with plt.show()
    # List of results containing text output and an image, if plt.show() was used or manually saved to output.png

    ctx = app._mcp_server.request_context
    session_id = get_session_id(ctx)
    print(f"Session {session_id}, exec_python")
    
    executor = ChrootExecutor(session_id)
    
    try:
        # Execute the Python code
        results = executor.exec_venv(python_code, requirements)
        
        # Filter out None values and process results
        processed_results = []
        
        for result in results:              
            if isinstance(result, Image.Image):
                b = io.BytesIO()
                result.save(b, 'PNG')
                processed_results.append(types.ImageContent(
                    type="image",
                    data = base64.b64encode(b.getvalue()).decode('utf-8'),
                    mimeType = "image/png"
                ))
            else:
                if not str(result):
                    continue

                processed_results.append(types.TextContent(
                    type="text",
                    text=str(result)
                ))
        
        return processed_results
        
    except Exception as e:
        # Return error as text result
        return [types.TextContent(
            type="text",
            text=f"Error executing Python code: {str(e)}"
        )]


@app.tool()
async def exec_bash(bash_code: str) -> list[str]:
    ctx = app._mcp_server.request_context
    session_id = get_session_id(ctx)
    print(f"Session {session_id}, exec_bash")
    
    executor = ChrootExecutor(session_id)

    return executor.exec_shell(bash_code)


def main_stdio():
    app.run(transport="stdio")


def main_http():
    import anyio
    from anycorn.config import Config
    from anycorn import serve

    config = Config()
    config.bind = [f"{app.settings.host}:{app.settings.port}"]

    anyio.run(serve, app.streamable_http_app(), config, backend="trio")
