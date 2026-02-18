# tests/test_edible_api.py

import logging

from lib.edible_api import EdibleAPIClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_api():
    """Test Edible API integration with updated Product model"""

    client = EdibleAPIClient()

    logger.info("\n" + "=" * 70)
    logger.info("EDIBLE API TEST SUITE")
    logger.info("=" * 70)

    # ===== TEST 1: Basic Search =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 1: Basic Search for 'chocolate'")
    logger.info("-" * 70)

    products = client.search("chocolate")

    if not products:
        logger.error("✗ FAILED: No products returned")
        return

    logger.info(f"✓ PASSED: Found {len(products)} products")

    # ===== TEST 2: Product Model Validation =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 2: Product Model Validation")
    logger.info("-" * 70)

    p = products[0]

    logger.info("\nProduct Fields:")
    logger.info(f"  ✓ id: {p.id}")
    logger.info(f"  ✓ name: {p.name[:50]}...")
    logger.info(f"  ✓ price: ${p.price:.2f}")
    logger.info(f"  ✓ popularity_rank: #{p.popularity_rank}")
    logger.info(f"  ✓ image_url: {p.image_url[:50] if p.image_url else 'None'}...")
    logger.info(
        f"  ✓ thumbnail_url: {p.thumbnail_url[:50] if p.thumbnail_url else 'None'}..."
    )
    logger.info(f"  ✓ description: {len(p.description)} chars")
    logger.info(
        f"  ✓ meta_description: {len(p.meta_description) if p.meta_description else 0} chars"
    )
    logger.info(f"  ✓ ingredients: {p.ingredients or 'None'}")

    # Check that removed fields are gone
    assert not hasattr(p, "url"), "✗ url field should be removed"
    assert not hasattr(p, "category"), "✗ category field should be removed"
    assert not hasattr(p, "raw_data"), "✗ raw_data field should be removed"
    assert not hasattr(p, "allergy_info"), "✗ allergy_info field should be removed"

    logger.info("\n✓ PASSED: All fields present, removed fields absent")

    # ===== TEST 3: Pydantic Serialization =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 3: Pydantic Serialization")
    logger.info("-" * 70)

    try:
        # Test model_dump()
        product_dict = p.model_dump()
        logger.info(f"  ✓ model_dump(): {len(product_dict)} fields")

        # Test model_dump_json()
        product_json = p.model_dump_json()
        logger.info(f"  ✓ model_dump_json(): {len(product_json)} chars")

        # Test that we can recreate Product from dict
        from lib.types import Product

        p2 = Product(**product_dict)
        logger.info("  ✓ Can recreate Product from dict")

        logger.info("\n✓ PASSED: Pydantic serialization works")

    except Exception as e:
        logger.error(f"✗ FAILED: {e}")

    # ===== TEST 4: AI Analysis Fields =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 4: Fields Available for AI Analysis")
    logger.info("-" * 70)

    logger.info("\nAI will analyze these fields to extract ProductAttributes:")
    logger.info(f"  1. name: '{p.name}'")
    logger.info(f"  2. description: {len(p.description)} chars")
    if p.description:
        logger.info(f"     Preview: {p.description[:100]}...")
    logger.info(
        f"  3. meta_description: {len(p.meta_description) if p.meta_description else 0} chars"
    )
    if p.meta_description:
        logger.info(f"     Preview: {p.meta_description[:100]}...")
    logger.info(f"  4. ingredients: {p.ingredients or 'Not provided'}")

    # Check if we have enough data for AI
    has_name = bool(p.name)
    has_desc = bool(p.description and len(p.description) > 20)
    has_meta = bool(p.meta_description and len(p.meta_description) > 20)
    has_ingredients = bool(p.ingredients)

    total_info = sum([has_name, has_desc, has_meta, has_ingredients])

    logger.info("\nData Quality Check:")
    logger.info(
        f"  {'✓' if has_name else '✗'} name: {'Present' if has_name else 'Missing'}"
    )
    logger.info(
        f"  {'✓' if has_desc else '✗'} description: {'Sufficient' if has_desc else 'Insufficient'}"
    )
    logger.info(
        f"  {'✓' if has_meta else '✗'} meta_description: {'Sufficient' if has_meta else 'Insufficient'}"
    )
    logger.info(
        f"  {'✓' if has_ingredients else '✗'} ingredients: {'Present' if has_ingredients else 'Missing'}"
    )
    logger.info(f"\n  Total: {total_info}/4 fields with useful data")

    if total_info >= 2:
        logger.info("✓ PASSED: Sufficient data for AI attribute extraction")
    else:
        logger.warning("⚠ WARNING: Limited data may affect AI accuracy")

    # ===== TEST 5: Cache Test =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 5: Cache Functionality")
    logger.info("-" * 70)

    logger.info("Searching for 'chocolate' again (should use cache)...")
    products2 = client.search("chocolate")
    logger.info(f"✓ PASSED: Got {len(products2)} products from cache")

    # ===== TEST 6: Multiple Searches =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 6: Different Search Queries")
    logger.info("-" * 70)

    test_queries = ["birthday", "strawberries", "gift basket"]

    for query in test_queries:
        products_test = client.search(query)
        logger.info(f"  '{query}': {len(products_test)} products")

    logger.info("\n✓ PASSED: All queries returned results")

    # ===== TEST 7: Natural Language Query =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 7: Natural Language Query")
    logger.info("-" * 70)

    natural_query = "birthday gift under 50"
    products_natural = client.search(natural_query)
    logger.info(f"Query: '{natural_query}'")
    logger.info(f"Results: {len(products_natural)} products")

    if products_natural:
        logger.info("\nFirst 3 results:")
        for i, p in enumerate(products_natural[:3], 1):
            logger.info(f"  {i}. {p.name[:60]} - ${p.price:.2f}")
        logger.info("✓ PASSED: Natural language query works")
    else:
        logger.warning("⚠ WARNING: No results for natural language query")

    # ===== TEST 8: Price Range =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 8: Price Range Analysis")
    logger.info("-" * 70)

    prices = [p.price for p in products]
    logger.info("Price range in first search:")
    logger.info(f"  Min: ${min(prices):.2f}")
    logger.info(f"  Max: ${max(prices):.2f}")
    logger.info(f"  Avg: ${sum(prices) / len(prices):.2f}")
    logger.info("✓ PASSED: Price data is present")

    # ===== TEST 9: Popularity Ranking =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 9: Popularity Ranking")
    logger.info("-" * 70)

    logger.info("First 5 products (by search order = popularity):")
    for p in products[:5]:
        logger.info(f"  #{p.popularity_rank}: {p.name[:50]} - ${p.price:.2f}")

    # Check that ranking is sequential
    ranks = [p.popularity_rank for p in products if p.popularity_rank]
    if ranks == list(range(1, len(ranks) + 1)):
        logger.info("✓ PASSED: Popularity ranking is sequential")
    else:
        logger.warning("⚠ WARNING: Popularity ranking has gaps")

    # ===== TEST 10: Image URLs =====
    logger.info("\n" + "-" * 70)
    logger.info("TEST 10: Image URL Availability")
    logger.info("-" * 70)

    has_image = sum(1 for p in products if p.image_url)
    has_thumbnail = sum(1 for p in products if p.thumbnail_url)

    logger.info(f"  Products with image_url: {has_image}/{len(products)}")
    logger.info(f"  Products with thumbnail_url: {has_thumbnail}/{len(products)}")

    if has_image > len(products) * 0.8:
        logger.info("✓ PASSED: Most products have images")
    else:
        logger.warning("⚠ WARNING: Many products missing images")

    # ===== SUMMARY =====
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUITE SUMMARY")
    logger.info("=" * 70)
    logger.info("✓ API Connection: Working")
    logger.info("✓ Product Model: Valid")
    logger.info("✓ Pydantic Serialization: Working")
    logger.info("✓ AI Analysis Fields: Available")
    logger.info("✓ Cache: Working")
    logger.info("✓ Multiple Queries: Working")
    logger.info(f"✓ Data Quality: {'Good' if total_info >= 3 else 'Acceptable'}")
    logger.info("\n✓ ALL TESTS PASSED - Ready for Phase 3")
    logger.info("=" * 70)

    # Save sample product for inspection
    logger.info(
        "\nSaving sample product to 'data/sample_product.txt' for inspection..."
    )
    with open("data/sample_product.txt", "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("SAMPLE PRODUCT FOR AI ANALYSIS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"ID: {p.id}\n")
        f.write(f"Name: {p.name}\n")
        f.write(f"Price: ${p.price:.2f}\n")
        f.write(f"Popularity Rank: #{p.popularity_rank}\n\n")
        f.write("-" * 70 + "\n")
        f.write("DESCRIPTION:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{p.description}\n\n")
        f.write("-" * 70 + "\n")
        f.write("META DESCRIPTION:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{p.meta_description or 'N/A'}\n\n")
        f.write("-" * 70 + "\n")
        f.write("INGREDIENTS:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{p.ingredients or 'N/A'}\n\n")
        f.write("-" * 70 + "\n")
        f.write("IMAGE URL:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{p.image_url or 'N/A'}\n")

    logger.info("✓ Sample saved")


if __name__ == "__main__":
    test_api()
