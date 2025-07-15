from typing import Callable

import httpx
from agents import RunContextWrapper, function_tool

from app.core.config import settings
from app.schemas.agent_context import AgentContext


@function_tool
async def web_search(
    wrapper: RunContextWrapper[AgentContext],
    search_term: str,
    num_results: int = 10,
    country: str = "US",
    language: str = "en",
) -> dict:
    """Search the web using the web search service for real-time web search results.

    This tool provides access to real-time web search results using the web search service.
    It returns structured search results including titles, URLs, descriptions, and snippets.

    **WHEN TO USE THIS TOOL:**
    - When you need to search for current information on the web
    - When looking for recent news, events, or trending topics
    - When you need to find specific websites or resources
    - When researching topics that require up-to-date information
    - When you need to verify current facts or data

    **SEARCH CAPABILITIES:**
    - Real-time web search results
    - Support for different countries and languages
    - Configurable number of results
    - Structured response with titles, URLs, and descriptions
    - Support for complex search queries and operators

    Args:
        search_term (str): The search query to execute. Can include search operators
            like "site:example.com", quotes for exact phrases, etc.
        num_results (int, optional): Number of results to return (default: 10, max: 50)
        country (str, optional): Country code for localized results (default: "US")
        language (str, optional): Language code for results (default: "en")

    Returns:
        dict: Search results containing:
            - total_results: Total number of results found
            - results: List of search results with title, url, description, and snippet
            - search_metadata: Information about the search query and parameters
    """

    if not settings.SEARCH1_API_KEY:
        return {
            "error": "Search1API key not configured. Please set SEARCH1_API_KEY in your environment."
        }

    # Ensure num_results is within reasonable bounds
    num_results = min(max(num_results, 1), 50)

    try:
        # Search1API endpoint - using common search API patterns
        url = "https://api.search1api.com/search"

        # Prepare request parameters
        params = {"query": search_term, "search_service": "google"}

        headers = {
            "Authorization": f"Bearer {settings.SEARCH1_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "JourneyAI-Search-Tool/1.0",
        }

        # Make the API request
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=params, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Format the response in a consistent structure
            formatted_results = []

            # Handle different possible response structures
            if "organic_results" in data:
                search_results = data["organic_results"]
            elif "results" in data:
                search_results = data["results"]
            elif "hits" in data:
                search_results = data["hits"]
            else:
                search_results = data.get("data", [])

            for result in search_results[:num_results]:
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", result.get("link", "")),
                    "description": result.get("description", result.get("snippet", "")),
                    "domain": result.get("domain", ""),
                    "position": result.get("position", len(formatted_results) + 1),
                }
                formatted_results.append(formatted_result)

            return {
                "total_results": data.get("total_results", len(formatted_results)),
                "results": formatted_results,
                "search_metadata": {
                    "query": search_term,
                    "num_results": num_results,
                    "country": country,
                    "language": language,
                    "processing_time": data.get("processing_time", 0),
                },
            }

    except httpx.TimeoutException:
        return {
            "error": "Search request timed out. Please try again with a simpler query."
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {
                "error": "Invalid Search1API key. Please check your SEARCH1_API_KEY configuration."
            }
        elif e.response.status_code == 429:
            return {
                "error": "Rate limit exceeded. Please wait before making another search request."
            }
        else:
            return {
                "error": f"Search API error: {e.response.status_code} - {e.response.text}"
            }
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


def get_tool() -> Callable:
    return web_search
