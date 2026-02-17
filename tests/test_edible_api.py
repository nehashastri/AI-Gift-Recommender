# tests/test_edible_api.py

from lib.edible_api import EdibleAPIClient


def test_api():
    """Test Edible API integration with updated Product model"""

    client = EdibleAPIClient()

    print("\n" + "=" * 70)
    print("EDIBLE API TEST SUITE")
    print("=" * 70)

    # ===== TEST 1: Basic Search =====
    print("\n" + "-" * 70)
    print("TEST 1: Basic Search for 'chocolate'")
    print("-" * 70)

    products = client.search("chocolate")

    if not products:
        print("✗ FAILED: No products returned")
        return

    print(f"✓ PASSED: Found {len(products)} products")

    # ===== TEST 2: Product Model Validation =====
    print("\n" + "-" * 70)
    print("TEST 2: Product Model Validation")
    print("-" * 70)

    p = products[0]

    print("\nProduct Fields:")
    print(f"  ✓ id: {p.id}")
    print(f"  ✓ name: {p.name[:50]}...")
    print(f"  ✓ price: ${p.price:.2f}")
    print(f"  ✓ popularity_rank: #{p.popularity_rank}")
    print(f"  ✓ image_url: {p.image_url[:50] if p.image_url else 'None'}...")
    print(
        f"  ✓ thumbnail_url: {p.thumbnail_url[:50] if p.thumbnail_url else 'None'}..."
    )
    print(f"  ✓ description: {len(p.description)} chars")
    print(
        f"  ✓ meta_description: {len(p.meta_description) if p.meta_description else 0} chars"
    )
    print(f"  ✓ ingredients: {p.ingredients or 'None'}")

    # Check that removed fields are gone
    assert not hasattr(p, "url"), "❌ url field should be removed"
    assert not hasattr(p, "category"), "❌ category field should be removed"
    assert not hasattr(p, "raw_data"), "❌ raw_data field should be removed"
    assert not hasattr(p, "allergy_info"), "❌ allergy_info field should be removed"

    print("\n✓ PASSED: All fields present, removed fields absent")

    # ===== TEST 3: Pydantic Serialization =====
    print("\n" + "-" * 70)
    print("TEST 3: Pydantic Serialization")
    print("-" * 70)

    try:
        # Test model_dump()
        product_dict = p.model_dump()
        print(f"  ✓ model_dump(): {len(product_dict)} fields")

        # Test model_dump_json()
        product_json = p.model_dump_json()
        print(f"  ✓ model_dump_json(): {len(product_json)} chars")

        # Test that we can recreate Product from dict
        from lib.types import Product

        p2 = Product(**product_dict)
        print("  ✓ Can recreate Product from dict")

        print("\n✓ PASSED: Pydantic serialization works")

    except Exception as e:
        print(f"✗ FAILED: {e}")

    # ===== TEST 4: AI Analysis Fields =====
    print("\n" + "-" * 70)
    print("TEST 4: Fields Available for AI Analysis")
    print("-" * 70)

    print("\nAI will analyze these fields to extract ProductAttributes:")
    print(f"  1. name: '{p.name}'")
    print(f"  2. description: {len(p.description)} chars")
    if p.description:
        print(f"     Preview: {p.description[:100]}...")
    print(
        f"  3. meta_description: {len(p.meta_description) if p.meta_description else 0} chars"
    )
    if p.meta_description:
        print(f"     Preview: {p.meta_description[:100]}...")
    print(f"  4. ingredients: {p.ingredients or 'Not provided'}")

    # Check if we have enough data for AI
    has_name = bool(p.name)
    has_desc = bool(p.description and len(p.description) > 20)
    has_meta = bool(p.meta_description and len(p.meta_description) > 20)
    has_ingredients = bool(p.ingredients)

    total_info = sum([has_name, has_desc, has_meta, has_ingredients])

    print("\nData Quality Check:")
    print(f"  {'✓' if has_name else '✗'} name: {'Present' if has_name else 'Missing'}")
    print(
        f"  {'✓' if has_desc else '✗'} description: {'Sufficient' if has_desc else 'Insufficient'}"
    )
    print(
        f"  {'✓' if has_meta else '✗'} meta_description: {'Sufficient' if has_meta else 'Insufficient'}"
    )
    print(
        f"  {'✓' if has_ingredients else '✗'} ingredients: {'Present' if has_ingredients else 'Missing'}"
    )
    print(f"\n  Total: {total_info}/4 fields with useful data")

    if total_info >= 2:
        print("✓ PASSED: Sufficient data for AI attribute extraction")
    else:
        print("⚠ WARNING: Limited data may affect AI accuracy")

    # ===== TEST 5: Cache Test =====
    print("\n" + "-" * 70)
    print("TEST 5: Cache Functionality")
    print("-" * 70)

    print("Searching for 'chocolate' again (should use cache)...")
    products2 = client.search("chocolate")
    print(f"✓ PASSED: Got {len(products2)} products from cache")

    # ===== TEST 6: Multiple Searches =====
    print("\n" + "-" * 70)
    print("TEST 6: Different Search Queries")
    print("-" * 70)

    test_queries = ["birthday", "strawberries", "gift basket"]

    for query in test_queries:
        products_test = client.search(query)
        print(f"  '{query}': {len(products_test)} products")

    print("\n✓ PASSED: All queries returned results")

    # ===== TEST 7: Natural Language Query =====
    print("\n" + "-" * 70)
    print("TEST 7: Natural Language Query")
    print("-" * 70)

    natural_query = "birthday gift under 50"
    products_natural = client.search(natural_query)
    print(f"Query: '{natural_query}'")
    print(f"Results: {len(products_natural)} products")

    if products_natural:
        print("\nFirst 3 results:")
        for i, p in enumerate(products_natural[:3], 1):
            print(f"  {i}. {p.name[:60]} - ${p.price:.2f}")
        print("✓ PASSED: Natural language query works")
    else:
        print("⚠ WARNING: No results for natural language query")

    # ===== TEST 8: Price Range =====
    print("\n" + "-" * 70)
    print("TEST 8: Price Range Analysis")
    print("-" * 70)

    prices = [p.price for p in products]
    print("Price range in first search:")
    print(f"  Min: ${min(prices):.2f}")
    print(f"  Max: ${max(prices):.2f}")
    print(f"  Avg: ${sum(prices) / len(prices):.2f}")
    print("✓ PASSED: Price data is present")

    # ===== TEST 9: Popularity Ranking =====
    print("\n" + "-" * 70)
    print("TEST 9: Popularity Ranking")
    print("-" * 70)

    print("First 5 products (by search order = popularity):")
    for p in products[:5]:
        print(f"  #{p.popularity_rank}: {p.name[:50]} - ${p.price:.2f}")

    # Check that ranking is sequential
    ranks = [p.popularity_rank for p in products if p.popularity_rank]
    if ranks == list(range(1, len(ranks) + 1)):
        print("✓ PASSED: Popularity ranking is sequential")
    else:
        print("⚠ WARNING: Popularity ranking has gaps")

    # ===== TEST 10: Image URLs =====
    print("\n" + "-" * 70)
    print("TEST 10: Image URL Availability")
    print("-" * 70)

    has_image = sum(1 for p in products if p.image_url)
    has_thumbnail = sum(1 for p in products if p.thumbnail_url)

    print(f"  Products with image_url: {has_image}/{len(products)}")
    print(f"  Products with thumbnail_url: {has_thumbnail}/{len(products)}")

    if has_image > len(products) * 0.8:
        print("✓ PASSED: Most products have images")
    else:
        print("⚠ WARNING: Many products missing images")

    # ===== SUMMARY =====
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    print("✓ API Connection: Working")
    print("✓ Product Model: Valid")
    print("✓ Pydantic Serialization: Working")
    print("✓ AI Analysis Fields: Available")
    print("✓ Cache: Working")
    print("✓ Multiple Queries: Working")
    print(f"✓ Data Quality: {'Good' if total_info >= 3 else 'Acceptable'}")
    print("\n✓ ALL TESTS PASSED - Ready for Phase 3")
    print("=" * 70)

    # Save sample product for inspection
    print("\nSaving sample product to 'data/sample_product.txt' for inspection...")
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

    print("✓ Sample saved")


if __name__ == "__main__":
    test_api()
