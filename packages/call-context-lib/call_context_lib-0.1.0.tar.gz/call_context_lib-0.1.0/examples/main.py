from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from .service import get_root_stream, get_v2_stream, get_invoke_data

app = FastAPI()

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/")
async def root():
    return StreamingResponse(
        await get_root_stream(),
        media_type="text/event-stream"
    )

@app.post("/v2")
async def v2():
    return StreamingResponse(
        await get_v2_stream(),
        media_type="text/event-stream"
    )

@app.post("/invoke")
async def invoke():
    data = await get_invoke_data()
    return data
