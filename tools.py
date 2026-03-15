from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import tool
from datetime import datetime


search = DuckDuckGoSearchRun()

search_tool = tool(name="search", func=search.run, description="Useful for searching the web for up-to-date information. Input should be a search query."
                   )