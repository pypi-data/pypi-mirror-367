from dotenv import load_dotenv

from notion_model import Client

# Load environment variables from .env file
load_dotenv()


client = Client()

pages = client.search.search_by_title()

# page = client.pages.retrieve_a_page("24788b4478e380a1bfe8c5a3a57287be")
