#Build reliable wrapper around Edible API with caching and error handling.

import requests
#import json
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from lib.types import Product

class EdibleAPIClient:
    """Client for Edible Arrangements API"""

    def __init__(self, base_url: str = "https://www.ediblearrangements.com/api/search/"):
        self.base_url = base_url
        self.cache: Dict[str, tuple[List[Product], datetime]] = {}
        self.cache_ttl = timedelta(minutes=30)

    def search(self, keyword: str, use_cache: bool = True) -> List[Product]:
        """
        Search Edible API for products

        Args:
            keyword: Search term
            use_cache: Whether to use cached results

        Returns:
            List of Product objects
        """
        # Check cache
        if use_cache and keyword in self.cache:
            products, cached_at = self.cache[keyword]
            if datetime.now() - cached_at < self.cache_ttl:
                print(f"Cache hit for '{keyword}' ({len(products)} products)")
                return products

        # Make API request
        print(f"Fetching products for '{keyword}' from API...")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        payload = {"keyword": keyword}

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            products = self._parse_response(data)

            # Cache results
            self.cache[keyword] = (products, datetime.now())

            print(f"Found {len(products)} products")
            return products

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []

    def _parse_response(self, data: dict) -> List[Product]:
        """Parse API response into Product objects"""
        products = []

        # Adjust this based on actual API response structure
        # You'll need to inspect the real response and adapt
        items = data.get('products', []) or data.get('items', []) or data.get('results', [])

        for item in items:
            try:
                product = Product(
                    id=str(item.get('id', item.get('sku', ''))),
                    name=item.get('name', item.get('title', 'Unknown')),
                    description=item.get('description', ''),
                    price=float(item.get('price', 0)),
                    image_url=item.get('image', item.get('imageUrl')),
                    rating=item.get('rating'),
                    review_count=item.get('reviewCount', item.get('reviews')),
                    category=item.get('category'),
                    raw_data=item
                )
                products.append(product)
            except Exception as e:
                print(f"Error parsing product: {e}")
                continue

        return products

    def search_multiple(self, keywords: List[str]) -> List[Product]:
        """
        Search for multiple keywords and merge results
        Deduplicates by product ID
        """
        all_products = []
        seen_ids = set()

        for keyword in keywords:
            products = self.search(keyword)
            for product in products:
                if product.id not in seen_ids:
                    all_products.append(product)
                    seen_ids.add(product.id)

        print(f"Merged {len(all_products)} unique products from {len(keywords)} searches")
        return all_products

# ===== KEYWORD MAPPING =====

OCCASION_KEYWORDS = {
    "birthday": ["birthday", "celebration", "party"],
    "anniversary": ["anniversary", "romance", "love"],
    "thank you": ["thank you", "appreciation", "gratitude"],
    "get well soon": ["get well", "sympathy", "comfort"],
    "congratulations": ["congratulations", "celebration", "achievement"],
    "just because": ["gift", "surprise", "treat"],
}

def get_keywords_for_occasion(occasion: str, budget: Optional[float] = None) -> List[str]:
    """Generate search keywords for an occasion"""
    base_keywords = OCCASION_KEYWORDS.get(occasion.lower(), ["gift"])

    # Add budget-related keywords
    if budget:
        if budget < 50:
            base_keywords.append("affordable")
        elif budget > 100:
            base_keywords.append("premium")

    return base_keywords
