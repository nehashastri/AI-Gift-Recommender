from typing import List, Tuple

from lib.types import GiftWizardState, Product


def calculate_best_match_score(
    product: Product, wizard_state: GiftWizardState
) -> Tuple[float, List[str]]:
    """
    Calculate how well product matches explicit preferences

    Returns:
        (score: 0-100, breakdown: list of scoring reasons)
    """
    score = 50  # Start neutral
    breakdown = []

    combined = f"{product.name} {product.description}".lower()

    # Count matched loves
    if wizard_state.recipient_loves:
        matched_loves = 0
        for loved in wizard_state.recipient_loves:
            if loved.lower() in combined:
                matched_loves += 1
                score += 15
                breakdown.append(f"+15: Contains {loved} (loved)")

        # Bonus for matching ALL loves
        if matched_loves == len(wizard_state.recipient_loves):
            score += 25
            breakdown.append("+25: Matches ALL preferences!")

        # Percentage bonus
        if matched_loves > 0:
            match_pct = (matched_loves / len(wizard_state.recipient_loves)) * 100
            breakdown.append(f"Matches {match_pct:.0f}% of preferences")

    return max(0, min(100, score)), breakdown


def calculate_unique_score(
    product: Product, wizard_state: GiftWizardState, all_products: List[Product]
) -> Tuple[float, List[str]]:
    """
    Calculate uniqueness/memorability score

    Returns:
        (score: 0-100, breakdown: list of scoring reasons)
    """
    score = 50  # Start neutral
    breakdown = []

    combined = f"{product.name} {product.description}".lower()

    # Unique/premium keywords
    unique_keywords = {
        "limited": 15,
        "exclusive": 15,
        "premium": 12,
        "artisan": 12,
        "handcrafted": 12,
        "luxury": 10,
        "gourmet": 10,
        "special edition": 15,
        "unique": 10,
        "rare": 10,
    }

    for keyword, points in unique_keywords.items():
        if keyword in combined:
            score += points
            breakdown.append(f"+{points}: Described as '{keyword}'")

    # Price premium indicator
    if all_products:
        avg_price = sum(p.price for p in all_products) / len(all_products)
        if product.price > avg_price * 1.5:
            score += 20
            breakdown.append("+20: Premium priced (1.5x average)")
        elif product.price > avg_price * 1.2:
            score += 10
            breakdown.append("+10: Above average price")

    # Health/fitness context (if in description)
    if wizard_state.recipient_description:
        desc_lower = wizard_state.recipient_description.lower()

        if any(
            word in desc_lower for word in ["health", "fit", "run", "active", "workout"]
        ):
            health_keywords = [
                "organic",
                "natural",
                "protein",
                "energy",
                "wellness",
                "recovery",
            ]
            for keyword in health_keywords:
                if keyword in combined:
                    score += 15
                    breakdown.append("+15: Health-focused (matches lifestyle)")
                    break

    return max(0, min(100, score)), breakdown
