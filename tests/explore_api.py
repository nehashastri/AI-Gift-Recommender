import json

import requests


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
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }

    print(f"Searching for: {keyword}")
    print(f"URL: {url}")
    print(f"Payload: {payload}\n")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print(f"Status Code: {response.status_code}\n")

        if response.status_code == 200:
            # Get the JSON
            data = response.json()

            # Pretty print it so we can see the structure
            print("="*60)
            print("FULL RESPONSE:")
            print("="*60)
            print(json.dumps(data, indent=2))

            # Let's explore the structure
            print("\n" + "="*60)
            print("STRUCTURE ANALYSIS:")
            print("="*60)

            print(f"Top-level keys: {list(data.keys())}")

            # Try to find where the products are
            for key, value in data.items():
                print(f"\n{key}: {type(value)}")
                if isinstance(value, list) and len(value) > 0:
                    print(f"  → List with {len(value)} items")
                    print(f"  → First item type: {type(value[0])}")
                    if isinstance(value[0], dict):
                        print(f"  → First item keys: {list(value[0].keys())}")

            # Try to print first product
            print("\n" + "="*60)
            print("FIRST PRODUCT (if found):")
            print("="*60)

            # Common places products might be:
            possible_keys = ['products', 'items', 'results', 'data']
            products = None

            for key in possible_keys:
                if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                    products = data[key]
                    print(f"Found products at: data['{key}']")
                    break

            if products:
                print(json.dumps(products[0], indent=2))
            else:
                print("Couldn't automatically find products. Check the FULL RESPONSE above.")

        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_edible_api()
