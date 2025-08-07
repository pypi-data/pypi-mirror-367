import asyncio
import os
from time import perf_counter

from dotenv import load_dotenv

from notion_model import AsyncClient, Client

load_dotenv()


async def main_async():
    async with AsyncClient(os.getenv("NOTION_API_KEY")) as client:
        # Get pages
        pages = await client.search.search_by_title()
        print(f"Found {len(pages)} pages")

        # Retrieve multiple pages concurrently (much faster!)
        tasks = [client.pages.retrieve_a_page(page.id) for page in pages[:3]]
        retrieved_pages = await asyncio.gather(*tasks)
        print(f"Retrieved {len(retrieved_pages)} pages concurrently")

        tasks = [client.blocks.retrieve_block_children(page.id) for page in retrieved_pages]
        page_contents = await asyncio.gather(*tasks)
        print(f"Retrieved {len(page_contents)} page contents concurrently")


def main_sync():
    client = Client(os.getenv("NOTION_API_KEY"))
    pages = client.search.search_by_title()
    print(f"Found {len(pages)} pages")

    # Retrieve multiple pages concurrently (much faster!)
    retrieved_pages = [client.pages.retrieve_a_page(page.id) for page in pages[:3]]
    print(f"Retrieved {len(retrieved_pages)} pages")

    page_contents = [
        client.blocks.retrieve_block_children(page.id) for page in retrieved_pages
    ]
    print(f"Retrieved {len(page_contents)} page contents")


if __name__ == "__main__":
    start = perf_counter()
    asyncio.run(main_async())
    print(f"Async execution time: {perf_counter() - start:.2f} seconds")

    start = perf_counter()
    main_sync()
    print(f"Sync execution time: {perf_counter() - start:.2f} seconds")
