import asyncio
import sys

from agent.loop import run_agent


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py "task description"')
        sys.exit(1)
    task = " ".join(sys.argv[1:])
    result = asyncio.run(run_agent(task))
    print(result)


if __name__ == "__main__":
    main()
