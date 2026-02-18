import json
import logging

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def explore_edible_api():
    """
    Let's see what the API actually returns!
    """
    url = "https://www.ediblearrangements.com/api/search/"

    # Test with a simple search
    keyword = "chocolate"

    payload = {"keyword": keyword}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    }

    logger.info(f"Searching for: {keyword}")
    logger.info(f"URL: {url}")
    logger.info(f"Payload: {payload}\n")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        logger.info(f"Status Code: {response.status_code}\n")

        if response.status_code == 200:
            # Get the JSON
            data = response.json()

            # Pretty print it so we can see the structure
            logger.info("=" * 60)
            logger.info("FULL RESPONSE:")
            logger.info("=" * 60)
            logger.info(json.dumps(data, indent=2))

            # Let's explore the structure
            logger.info("\n" + "=" * 60)
            logger.info("STRUCTURE ANALYSIS:")
            logger.info("=" * 60)

            logger.info(f"Top-level keys: {list(data.keys())}")

            # Try to find where the products are
            for key, value in data.items():
                logger.info(f"\n{key}: {type(value)}")
                if isinstance(value, list) and len(value) > 0:
                    logger.info(f"  → List with {len(value)} items")
                    logger.info(f"  → First item type: {type(value[0])}")
                    if isinstance(value[0], dict):
                        logger.info(f"  → First item keys: {list(value[0].keys())}")

            # Try to print first product
            logger.info("\n" + "=" * 60)
            logger.info("FIRST PRODUCT (if found):")
            logger.info("=" * 60)

            # Common places products might be:
            possible_keys = ["products", "items", "results", "data"]
            products = None

            for key in possible_keys:
                if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                    products = data[key]
                    logger.info(f"Found products at: data['{key}']")
                    break

            if products:
                logger.info(json.dumps(products[0], indent=2))
            else:
                logger.info(
                    "Couldn't automatically find products. Check the FULL RESPONSE above."
                )

        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    explore_edible_api()
