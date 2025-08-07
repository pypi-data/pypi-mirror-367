"""Unit tests for the test_pkg package."""

import os

import pytest

from notion_model import Client

if os.getenv("NOTION_API_KEY") is None:
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()


@pytest.fixture(scope="module", name="notion_client")
def fixture_notion_client():
    """Fixture to create a Notion client."""
    if not os.getenv("NOTION_API_KEY"):
        raise ValueError("NOTION_API_KEY not found in environment variables")
    return Client()


def test_retrieve_pages(notion_client: Client) -> None:
    """Example test case."""
    pages = notion_client.search.search_by_title()
    assert len(pages) > 0, "Expected at least one page"

    for page in pages:
        if page.object == "page":
            notion_client.pages.retrieve_a_page(page.id)
        else:
            pass
            # TODO: implement database case


def test_retrieve_page_children(notion_client: Client) -> None:
    """Example test case."""
    page_id: str = "24688b4478e38174bf36eea6b53543b8"
    blocks = notion_client.blocks.retrieve_block_children(page_id)
    assert len(blocks) > 0, "Expected at least one block"

    for block in blocks:
        if block.has_children:
            children = notion_client.blocks.retrieve_block_children(block.id)
            assert len(children) >= 0, "Expected zero or more child blocks"
        notion_client.blocks.retrieve_a_block(block.id)


def test_users(notion_client: Client) -> None:
    """Example test case for users."""
    users = notion_client.user.list_all_users()
    assert len(users) > 0, "Expected at least one user"

    for user in users:
        notion_client.user.retrieve_a_user(user.id)
