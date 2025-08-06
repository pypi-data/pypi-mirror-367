import asyncio

async def acall_llm_stream(input: str, model: str):
    print(f"this is input :: {input}")
    print(f"this is model :: {model}")
    for word in ["Hi", " ", "there"]:
        await asyncio.sleep(0)  # ✅ 최소 하나라도 await 필요
        print(f"word is :: {word}")
        yield word

def call_llm_stream(input: str, model: str):
    print(f"this is input :: {input}")
    print(f"this is model :: {model}")
    for word in ["Hi", " ", "there"]:
        print(f"word is :: {word}")
        yield word

async def acall_llm(input: str, model: str) -> str:
    print(f"this is input :: {input}")
    print(f"this is model :: {model}")
    return f"This is input :: {input} with model :: {model}"

def call_llm(input: str, model: str) -> str:
    print(f"this is input :: {input}")
    print(f"this is model :: {model}")
    return f"This is input :: {input} with model :: {model}"
