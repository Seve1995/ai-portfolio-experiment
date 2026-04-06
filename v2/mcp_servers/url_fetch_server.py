"""
MCP Tool: URL Fetch (Sanitized)
Purpose: Read a URL and extract clean text. HTML stripped, scripts removed.
Security: Treats all web content as untrusted data. Sanitizes against prompt injection.
"""

import logging
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TOOL_DEFINITION = {
    "name": "fetch_url",
    "description": (
        "Fetch and read a web page's text content. Use this to read articles, SEC filings, "
        "earnings reports, or analyst research found via web_search. "
        "The content is cleaned (no ads, scripts, navigation) and truncated to fit context limits."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Full URL to fetch (must start with https://)"
            },
            "max_chars": {
                "type": "integer",
                "minimum": 500,
                "maximum": 8000,
                "default": 4000,
                "description": "Maximum characters of text to return (500-8000)"
            }
        },
        "required": ["url"]
    }
}

# Domains we refuse to fetch (security or irrelevance)
BLOCKED_DOMAINS = [
    "localhost", "127.0.0.1", "0.0.0.0",
    "internal", ".local",
]

# Tags to remove entirely (content + tag)
STRIP_TAGS = [
    "script", "style", "nav", "header", "footer",
    "aside", "iframe", "noscript", "svg", "form",
    "button", "input", "select", "textarea",
]


def _sanitize_text(text: str) -> str:
    """
    Sanitize extracted text against prompt injection.
    Remove anything that looks like it's trying to manipulate the AI.
    """
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{3,}', '  ', text)
    
    # Strip common injection patterns
    injection_patterns = [
        r'(?i)ignore\s+(all\s+)?previous\s+instructions',
        r'(?i)you\s+are\s+now\s+a',
        r'(?i)system\s*:\s*',
        r'(?i)assistant\s*:\s*',
        r'(?i)<\s*system\s*>',
    ]
    for pattern in injection_patterns:
        text = re.sub(pattern, '[FILTERED]', text)
    
    return text.strip()


def execute(url: str, max_chars: int = 4000) -> dict:
    """
    Fetch URL, extract text, sanitize.
    
    Returns:
        {
            "url": "https://...",
            "title": "Article Title",
            "text": "Clean extracted text...",
            "char_count": 3500,
            "truncated": false
        }
    """
    # Validate URL
    if not url.startswith(("https://", "http://")):
        return {"error": "URL must start with https:// or http://"}

    for blocked in BLOCKED_DOMAINS:
        if blocked in url.lower():
            return {"error": f"Blocked domain: {blocked}"}

    max_chars = min(max(max_chars, 500), 8000)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AIPortfolioBot/2.0; +https://github.com/Seve1995/ai-portfolio-experiment)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        with httpx.Client(timeout=15.0, follow_redirects=True, max_redirects=3) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "text/plain" not in content_type:
            return {"error": f"Unsupported content type: {content_type}", "url": url}

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Remove unwanted tags
        for tag_name in STRIP_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Extract text
        text = soup.get_text(separator="\n")
        text = _sanitize_text(text)

        # Truncate
        truncated = False
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            truncated = True

        logger.info(f"Fetched {url}: {len(text)} chars, truncated={truncated}")

        return {
            "url": url,
            "title": title,
            "text": text,
            "char_count": len(text),
            "truncated": truncated,
        }

    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}", "url": url}
    except httpx.TimeoutException:
        return {"error": "Request timed out (15s)", "url": url}
    except Exception as e:
        logger.error(f"URL fetch error: {e}")
        return {"error": str(e), "url": url}
