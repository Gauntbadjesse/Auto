TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "goto",
            "description": "Navigate to a URL. Must be on the allowed domain.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_text",
            "description": "Read visible text from the current page (or a CSS selector within it).",
            "parameters": {
                "type": "object",
                "properties": {"selector": {"type": "string", "default": "body"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Click an element matching a CSS selector on the current page.",
            "parameters": {
                "type": "object",
                "properties": {"selector": {"type": "string"}},
                "required": ["selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fill",
            "description": "Type a value into an input/textarea matching a CSS selector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["selector", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "login",
            "description": "Check whether site credentials are configured before attempting a login form.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "Call when the task is complete (or cannot be completed) to stop and report back.",
            "parameters": {
                "type": "object",
                "properties": {"summary": {"type": "string"}},
                "required": ["summary"],
            },
        },
    },
]


async def dispatch(browser, name: str, args: dict) -> str:
    if name == "goto":
        return await browser.goto(args["url"])
    if name == "read_text":
        return await browser.read_text(args.get("selector", "body"))
    if name == "click":
        return await browser.click(args["selector"])
    if name == "fill":
        return await browser.fill(args["selector"], args["value"])
    if name == "login":
        return await browser.login()
    raise ValueError(f"Unknown tool: {name}")
