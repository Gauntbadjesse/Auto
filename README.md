# newlifesmp agent

A self-directed web agent that plans its own steps (via a self-hosted LLM) and
acts on **newlifesmp.com only** — navigation and clicks that would leave that
domain are blocked at the browser layer, not just by prompt instructions.

## Setup

1. Self-host an LLM with an OpenAI-compatible API, e.g. [Ollama](https://ollama.com):
   ```
   ollama pull llama3.1:8b   # or qwen2.5:7b / mistral-nemo — any tool-calling model
   ollama serve
   ```
2. `pip install -r requirements.txt && playwright install chromium`
3. `cp .env.example .env` and fill in `LLM_MODEL`, `ALLOWED_DOMAIN`, and
   `SITE_USERNAME`/`SITE_PASSWORD` if the agent needs to log in.
4. Run a task:
   ```
   python main.py "Go to newlifesmp.com, open the whitelist application form, and fill it out with test data"
   ```

## How it's scoped to one site

`agent/browser.py` intercepts every navigation (direct `goto`, link clicks,
redirects) and aborts it unless the URL's host is `ALLOWED_DOMAIN` or a
subdomain of it. The LLM only ever sees `goto`/`click`/`fill`/`read_text`
tools — it has no raw HTTP or filesystem access.

## Notes for the remote server (once you have specs)

- Model size should match available RAM/VRAM: 7-8B models run fine on a
  single consumer GPU or in CPU mode (slower); pick a bigger quantized model
  only if you have the VRAM to spare.
- Playwright needs its browser binaries (`playwright install chromium`) and,
  on a headless Linux box, usually its system deps too
  (`playwright install-deps`).
- Tell me the server's OS/GPU and I'll adjust the model choice and any
  systemd/service setup.
