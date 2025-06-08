import os
import asyncio

from dotenv import load_dotenv


async def main():

    from workflow import run_workflow

    query = """What are the news of today of Biotechnology companies in large U.S. cities?"""

    print(await run_workflow(query, num_articles_tldr=5))


if __name__ == "__main__":
    load_dotenv()

    asyncio.run(main())
