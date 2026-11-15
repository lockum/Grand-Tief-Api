import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def fetch_article_details(article_url: str) -> Dict[str, Any]:
    """
    Fetches the article web page to extract OpenGraph description, full text summary,
    and structured event bonuses if applicable.
    """
    details: Dict[str, Any] = {
        "summary": None,
        "bonuses": [],
        "discounts": [],
        "podium_vehicle": None,
        "prize_ride": None,
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(article_url, headers=HEADERS, follow_redirects=True)

        if resp.status_code != 200:
            return details

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract meta description
        og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        if og_desc and og_desc.get("content"):
            details["summary"] = og_desc["content"].strip()

        # Look for bonuses & discounts keywords in text
        text = soup.get_text()

        # Search for podium vehicle patterns
        podium_match = re.search(r'Lucky Wheel(?:.*?Podium Vehicle)?[:\s]+(?:The\s+)?([A-Za-z0-9\s\-]+?)(?:\.|\n|$)', text, re.IGNORECASE)
        if podium_match:
            details["podium_vehicle"] = podium_match.group(1).strip()

        # Search for prize ride patterns
        prize_match = re.search(r'Prize Ride[:\s]+(?:The\s+)?([A-Za-z0-9\s\-]+?)(?:\.|\n|$)', text, re.IGNORECASE)
        if prize_match:
            details["prize_ride"] = prize_match.group(1).strip()

        # Extract bullet points / list items
        for li in soup.find_all("li"):
            item_text = li.get_text().strip()
            if not item_text:
                continue
            lower_item = item_text.lower()
            if "2x" in lower_item or "3x" in lower_item or "double" in lower_item or "triple" in lower_item or "gta$" in lower_item or "rp" in lower_item:
                details["bonuses"].append(item_text)
            elif "% off" in lower_item or "discount" in lower_item:
                details["discounts"].append(item_text)

        # Keep lists clean and bounded
        details["bonuses"] = details["bonuses"][:10]
        details["discounts"] = details["discounts"][:10]

        return details

    except Exception as e:
        logger.warning(f"Failed to parse article details for {article_url}: {e}")
        return details

