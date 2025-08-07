"""Async unit tests for the notion_model package."""

import asyncio
import os

import pytest

from notion_model import AsyncClient

if os.getenv("NOTION_API_KEY") is None:
    from dotenv import load_dotenv

    load_dotenv()


@pytest.mark.asyncio
async def test_concurrent_page_retrieval():
    """Test retrieving multiple pages concurrently."""
    async with AsyncClient() as client:
        # First get some page IDs
        pages = await client.search.search_by_title()
        assert len(pages) > 0, "Expected at least one page"

        # Take first 3 pages for concurrent retrieval
        page_ids = [page.id for page in pages[:3] if page.object == "page"]

        # Retrieve all pages concurrently
        tasks = [client.pages.retrieve_a_page(page_id) for page_id in page_ids]
        retrieved_pages = await asyncio.gather(*tasks)

        assert len(retrieved_pages) == len(page_ids)
        for page in retrieved_pages:
            assert page.id is not None


@pytest.mark.asyncio
async def test_concurrent_block_retrieval():
    """Test retrieving blocks from multiple pages concurrently."""
    async with AsyncClient() as client:
        pages = await client.search.search_by_title()
        page_ids = [page.id for page in pages[:2]]  # Test with 2 pages

        # Retrieve blocks from all pages concurrently
        tasks = [client.blocks.retrieve_block_children(page_id) for page_id in page_ids]
        all_blocks = await asyncio.gather(*tasks)

        assert len(all_blocks) == len(page_ids)

        # Now retrieve individual blocks concurrently
        all_block_ids = []
        for blocks in all_blocks:
            all_block_ids.extend([block.id for block in blocks[:2]])  # Take first 2 blocks

        if all_block_ids:
            tasks = [client.blocks.retrieve_a_block(block_id) for block_id in all_block_ids]
            retrieved_blocks = await asyncio.gather(*tasks)
            assert len(retrieved_blocks) == len(all_block_ids)


@pytest.mark.asyncio
async def test_mixed_concurrent_operations():
    """Test mixing different types of operations concurrently."""
    async with AsyncClient() as client:
        # Create tasks for different operations
        tasks = [
            client.search.search_by_title(""),
            client.user.list_all_users(),
            client.pages.retrieve_a_page("24688b4478e38174bf36eea6b53543b8"),
        ]

        # Run all operations concurrently
        search_results, users, page = await asyncio.gather(*tasks)

        assert len(search_results) > 0
        assert len(users) > 0
        assert page.id is not None


# @pytest.mark.asyncio
# async def test_async_performance_comparison():
#     """Compare sync vs async performance."""
#     import time
#     from notion_model import Client

#     # Sync version timing
#     sync_client = Client()
#     pages = sync_client.search.search_by_title()
#     page_ids = [page.id for page in pages[:3]]

#     start_time = time.time()
#     for page_id in page_ids:
#         sync_client.pages.retrieve_a_page(page_id)
#     sync_duration = time.time() - start_time

#     # Async version timing
#     async with AsyncClient() as async_client:
#         start_time = time.time()
#         tasks = [async_client.pages.retrieve_a_page(page_id) for page_id in page_ids]
#         await asyncio.gather(*tasks)
#         async_duration = time.time() - start_time

#     print(f"Sync duration: {sync_duration:.2f}s")
#     print(f"Async duration: {async_duration:.2f}s")
#     print(f"Speedup: {sync_duration / async_duration:.2f}x")

#     # Async should be faster for multiple requests
#     assert async_duration < sync_duration
