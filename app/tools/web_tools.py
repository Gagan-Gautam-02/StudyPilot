from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_core.tools import tool

# Wikipedia Tool
api_wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=1000)
wikipedia_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

# DuckDuckGo Tool
duckduckgo_tool = DuckDuckGoSearchRun()

# ArXiv Tool wrapper
@tool
def arxiv_tool(query: str) -> str:
    """Searches scientific, research, and academic articles on ArXiv. Use this for highly technical or academic research."""
    arxiv = ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=1000)
    return arxiv.run(query)

def get_web_tools():
    """Returns a list of web search tools for the Study Agent."""
    return [wikipedia_tool, duckduckgo_tool, arxiv_tool]
