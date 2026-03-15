from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

wrapper = DuckDuckGoSearchAPIWrapper(max_results=5, time="y")
search_tool = DuckDuckGoSearchRun(api_wrapper=wrapper)
