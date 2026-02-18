# lib/edible_api.py

import html
import logging
import re
from typing import List

import requests

from lib.types import Product

logger = logging.getLogger(__name__)


class EdibleAPIClient:
    """Client for Edible Arrangements API"""

    def __init__(self):
        self.base_url = "https://www.ediblearrangements.com/api/search/"
        self.cache = {}

    def search(self, keyword: str, use_cache: bool = True) -> List[Product]:
        """
        Search for products

        Args:
            keyword: Search term
            use_cache: Whether to use cached results

        Returns:
            List of Product objects
        """
        if use_cache and keyword in self.cache:
            logger.debug(f"Using cached results for '{keyword}'")
            return self.cache[keyword]

        logger.debug(f"Fetching from API: '{keyword}'")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.ediblearrangements.com/",
        }

        payload = {"keyword": keyword}

        try:
            response = requests.post(
                self.base_url, json=payload, headers=headers, timeout=10
            )

            # Accept both 200 and 201 as success
            if response.status_code not in [200, 201]:
                logger.error(f"API Error: Status {response.status_code}")
                return []

            # Response is a direct array
            data = response.json()
            products = self._parse_response(data)

            # Cache results
            self.cache[keyword] = products

            logger.debug(f"Found {len(products)} products")
            return products

        except Exception as e:
            logger.error(f"Error: {e}")
            return []

    def _parse_response(self, data: List[dict]) -> List[Product]:
        """Parse API response into Product objects"""
        products = []

        for index, item in enumerate(data, start=1):
            try:
                # Use maxPrice as requested
                price = item.get("maxPrice", item.get("minPrice", 0))

                # Sanitize description to remove HTML tags and normalize whitespace
                raw_description = item.get("description", "")
                clean_description = self._sanitize_description(raw_description)

                # Parse occasion tags from API (comma-separated string)
                occasions_raw = item.get("occasion", "")
                occasions = (
                    [
                        occ.strip().lower()
                        for occ in occasions_raw.split(",")
                        if occ.strip()
                    ]
                    if occasions_raw
                    else []
                )

                # Debug: Log first 3 products' occasion parsing
                if index <= 3:
                    logger.debug(
                        f"[API PARSE] Product #{index} ({item.get('alt', 'Unknown')[:40]}): occasion_raw='{occasions_raw}' -> parsed={occasions}"
                    )

                product = Product(
                    id=str(item.get("id", "")),
                    name=item.get("alt", item.get("name", "Unknown Product")),
                    description=clean_description,
                    meta_description=item.get("metaTagDescription"),
                    price=float(price),
                    image_url=item.get("image"),
                    thumbnail_url=item.get("thumbnail"),
                    ingredients=item.get("ingrediantNames"),
                    popularity_rank=index,
                    occasions=occasions,
                )

                products.append(product)

            except Exception as e:
                logger.warning(f"Couldn't parse product at index {index}: {e}")
                continue

        return products

    def _sanitize_description(self, description: str) -> str:
        """
        Clean description by removing HTML tags and normalizing whitespace

        Handles:
        - HTML tags: <br>, <br/>, <p>, etc.
        - HTML entities: &nbsp;, &amp;, etc.
        - Carriage returns and excessive whitespace
        - Line breaks within text
        """
        if not description:
            return ""

        # Convert common HTML entities
        text = html.unescape(description)

        # Remove HTML tags: <br>, <br/>, <p>, </p>, etc.
        text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"</?p\s*/?>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)  # Remove any other HTML tags

        # Normalize whitespace: convert \r\n, \r, \n to single space
        text = re.sub(r"[\r\n]+", " ", text)

        # Collapse multiple spaces into single space
        text = re.sub(r"\s+", " ", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def clear_cache(self):
        """Clear cached results"""
        self.cache = {}
