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
            "description": "Read the full visible text of the current page, for context/instructions.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "look",
            "description": (
                "Look at the page like a human would: returns a numbered list of visible "
                "buttons, links, and form fields with their labels. Call this before click/type "
                "to see what's on screen, and again after the page changes."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Click the element with this number, as shown by look().",
            "parameters": {
                "type": "object",
                "properties": {"element_id": {"type": "integer"}},
                "required": ["element_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type",
            "description": "Type text into the input/textarea with this number, as shown by look().",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_id": {"type": "integer"},
                    "value": {"type": "string"},
                },
                "required": ["element_id", "value"],
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
        return await browser.read_text()
    if name == "look":
        return await browser.look()
    if name == "click":
        return await browser.click(args["element_id"])
    if name == "type":
        return await browser.type(args["element_id"], args["value"])
    if name == "login":
        return await browser.login()
    raise ValueError(f"Unknown tool: {name}")
