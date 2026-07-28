import os
import math
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """Search DuckDuckGo for real-time web results on a given topic or question.
    Returns a formatted list of search results with titles, links, and snippets.
    Use this for finding current information, prices, facts, or news.
    """
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            if not results:
                return "No search results found."
            formatted = []
            for r in results:
                formatted.append(f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {r.get('body')}\n")
            return "\n---\n".join(formatted)
    except Exception as e:
        return f"Error during search: {str(e)}"

@tool
def web_scrape(url: str) -> str:
    """Fetch and scrape the readable text contents of a website URL.
    Use this after finding a relevant link from web_search to read full webpage contents.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove scripts, styles, and headers/footers if possible to reduce noise
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        # Return first 4000 characters to stay within context windows
        if len(text) > 4000:
            return text[:4000] + "\n\n... (truncated for brevity) ..."
        return text
    except Exception as e:
        return f"Error scraping URL: {str(e)}"

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.
    Use this tool for math calculations like addition, subtraction, division, multiplication, exponentiation, and ratios.
    Accepts standard math syntax: e.g., '120 * 1.05', '300 / (15 + 5)', 'pow(2, 8)', 'sqrt(144)'.
    """
    try:
        # Define allowed characters/functions for safe evaluation
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
            "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "log": math.log, "pi": math.pi, "e": math.e
        }
        # Replace caret with double asterisk for exponentiation
        expression = expression.replace("^", "**")
        # Evaluate safely
        val = eval(expression, {"__builtins__": None}, allowed_names)
        return str(val)
    except Exception as e:
        return f"Error evaluating expression '{expression}': {str(e)}"

@tool
def file_write(filename: str, content: str) -> str:
    """Write or overwrite content to a file in the workspace directory.
    Use this to save summaries, reports, final analysis, data lists, or markdown files.
    The filename should be a clean relative filename, e.g. 'report.txt' or 'data.csv'.
    """
    try:
        # Prevent directory traversal
        clean_name = os.path.basename(filename)
        # Write to the current working directory (project directory or script CWD)
        with open(clean_name, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote content to file: {clean_name}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def file_read(filename: str) -> str:
    """Read contents of a file in the workspace directory.
    Use this to view previously written files or verify your outputs.
    """
    try:
        clean_name = os.path.basename(filename)
        if not os.path.exists(clean_name):
            return f"File '{clean_name}' does not exist."
        with open(clean_name, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Collection of all tools
def get_all_tools():
    return [web_search, web_scrape, calculator, file_write, file_read]
