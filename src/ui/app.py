import chainlit as cl
import ollama

MODEL = "gemma4:latest"
OLLAMA_HOST = "http://localhost:11434"


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])


@cl.on_message
async def on_message(message: cl.Message):
    history: list = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    client = ollama.AsyncClient(host=OLLAMA_HOST)
    response = cl.Message(content="")
    await response.send()

    async for chunk in await client.chat(
        model=MODEL,
        messages=history,
        stream=True,
    ):
        token = chunk["message"]["content"]
        await response.stream_token(token)

    await response.update()
    history.append({"role": "assistant", "content": response.content})
    cl.user_session.set("history", history)
