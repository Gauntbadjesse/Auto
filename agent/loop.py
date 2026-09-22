import json

from openai import OpenAI

from . import config
from .browser import DomainNotAllowed, SiteBrowser
from .tools import TOOLS, dispatch

SYSTEM_PROMPT = (
    f"You are an autonomous web agent restricted to {config.ALLOWED_DOMAIN}. "
    "You may only navigate to and act on pages under that domain; any attempt "
    "to leave it will be blocked. Use the available tools step by step: read "
    "the page before acting, fill and click forms deliberately, and call "
    "finish(summary) once the task is done or you're stuck."
)


async def run_agent(task: str) -> str:
    client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)
    browser = SiteBrowser()
    await browser.start()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    try:
        for _ in range(config.MAX_STEPS):
            resp = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                tools=TOOLS,
            )
            msg = resp.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))

            if not msg.tool_calls:
                return msg.content or "(no response)"

            for call in msg.tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments or "{}")

                if name == "finish":
                    return args.get("summary", "Done.")

                try:
                    result = await dispatch(browser, name, args)
                except DomainNotAllowed as e:
                    result = f"BLOCKED: {e}"
                except Exception as e:  # noqa: BLE001 - surface to the model, don't crash the loop
                    result = f"ERROR: {e}"

                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": result}
                )

        return "Stopped: reached max steps without finishing."
    finally:
        await browser.stop()
