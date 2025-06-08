import os
from typing import TypedDict, Annotated, List
from langgraph.graph import Graph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables.graph import MermaidDrawMethod
from datetime import datetime
import re

from getpass import getpass
from dotenv import load_dotenv

from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup

from IPython.display import display, Image as IPImage
import asyncio


class GraphState(TypedDict):
    news_query: Annotated[
        str, "Input query to extract news search parameters from."
    ]
    num_searches_remaining: Annotated[int, "Number of articles to search for."]
    newsapi_params: Annotated[dict, "Structured argument for the News API."]
    past_searches: Annotated[List[dict], "List of search params already used."]
    articles_metadata: Annotated[
        list[dict], "Article metadata response from the News API"
    ]
    scraped_urls: Annotated[List[str], "List of urls already scraped."]
    num_articles_tldr: Annotated[
        int, "Number of articles to create TL;DR for."
    ]
    potential_articles: Annotated[
        List[dict[str, str, str]],
        "Article with full text to consider summarizing.",
    ]
    tldr_articles: Annotated[
        List[dict[str, str, str]], "Selected article TL;DRs."
    ]
    formatted_results: Annotated[str, "Formatted results to display."]


class NewsApiParams(BaseModel):
    q: str = Field(
        description="1-3 concise keyword search terms that are not too specific"
    )
    sources: str = Field(
        description="comma-separated list of sources from: 'abc-news,abc-news-au,associated-press,australian-financial-review,axios,bbc-news,bbc-sport,bloomberg,business-insider,cbc-news,cbs-news,cnn,financial-post,fortune'"
    )
    from_param: str = Field(
        description="date in format 'YYYY-MM-DD' Two days ago minimum. Extend up to 30 days on second and subsequent requests."
    )
    to: str = Field(
        description="date in format 'YYYY-MM-DD' today's date unless specified"
    )
    language: str = Field(
        description="language of articles 'en' unless specified one of ['ar', 'de', 'en', 'es', 'fr', 'he', 'it', 'nl', 'no', 'pt', 'ru', 'se', 'ud', 'zh']"
    )
    sort_by: str = Field(
        description="sort by 'relevancy', 'popularity', or 'publishedAt'"
    )
