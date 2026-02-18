import logging
import random
from typing import Callable, List, Optional, Tuple

from lib.ai_client import AIClient, cosine_similarity
from lib.types import GiftWizardState, Product

logger = logging.getLogger(__name__)


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


def select_unique_pick(
    path_b_safe: List[Product],
    path_b_similarity_scores: dict[str, float],
    wizard_state: GiftWizardState,
    all_products: List[Product],
    ai_safety_filter: Optional[
        Callable[[List[Product], GiftWizardState, str], List[Product]]
    ] = None,
) -> Optional[dict]:
    """
    Select unique pick from Path B products with comprehensive fallback logic

    Selection priority:
    1. Semantic similarity scores (from Path B)
    2. Default curated unique products (within budget, scored semantically by description/likes)

    Args:
        path_b_safe: Products from Path B that passed safety validation
        path_b_similarity_scores: Map of product.id -> similarity score
        wizard_state: Gift wizard state with recipient preferences
        all_products: All available products for price comparison (unused, kept for compatibility)
        ai_safety_filter: Optional callback for filtering default products

    Returns:
        Dict with keys: product, score, breakdown (or None if no unique found)
    """
    unique = None

    # === METHOD 1: Semantic Similarity (Primary) ===
    if path_b_safe and path_b_similarity_scores:
        scored_products = [p for p in path_b_safe if p.id in path_b_similarity_scores]

        if scored_products:
            best_product = max(
                scored_products, key=lambda p: path_b_similarity_scores[p.id]
            )
            similarity = path_b_similarity_scores[best_product.id]
            unique = {
                "product": best_product,
                "score": similarity * 100,  # Convert to 0-100 scale
                "breakdown": [
                    f"Semantic similarity: {similarity:.2f}",
                    "Matches recipient's lifestyle and personality",
                ],
            }

    # === METHOD 2: Default Curated Products (Fallback) ===
    if unique is None and ai_safety_filter is not None:
        logger.info(
            "[UNIQUE FALLBACK] Path B empty or no semantic matches, using default unique products..."
        )

        from lib.default_uniques import DefaultUniqueProducts

        default_manager = DefaultUniqueProducts()
        default_products = default_manager.get_default_products()

        logger.debug(
            f"[UNIQUE FALLBACK] Loaded {len(default_products)} default unique products"
        )

        if default_products:
            # Filter by budget if specified
            if (
                wizard_state.budget_max is not None
                or wizard_state.budget_min is not None
            ):
                before_count = len(default_products)
                if wizard_state.budget_min:
                    default_products = [
                        p
                        for p in default_products
                        if p.price >= wizard_state.budget_min
                    ]
                if wizard_state.budget_max:
                    default_products = [
                        p
                        for p in default_products
                        if p.price <= wizard_state.budget_max
                    ]

                logger.debug(
                    f"[UNIQUE FALLBACK] Budget filter: {before_count} → {len(default_products)} products"
                )

            if default_products:
                # Filter through AI safety check
                logger.info("[UNIQUE FALLBACK] Applying AI safety filter...")
                safe_defaults = ai_safety_filter(
                    default_products, wizard_state, "Default Uniques"
                )

                logger.info(
                    f"[UNIQUE FALLBACK] {len(default_products)} → {len(safe_defaults)} "
                    "products after safety filter"
                )

                if safe_defaults:
                    # Score each safe product semantically based on recipient profile
                    unique = _select_semantic_unique(safe_defaults, wizard_state)
                    if unique is None:
                        # Fallback to random if semantic scoring fails
                        logger.info(
                            "[UNIQUE FALLBACK] Semantic scoring inconclusive, using random selection"
                        )
                        selected_product = random.choice(safe_defaults)
                        unique = {
                            "product": selected_product,
                            "score": 60,  # Neutral score for default selection
                            "breakdown": ["Curated unique pick within budget"],
                        }
                        logger.info(
                            f"[UNIQUE FALLBACK] Randomly selected: {selected_product.name}"
                        )
                else:
                    logger.info(
                        "[UNIQUE FALLBACK] No default products passed safety filter. "
                        "Returning no unique pick."
                    )
            else:
                logger.info("[UNIQUE FALLBACK] No default products in budget range.")
        else:
            logger.warning("[UNIQUE FALLBACK] No default products available.")

    return unique


def _select_semantic_unique(
    products: List[Product], wizard_state: GiftWizardState
) -> Optional[dict]:
    """
    Score products semantically based on recipient profile and select the best match.

    Uses recipient description, likes, and hates to compute semantic similarity.
    Falls back to random if scores are too low.

    Args:
        products: List of products to score
        wizard_state: Gift wizard state with recipient preferences

    Returns:
        Dict with product, score, breakdown or None if scoring fails
    """
    if not products or not wizard_state.recipient_description:
        logger.debug(
            "[SEMANTIC UNIQUE] No description or products, skipping semantic scoring"
        )
        return None

    try:
        ai_client = AIClient()

        # Build contextual profile from recipient info
        profile_parts = []
        if wizard_state.recipient_description:
            profile_parts.append(f"Personality: {wizard_state.recipient_description}")
        if wizard_state.recipient_loves:
            loves = [l for l in wizard_state.recipient_loves if l.strip()]
            if loves:
                profile_parts.append(f"Loves: {', '.join(loves)}")
        if wizard_state.recipient_hates:
            hates = [h for h in wizard_state.recipient_hates if h.strip()]
            if hates:
                profile_parts.append(f"Hates: {', '.join(hates)}")

        recipient_profile = (
            "\n".join(profile_parts)
            if profile_parts
            else wizard_state.recipient_description
        )

        logger.debug(
            f"[SEMANTIC UNIQUE] Recipient profile: {recipient_profile[:100]}..."
        )

        # Get embedding of recipient profile
        profile_embedding = ai_client.get_embedding(recipient_profile)

        # Score each product
        scored_products = []
        for product in products:
            product_text = f"{product.name} {product.description}"
            product_embedding = ai_client.get_embedding(product_text)

            similarity = cosine_similarity(profile_embedding, product_embedding)
            scored_products.append((product, similarity))

            logger.debug(
                f"[SEMANTIC UNIQUE] {product.name[:45]:45} | Similarity: {similarity:.3f}"
            )

        # Find the best match (highest cosine similarity)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        best_product, best_similarity = scored_products[0]

        unique = {
            "product": best_product,
            "score": best_similarity * 100,
            "breakdown": [
                f"Semantic match: {best_similarity:.2f}",
                "Aligns with recipient's interests and personality",
            ],
        }
        logger.info(
            f"[SEMANTIC UNIQUE] Selected: {best_product.name} (similarity: {best_similarity:.3f})"
        )
        return unique

    except Exception as e:
        logger.error(f"[SEMANTIC UNIQUE] Error during semantic scoring: {e}")
        return None


def calculate_safe_bet_score(product: Product) -> Tuple[float, List[str]]:
    """
    Calculate safe bet score based on popularity/reliability indicators

    Safe bet prioritizes popularity and proven appeal over personalization.

    Returns:
        (score: 0-100, breakdown: list of scoring reasons)
    """
    breakdown = []

    # Primary indicator: popularity rank (lower is better)
    if product.popularity_rank is not None:
        # Convert rank to score: rank 1 = 100, rank 100+ = 0
        score = max(100 - product.popularity_rank, 0)
        breakdown.append(
            f"Popularity rank #{product.popularity_rank} (top-rated product)"
        )
    else:
        # No popularity data available
        score = 50
        breakdown.append("Selected from available options (no popularity ranking)")

    return score, breakdown
