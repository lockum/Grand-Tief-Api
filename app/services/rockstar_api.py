import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

NEWSWIRE_QUERY = """
query NewswireList(
    $locale: String!
    $page: Int!
    $limit: Int
    $tagIdHash: String
    $metaUrl: String!
) {
    posts(
        page: $page
        locale: $locale
        limit: $limit
        tagIdHash: $tagIdHash
    ) {
        paging {
            pageCount
            page
            count
            nextPage
            prevPage
            perPage
        }
        results {
            id: id_hash
            url
            title
            name_slug
            created
            created_formatted
            primary_tags {
                id
                name
            }
            secondary_tags {
                id
                name
            }
            preview_images_parsed {
                newswire_block {
                    square
                    d16x9
                    _fallback
                }
            }
        }
    }
}
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": settings.ROCKSTAR_BASE_URL,
    "Referer": f"{settings.ROCKSTAR_BASE_URL}/newswire"
}


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    return BeautifulSoup(raw_html, "html.parser").get_text().strip()


def determine_category(tags: List[str], tag_filter: Optional[str] = None) -> str:
    tags_lower = [t.lower() for t in tags]
    if tag_filter == "vi" or any("vi" in t or "gta 6" in t or "grand theft auto vi" in t for t in tags_lower):
        return "gta6"
    if tag_filter == "gta-online" or any("gta online" in t for t in tags_lower):
        return "gta_online"
    return "rockstar"


def check_is_weekly_event(title: str, tags: List[str]) -> bool:
    title_lower = title.lower()
    keywords = [
        "bonuses", "discounts", "event week", "double rewards", "triple rewards",
        "podium", "prize ride", "claim a free", "weekly update", "gta+ members"
    ]
    return any(kw in title_lower for kw in keywords)


async def fetch_newswire_posts(
    tag_id_hash: Optional[str] = None,
    page: int = 1,
    limit: int = 15,
    locale: str = "en_us"
) -> List[Dict[str, Any]]:
    """
    Fetches official posts from Rockstar Games GraphQL API.
    """
    variables = {
        "locale": locale,
        "page": page,
        "limit": limit,
        "tagIdHash": tag_id_hash,
        "metaUrl": "/newswire"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                settings.ROCKSTAR_GRAPHQL_URL,
                json={"query": NEWSWIRE_QUERY, "variables": variables},
                headers=HEADERS
            )

        if resp.status_code != 200:
            logger.error(f"Rockstar API returned HTTP {resp.status_code}: {resp.text}")
            return []

        data = resp.json()
        results = data.get("data", {}).get("posts", {}).get("results", [])

        normalized_posts = []
        for post in results:
            post_id = post.get("id")
            if not post_id:
                continue

            raw_title = post.get("title", "")
            title = clean_html(raw_title)

            # Extract tags
            ptags = [t.get("name") for t in (post.get("primary_tags") or []) if t.get("name")]
            stags = [t.get("name") for t in (post.get("secondary_tags") or []) if t.get("name")]
            tags = list(dict.fromkeys(ptags + stags))

            category = determine_category(tags, tag_id_hash)
            is_weekly = check_is_weekly_event(title, tags)

            # Images
            imgs = post.get("preview_images_parsed", {}).get("newswire_block", {})
            image_url = imgs.get("d16x9") or imgs.get("square") or imgs.get("_fallback")

            raw_url = post.get("url", "")
            full_url = f"{settings.ROCKSTAR_BASE_URL}{raw_url}" if raw_url.startswith("/") else raw_url

            normalized_posts.append({
                "id": post_id,
                "title": title,
                "slug": post.get("name_slug"),
                "url": full_url,
                "image_url": image_url,
                "category": category,
                "tags": tags,
                "published_at": post.get("created"),
                "is_weekly_event": is_weekly
            })

        return normalized_posts

    except Exception as e:
        logger.error(f"Error fetching from Rockstar API: {e}", exc_info=True)
        return []

