import json
import logging
from typing import List

from lib.ai_client import AIClient, cosine_similarity
from lib.edible_api import EdibleAPIClient
from lib.types import (
    GiftWizardState,
    Product,
    Recommendation,
    SafetyValidationResponse,
    ThreePickRecommendations,
)

logger = logging.getLogger(__name__)


class GiftRecommender:
    """Main recommendation engine"""

    def __init__(self):
        self.edible_client = EdibleAPIClient()
        self.ai_client = AIClient()

    def get_recommendations(
        self, wizard_state: GiftWizardState
    ) -> ThreePickRecommendations:
        """
        Main entry point for recommendations

        Pipeline:
        1. Fetch products from Edible API
        2. Path A: Pre-filter by explicit preferences
        3. Path B: Semantic filter for unique picks
        4. AI safety validation (both paths)
        5. Select best match, safe bet, unique
        6. Generate explanations
        """

        logger.info("\n" + "=" * 50)
        logger.info("STARTING RECOMMENDATION PIPELINE")
        logger.info("=" * 50)
        logger.info(f"[INPUT] Occasion: {wizard_state.occasion}")
        logger.info(f"[INPUT] Budget: {wizard_state.budget} (legacy)")
        logger.info(
            f"[INPUT] Budget Min: ${wizard_state.budget_min}"
            if wizard_state.budget_min
            else "[INPUT] Budget Min: None"
        )
        logger.info(
            f"[INPUT] Budget Max: ${wizard_state.budget_max}"
            if wizard_state.budget_max
            else "[INPUT] Budget Max: None"
        )
        logger.info(f"[INPUT] Recipient: {wizard_state.recipient_name}")
        logger.info(f"[INPUT] Loves: {wizard_state.recipient_loves}")
        logger.info(f"[INPUT] Hates: {wizard_state.recipient_hates}")
        logger.info(f"[INPUT] Allergies: {wizard_state.recipient_allergies}")
        logger.info(f"[INPUT] Dietary: {wizard_state.recipient_dietary}")
        logger.info(f"[INPUT] Description: {wizard_state.recipient_description}")

        # === STEP 1: FETCH PRODUCTS ===
        logger.info("\n[Step 1] Fetching products from Edible API...")
        all_products = self._fetch_products(wizard_state)
        logger.info(f"Fetched {len(all_products)} products")

        if len(all_products) < 5:
            raise Exception(
                f"Not enough products found ({len(all_products)}). Try broader search."
            )

        # === STEP 2: PATH A - EXPLICIT PREFERENCE FILTERING ===
        logger.info("\n[Step 2] Path A: Filtering by explicit preferences...")
        path_a_products = self._prefilter_explicit(all_products, wizard_state)
        logger.info(f"Path A: {len(all_products)} → {len(path_a_products)} products")

        # === STEP 3: PATH B - SEMANTIC UNIQUE FILTERING ===
        logger.info("\n[Step 3] Path B: Semantic filtering for unique picks...")
        path_b_products, path_b_similarity_scores = self._prefilter_semantic(
            all_products, wizard_state
        )
        logger.info(f"Path B: {len(all_products)} → {len(path_b_products)} products")

        # === STEP 4: AI SAFETY VALIDATION ===
        logger.info("\n[Step 4] AI Safety Validation...")
        path_a_safe = self._ai_safety_filter(path_a_products, wizard_state, "Path A")
        path_b_safe = self._ai_safety_filter(path_b_products, wizard_state, "Path B")

        logger.info(f"Path A safe: {len(path_a_safe)} products")
        logger.info(f"Path B safe: {len(path_b_safe)} products")

        if len(path_a_safe) < 2:
            raise Exception("Not enough safe products in Path A after safety filter")

        # === STEP 5: SELECTION ===
        logger.info("\n[Step 5] Selecting top 3 picks...")
        picks = self._select_three_picks(
            path_a_safe, path_b_safe, wizard_state, path_b_similarity_scores
        )

        # === STEP 6: GENERATE EXPLANATIONS ===
        logger.info("\n[Step 6] Generating explanations...")
        picks = self._add_explanations(picks, wizard_state)

        logger.info("\n" + "=" * 50)
        logger.info("RECOMMENDATION PIPELINE COMPLETE")
        logger.info("=" * 50 + "\n")

        return picks

    def _fetch_products(self, wizard_state: GiftWizardState) -> List[Product]:
        """Fetch products from Edible API based on occasion and budget"""

        # Build search keyword
        parts = []

        if wizard_state.occasion:
            parts.append(wizard_state.occasion)

        if wizard_state.recipient_loves:
            loves = [
                item.strip() for item in wizard_state.recipient_loves if item.strip()
            ]
            if loves:
                parts.append(", ".join(loves))
                logger.debug(f"[SEARCH] Including recipient loves: {loves}")

        # Don't include budget in search term - it's just a filter
        keyword = " ".join(parts).strip()

        logger.debug(f"\n{'=' * 60}")
        logger.debug(f"[SEARCH] Final search keyword: '{keyword}'")
        logger.debug(f"{'=' * 60}\n")

        products = self.edible_client.search(keyword)

        logger.debug(f"\n[API FETCH] Received {len(products)} products from API")

        # Display products in table format
        if products:
            self._display_products_table(products, "ALL PRODUCTS FROM API")

        # Filter by budget if specified (using structured fields - NO BUFFERS)
        if wizard_state.budget_max is not None or wizard_state.budget_min is not None:
            before_count = len(products)

            logger.debug("\n[BUDGET FILTER] Applying STRICT filtering:")
            if wizard_state.budget_min:
                logger.debug(f"  Min: ${wizard_state.budget_min}")
            if wizard_state.budget_max:
                logger.debug(f"  Max: ${wizard_state.budget_max}")
            if wizard_state.budget_min:
                products = [p for p in products if p.price >= wizard_state.budget_min]
            if wizard_state.budget_max:
                products = [p for p in products if p.price <= wizard_state.budget_max]

            after_count = len(products)
            logger.debug(
                f"[BUDGET FILTER] Filtered: {before_count} \u2192 {after_count} products"
            )

            if products:
                self._display_products_table(products, "AFTER BUDGET FILTERING")
        else:
            logger.debug("[BUDGET FILTER] No budget constraints, keeping all products")

        return products

    def _display_products_table(self, products: List[Product], title: str = "PRODUCTS"):
        """Display products in a readable table format for debugging"""
        logger.debug(f"\n{'=' * 80}")
        logger.debug(f" {title} ")
        logger.debug(f"{'=' * 80}")
        logger.debug(f"{'#':<4} {'NAME':<40} {'PRICE':<10} {'ID':<10}")
        logger.debug(f"{'-' * 80}")

        for idx, product in enumerate(products[:20], 1):  # Show first 20
            name = product.name[:38] + ".." if len(product.name) > 40 else product.name
            logger.debug(f"{idx:<4} {name:<40} ${product.price:<9.2f} {product.id:<10}")

        if len(products) > 20:
            logger.debug(f"... and {len(products) - 20} more products")

        logger.debug(f"{'=' * 80}\n")

    def _prefilter_explicit(
        self, products: List[Product], wizard_state: GiftWizardState
    ) -> List[Product]:
        """
        PATH A: Keep products that mention at least one explicitly loved item
        Used for Best Match and Safe Bet picks
        """
        logger.debug("\n[PATH A - EXPLICIT FILTER]")
        logger.debug(f"Recipient loves: {wizard_state.recipient_loves}")

        if not wizard_state.recipient_loves:
            # If no preferences, return all products
            logger.debug("No explicit loves specified, returning all products")
            return products

        filtered = []

        for product in products:
            combined = f"{product.name} {product.description} {product.meta_description}".lower()

            # Check if ANY loved item is mentioned
            matched_loves = []
            for loved in wizard_state.recipient_loves:
                if loved.lower() in combined:
                    matched_loves.append(loved)

            if matched_loves:
                filtered.append(product)
                logger.debug(
                    f"✓ {product.name[:50]:50} | Matches: {', '.join(matched_loves)}"
                )

        logger.debug(f"[PATH A] Result: {len(filtered)} products match explicit loves")
        return filtered

    def _prefilter_semantic(
        self, products: List[Product], wizard_state: GiftWizardState
    ) -> tuple[List[Product], dict[str, float]]:
        """
        PATH B: Semantic matching for unique picks
        - Match persona description semantically
        - EXCLUDE products that mention explicit loves/hates

        Returns:
            (products, similarity_scores) where similarity_scores is a dict mapping product.id -> similarity score
        """
        logger.debug("\n[PATH B - SEMANTIC FILTER]")
        logger.debug(f"Recipient description: {wizard_state.recipient_description}")
        logger.debug(f"Excluding explicit loves: {wizard_state.recipient_loves}")
        logger.debug(f"Excluding explicit hates: {wizard_state.recipient_hates}")

        if not wizard_state.recipient_description:
            logger.debug("No description provided, returning empty semantic results")
            return [], {}

        # Get embedding of persona description
        description_embedding = self.ai_client.get_embedding(
            wizard_state.recipient_description
        )

        candidates = []

        for product in products:
            combined = f"{product.name} {product.description}".lower()

            # EXCLUDE if mentions explicit preferences
            mentions_explicit = False
            excluded_by = None

            for loved in wizard_state.recipient_loves:
                if loved.lower() in combined:
                    mentions_explicit = True
                    excluded_by = f"love: {loved}"
                    break

            if not mentions_explicit:
                for hated in wizard_state.recipient_hates or []:
                    if hated.lower() in combined:
                        mentions_explicit = True
                        excluded_by = f"hate: {hated}"
                        break

            if mentions_explicit:
                logger.debug(f"✗ {product.name[:45]:45} | Excluded by {excluded_by}")
                continue  # Skip, belongs in Path A

            # Calculate semantic similarity
            product_text = f"{product.name} {product.description}"
            product_embedding = self.ai_client.get_embedding(product_text)

            similarity = cosine_similarity(description_embedding, product_embedding)

            # Keep if semantically relevant
            if similarity > 0.8:
                candidates.append((product, similarity))
                logger.debug(f"✓ {product.name[:45]:45} | Similarity: {similarity:.3f}")

        # Sort by similarity and take top 3
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates[:3]

        top_products = [p for p, _ in top_candidates]
        similarity_scores = {p.id: sim for p, sim in top_candidates}

        logger.debug(
            f"[PATH B] Result: {len(top_products)} products with high semantic similarity"
        )
        return top_products, similarity_scores

    def _ai_safety_filter(
        self, products: List[Product], wizard_state: GiftWizardState, source_path: str
    ) -> List[Product]:
        """
        Use AI to identify products that should be rejected
        based on hates and allergies
        """
        logger.debug(f"\n[{source_path} - AI SAFETY FILTER]")
        logger.debug("Checking against:")
        logger.debug(f"  Hates: {wizard_state.recipient_hates}")
        logger.debug(f"  Allergies: {wizard_state.recipient_allergies}")
        logger.debug(f"  Dietary: {wizard_state.recipient_dietary}")

        if not products:
            logger.debug("No products to filter")
            return []

        if not wizard_state.recipient_hates and not wizard_state.recipient_allergies:
            # No restrictions, all products are safe
            logger.debug("No restrictions specified, all products are safe")
            return products

        hates = wizard_state.recipient_hates or []
        allergies = wizard_state.recipient_allergies or []
        dietary = wizard_state.recipient_dietary or []

        # Build prompt
        prompt = f"""You are a safety validator for a gift recommendation system.
Identify products that should be REJECTED based on the recipient's restrictions.

RECIPIENT RESTRICTIONS:
        - HATES: {", ".join(hates) if hates else "nothing specified"}
        - ALLERGIES: {", ".join(allergies) if allergies else "none"}
        - DIETARY: {", ".join(dietary) if dietary else "none"}

PRODUCTS TO VALIDATE (from {source_path}):
{
            json.dumps(
                [
                    {
                        "product_id": p.id,
                        "name": p.name,
                        "description": p.description[:150],
                    }
                    for p in products
                ],
                indent=2,
            )
        }

For each product, determine if it should be REJECTED.

REJECTION CRITERIA:
1. Contains hated items (exact or obvious variants)
   - If hates "nuts", reject products with almonds/peanuts/cashews
   - BUT: "nut-free" should NOT be rejected (negation)

2. Contains allergens (be very careful)
   - Look for explicit mentions AND hidden sources
   - Example: dairy allergy → reject "cream", "butter", "milk chocolate"

3. Violates dietary restrictions
   - Vegan → reject dairy, eggs, honey
   - Gluten-free → reject wheat, flour

IMPORTANT:
- Be conservative (when in doubt, don't reject)
- Understand negation: "nut-free" is SAFE for nut allergies
- Only reject if confident
- Provide clear reasoning

Return ONLY a JSON object:
{{
  "validations": [
    {{"product_id": "product_id", "reject": true/false, "reason": "explanation or null"}}
  ]
}}
"""

        try:
            response = self.ai_client.chat_completion_json(
                [{"role": "user", "content": prompt}]
            )

            validation_response = SafetyValidationResponse(**response)

            # Filter out rejected products
            safe_products = []
            rejected_count = 0
            for product in products:
                validation = next(
                    (
                        v
                        for v in validation_response.validations
                        if v.product_id == product.id
                    ),
                    None,
                )

                if not validation or not validation.reject:
                    safe_products.append(product)
                else:
                    rejected_count += 1
                    logger.debug(
                        f"  ✗ REJECTED: {product.name[:50]} - {validation.reason}"
                    )

            logger.debug(
                f"[{source_path} SAFETY] {len(safe_products)} safe, {rejected_count} rejected"
            )
            return safe_products

        except Exception as e:
            logger.error(f"AI Safety Filter Error: {e}")
            # Fallback: use simple keyword matching
            return self._fallback_safety_filter(products, wizard_state)

    def _fallback_safety_filter(
        self, products: List[Product], wizard_state: GiftWizardState
    ) -> List[Product]:
        """Fallback safety filter using keyword matching"""
        safe_products = []

        hates = wizard_state.recipient_hates or []
        allergies = wizard_state.recipient_allergies or []

        for product in products:
            combined = f"{product.name} {product.description}".lower()

            # Check for hated items
            has_hated = any(
                hated.lower() in combined and "free" not in combined for hated in hates
            )

            # Check for allergens
            has_allergen = any(
                allergen.lower() in combined and "free" not in combined
                for allergen in allergies
            )

            if not has_hated and not has_allergen:
                safe_products.append(product)

        return safe_products

    # Add these methods to the GiftRecommender class

    def _select_three_picks(
        self,
        path_a_safe: List[Product],
        path_b_safe: List[Product],
        wizard_state: GiftWizardState,
        path_b_similarity_scores: dict[str, float],
    ) -> ThreePickRecommendations:
        """
        Select best match, safe bet, and unique from filtered pools
        """
        from lib.scorer import (
            calculate_best_match_score,
            calculate_unique_score,
        )

        # === BEST MATCH (from Path A) ===
        best_match_scores = []
        for product in path_a_safe:
            score, breakdown = calculate_best_match_score(product, wizard_state)
            best_match_scores.append(
                {"product": product, "score": score, "breakdown": breakdown}
            )

        best_match = max(best_match_scores, key=lambda x: x["score"])

        # === SAFE BET (from Path A, exclude best match) ===
        remaining_a = [p for p in path_a_safe if p.id != best_match["product"].id]

        # BULLETPROOF OCCASION FILTERING: Remove products with incompatible occasions
        # Filter out products that mention distinct occasions different from the user's occasion
        if wizard_state.occasion:
            remaining_a = self._filter_by_occasion(remaining_a, wizard_state.occasion)

        # Select product with lowest popularity_rank (most popular)
        products_with_rank = [p for p in remaining_a if p.popularity_rank is not None]

        if products_with_rank:
            safe_bet_product = min(
                products_with_rank, key=lambda p: p.popularity_rank or 999
            )
            safe_bet = {
                "product": safe_bet_product,
                "score": max(100 - safe_bet_product.popularity_rank, 0)
                if safe_bet_product.popularity_rank
                else 50,
                "breakdown": [
                    f"Most popular choice (popularity rank #{safe_bet_product.popularity_rank})"
                ],
            }
        elif remaining_a:
            # Fallback to first product if no popularity ranks available
            safe_bet = {
                "product": remaining_a[0],
                "score": 50,
                "breakdown": [
                    "Selected from available options (no popularity ranking)"
                ],
            }
        else:
            # Fallback to best match if no other products
            safe_bet = best_match

        # === UNIQUE (from Path B) ===
        unique = None
        if path_b_safe:
            # Use semantic similarity scores if available (primary method)
            if path_b_similarity_scores:
                # Filter to products that are in path_b_safe and have similarity scores
                scored_products = [
                    p for p in path_b_safe if p.id in path_b_similarity_scores
                ]

                if scored_products:
                    # Use the product with highest semantic similarity
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

            # Fallback to keyword-based scoring if no similarity scores available
            if unique is None:
                unique_scores = []
                for product in path_b_safe:
                    score, breakdown = calculate_unique_score(
                        product, wizard_state, path_a_safe + path_b_safe
                    )
                    unique_scores.append(
                        {"product": product, "score": score, "breakdown": breakdown}
                    )

                unique = max(unique_scores, key=lambda x: x["score"])
        else:
            # Fallback: pick a "unique" option from remaining Path A items
            remaining_for_unique = [
                p
                for p in path_a_safe
                if p.id not in {best_match["product"].id, safe_bet["product"].id}
            ]
            if remaining_for_unique:
                unique_scores = []
                for product in remaining_for_unique:
                    score, breakdown = calculate_unique_score(
                        product, wizard_state, path_a_safe + path_b_safe
                    )
                    breakdown.append(
                        "Fallback: no description for semantic match; selected from remaining options"
                    )
                    unique_scores.append(
                        {"product": product, "score": score, "breakdown": breakdown}
                    )

                unique = max(unique_scores, key=lambda x: x["score"])
            else:
                # Final fallback: reuse safe bet if there is no remaining distinct option
                unique = safe_bet

        # Build recommendations
        return ThreePickRecommendations(
            best_match=Recommendation(
                product=best_match["product"],
                score=best_match["score"],
                category="best_match",
                explanation="",  # Will be filled by AI
                score_breakdown=best_match["breakdown"],
            ),
            safe_bet=Recommendation(
                product=safe_bet["product"],
                score=safe_bet["score"],
                category="safe_bet",
                explanation="",
                score_breakdown=safe_bet["breakdown"],
            ),
            unique=Recommendation(
                product=unique["product"],
                score=unique["score"],
                category="unique",
                explanation="",
                score_breakdown=unique["breakdown"],
            )
            if unique
            else None,
        )

    def _filter_by_occasion(
        self, products: List[Product], user_occasion: str
    ) -> List[Product]:
        """Use API occasion tags for authoritative filtering."""
        user_occasion_lower = user_occasion.lower().strip()
        search_terms = [user_occasion_lower, f"{user_occasion_lower} gifts"]

        logger.debug(f"[OCCASION] Filtering {len(products)} for '{user_occasion}'")
        logger.debug(f"[OCCASION] Search terms: {search_terms}")
        filtered = []
        for product in products:
            product_occasions = [o.lower() for o in product.occasions]
            logger.debug(
                f"[OCCASION] {product.name[:40]:40} | Raw occasions: {product.occasions} | Lowercase: {product_occasions}"
            )
            matches = any(
                term in occ for term in search_terms for occ in product_occasions
            )
            if matches:
                logger.debug(f"✓ MATCH: {product.name[:40]:40} | {product_occasions}")
                filtered.append(product)
            else:
                logger.debug(f"✗ SKIP: {product.name[:40]:40} | {product_occasions}")

        logger.info(
            f"[OCCASION] Result: {len(filtered)}/{len(products)} match '{user_occasion}'"
        )

        if filtered:
            return filtered
        else:
            logger.warning(
                f"[OCCASION] No matches. Using all {len(products)} as fallback."
            )
            return products

    def _add_explanations(
        self, picks: ThreePickRecommendations, wizard_state: GiftWizardState
    ) -> ThreePickRecommendations:
        """Generate AI explanations for each pick"""

        # Best Match
        picks.best_match.explanation = self._generate_explanation(
            picks.best_match, wizard_state, "best_match"
        )

        # Safe Bet
        picks.safe_bet.explanation = self._generate_explanation(
            picks.safe_bet, wizard_state, "safe_bet"
        )

        # Unique
        if picks.unique:
            picks.unique.explanation = self._generate_explanation(
                picks.unique, wizard_state, "unique"
            )

        return picks

    def _generate_explanation(
        self,
        recommendation: Recommendation,
        wizard_state: GiftWizardState,
        category: str,
    ) -> str:
        """Generate grounded explanation for a recommendation"""

        recipient_name = wizard_state.recipient_name or "them"

        category_context = {
            "best_match": f"This is the BEST MATCH because it aligns with {recipient_name}'s explicit preferences.",
            "safe_bet": f"This is a SAFE BET - a popular, well-reviewed choice that {recipient_name} will likely enjoy.",
            "unique": f"This is SOMETHING UNIQUE - a creative choice based on {recipient_name}'s lifestyle and personality.",
        }

        prompt = f"""You are explaining why a product was recommended as a gift.

    CATEGORY: {category_context[category]}

    PRODUCT:
    - Name: {recommendation.product.name}
    - Price: ${recommendation.product.price}
    - Description: {recommendation.product.description[:200]}

    RECIPIENT ({recipient_name}):
    - Loves: {", ".join(wizard_state.recipient_loves) if wizard_state.recipient_loves else "not specified"}
    - Hates: {", ".join(wizard_state.recipient_hates) if wizard_state.recipient_hates else "not specified"}
    - Description: {wizard_state.recipient_description or "not provided"}

    SCORING BREAKDOWN:
    {chr(10).join(recommendation.score_breakdown)}

    FINAL SCORE: {recommendation.score:.0f}/100

    Write a natural, friendly 2-3 sentence explanation of why this product is a great {category.replace("_", " ")}.

    Rules:
    1. ONLY mention details that appear in the product description
    2. Reference specific items from their loves/hates if relevant
    3. Keep it concise and conversational
    4. Use {recipient_name}'s name
    5. Don't mention the score explicitly

    Example for best match:
    "This is perfect for {recipient_name} who loves chocolate and strawberries! These chocolate-dipped strawberries combine both of their favorite treats. At $45, it's also well within your budget."

    Generate explanation:"""

        try:
            explanation = self.ai_client.chat_completion(
                [{"role": "user", "content": prompt}], temperature=0.7
            )

            return explanation.strip()

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            # Fallback to template
            return self._template_explanation(recommendation, wizard_state, category)

    def _template_explanation(
        self,
        recommendation: Recommendation,
        wizard_state: GiftWizardState,
        category: str,
    ) -> str:
        """Fallback template explanation"""
        recipient_name = wizard_state.recipient_name or "them"

        if category == "best_match":
            return f"This {recommendation.product.name} is a great match for {recipient_name}'s preferences!"
        elif category == "safe_bet":
            return f"This {recommendation.product.name} is a reliable choice that's popular with many customers."
        else:
            return f"This {recommendation.product.name} is a unique option we think {recipient_name} will love!"
