# lib/edible_api.py

from typing import List

import requests

from lib.types import Product


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
            print(f"✓ Using cached results for '{keyword}'")
            return self.cache[keyword]

        print(f"→ Fetching from API: '{keyword}'")

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
                print(f"✗ API Error: Status {response.status_code}")
                return []

            # Response is a direct array
            data = response.json()
            products = self._parse_response(data)

            # Cache results
            self.cache[keyword] = products

            print(f"✓ Found {len(products)} products")
            return products

        except Exception as e:
            print(f"✗ Error: {e}")
            return []

    def _parse_response(self, data: List[dict]) -> List[Product]:
        """Parse API response into Product objects"""
        products = []

        for index, item in enumerate(data, start=1):
            try:
                # Use maxPrice as requested
                price = item.get("maxPrice", item.get("minPrice", 0))

                product = Product(
                    id=str(item.get("id", "")),
                    name=item.get("alt", item.get("name", "Unknown Product")),
                    description=item.get("description", ""),
                    meta_description=item.get("metaTagDescription"),
                    price=float(price),
                    image_url=item.get("image"),
                    thumbnail_url=item.get("thumbnail"),
                    ingredients=item.get("ingrediantNames"),
                    popularity_rank=index,
                )

                products.append(product)

            except Exception as e:
                print(f"Warning: Couldn't parse product at index {index}: {e}")
                continue

        return products

    def clear_cache(self):
        """Clear cached results"""
        self.cache = {}
