"""
Default unique products fallback system

When Path B (semantic filtering) fails to find unique products,
this module provides a curated set of default unique products
that can be matched against the recipient's description.
"""

import json
import logging
from pathlib import Path
from typing import List

from lib.edible_api import EdibleAPIClient
from lib.types import Product

logger = logging.getLogger(__name__)

# Keywords for fetching unique default products
DEFAULT_UNIQUE_KEYWORDS = ["wellness", "hot sauce", "plants", "sculpd"]

DEFAULT_UNIQUES_FILE = Path(__file__).parent.parent / "data" / "default_uniques.json"


class DefaultUniqueProducts:
    """Manages default unique products for fallback matching"""

    def __init__(self):
        self.edible_client = EdibleAPIClient()
        self._products_cache: List[Product] = []

    def get_default_products(self, force_refresh: bool = False) -> List[Product]:
        """
        Get default unique products, loading from cache or fetching if needed

        Args:
            force_refresh: If True, ignore cache and fetch fresh from API

        Returns:
            List of default unique products
        """
        if force_refresh or not self._products_cache:
            # Try to load from file first
            if not force_refresh and DEFAULT_UNIQUES_FILE.exists():
                logger.debug("[DEFAULT UNIQUES] Loading from cache file...")
                self._products_cache = self._load_from_file()
            
            # If still empty, fetch from API
            if not self._products_cache:
                logger.info("[DEFAULT UNIQUES] Fetching from API...")
                self._products_cache = self._fetch_from_api()
                self._save_to_file(self._products_cache)
        
        return self._products_cache

    def _fetch_from_api(self) -> List[Product]:
        """Fetch default unique products from API"""
        all_products = []
        
        for keyword in DEFAULT_UNIQUE_KEYWORDS:
            logger.debug(f"[DEFAULT UNIQUES] Fetching products for '{keyword}'...")
            products = self.edible_client.search(keyword, use_cache=True)
            
            # Take top 5 products per keyword to keep it manageable
            all_products.extend(products[:5])
            logger.debug(f"  Added {len(products[:5])} products")
        
        # Deduplicate by product ID
        unique_products = {}
        for product in all_products:
            if product.id not in unique_products:
                unique_products[product.id] = product
        
        result = list(unique_products.values())
        logger.info(f"[DEFAULT UNIQUES] Fetched {len(result)} unique products")
        
        return result

    def _load_from_file(self) -> List[Product]:
        """Load products from cache file"""
        try:
            with open(DEFAULT_UNIQUES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            products = [Product(**item) for item in data]
            logger.debug(f"[DEFAULT UNIQUES] Loaded {len(products)} products from cache")
            return products
        
        except Exception as e:
            logger.warning(f"[DEFAULT UNIQUES] Failed to load from cache: {e}")
            return []

    def _save_to_file(self, products: List[Product]) -> None:
        """Save products to cache file"""
        try:
            # Ensure data directory exists
            DEFAULT_UNIQUES_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert products to dict for JSON serialization
            data = [product.model_dump() for product in products]
            
            with open(DEFAULT_UNIQUES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"[DEFAULT UNIQUES] Saved {len(products)} products to cache")
        
        except Exception as e:
            logger.warning(f"[DEFAULT UNIQUES] Failed to save to cache: {e}")

    def clear_cache(self) -> None:
        """Clear in-memory and file cache"""
        self._products_cache = []
        if DEFAULT_UNIQUES_FILE.exists():
            DEFAULT_UNIQUES_FILE.unlink()
            logger.info("[DEFAULT UNIQUES] Cache cleared")
