from fastapi import FastAPI
from fastapi.responses import StreamingResponse
try:
    from service import (
        get_openai_stream_example, 
        get_openai_invoke_example, 
        get_openai_stream,
        get_llm_module_stream_example,
        get_llm_module_invoke_example
    )
except ImportError:
    from .service import (
        get_openai_stream_example, 
        get_openai_invoke_example, 
        get_openai_stream,
        get_llm_module_stream_example,
        get_llm_module_invoke_example
    )

app = FastAPI()

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/openai-stream-example")
async def openai_stream_example():
    """Example endpoint showing new callback pattern with streaming"""
    return StreamingResponse(
        get_openai_stream_example(),
        media_type="text/event-stream"
    )

@app.post("/openai-invoke-example")
async def openai_invoke_example():
    """Example endpoint showing new callback pattern with invoke"""
    result = await get_openai_invoke_example()
    return result

@app.post("/openai-stream")
async def openai_stream(input_text: str = "한국", model: str = "gpt-4"):
    """Parameterized streaming endpoint"""
    return StreamingResponse(
        get_openai_stream(input_text, model),
        media_type="text/event-stream"
    )

@app.post("/llm-module-stream-example")
async def llm_module_stream_example():
    """Example endpoint using llm_module functions with streaming"""
    return StreamingResponse(
        get_llm_module_stream_example(),
        media_type="text/event-stream"
    )

@app.post("/llm-module-invoke-example")
async def llm_module_invoke_example():
    """Example endpoint using llm_module functions with invoke"""
    result = await get_llm_module_invoke_example()
    return result
