"""Test suite for Pydantic models in lib/types.py"""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from lib.types import (
    GiftWizardState,
    Persona,
    Product,
    ProductAttributes,
    ProductScore,
    Recommendation,
    SafetyValidation,
    SafetyValidationResponse,
    ThreePickRecommendations,
)


class TestProduct:
    """Test Product model"""

    def test_instantiate_with_required_fields(self):
        """Can instantiate with only required fields"""
        product = Product(
            id="1",
            name="Chocolate Box",
            description="Nice chocolate",
            price=25.0,
        )
        assert product.id == "1"
        assert product.name == "Chocolate Box"
        assert product.price == 25.0

    def test_instantiate_with_all_fields(self):
        """Can instantiate with all fields"""
        product = Product(
            id="1",
            name="Chocolate Box",
            description="Nice chocolate",
            price=25.0,
            image_url="http://example.com/image.jpg",
            rating=4.5,
            review_count=100,
            category="dessert",
            raw_data={"source": "edible_api"},
        )
        assert product.image_url == "http://example.com/image.jpg"
        assert product.rating == 4.5

    def test_optional_fields_have_defaults(self):
        """Optional fields have proper defaults"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        assert product.image_url is None
        assert product.rating is None
        assert product.review_count is None
        assert product.category is None
        assert product.raw_data is None

    def test_validation_invalid_price(self):
        """Validation should fail for invalid price type"""
        with pytest.raises(ValidationError):
            Product(
                id="1",
                name="Box",
                description="Desc",
                price="not_a_number",  # type: ignore
            )

    def test_validation_missing_required_field(self):
        """Validation should fail for missing required fields"""
        with pytest.raises(ValidationError):
            Product(id="1", name="Box", price=25.0)  # type: ignore

    def test_json_serialization(self):
        """Can serialize to JSON"""
        product = Product(
            id="1",
            name="Chocolate Box",
            description="Nice",
            price=25.0,
            rating=4.5,
        )
        json_str = product.model_dump_json()
        data = json.loads(json_str)
        assert data["id"] == "1"
        assert data["name"] == "Chocolate Box"
        assert data["rating"] == 4.5

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = (
            '{"id":"1","name":"Box","description":"Desc","price":25.0,"rating":4.5}'
        )
        product = Product.model_validate_json(json_str)
        assert product.id == "1"
        assert product.price == 25.0
        assert product.rating == 4.5


class TestProductAttributes:
    """Test ProductAttributes model"""

    def test_instantiate_minimal(self):
        """Can instantiate with minimal fields"""
        attrs = ProductAttributes(product_id="1")
        assert attrs.product_id == "1"

    def test_default_list_fields(self):
        """List fields have empty list defaults"""
        attrs = ProductAttributes(product_id="1")
        assert attrs.ingredients == []
        assert attrs.fruit_types == []
        assert attrs.dietary_labels == []

    def test_default_values(self):
        """Default values are correct"""
        attrs = ProductAttributes(product_id="1")
        assert attrs.contains_nuts is False
        assert attrs.chocolate_type is None
        assert attrs.category == "other"

    def test_instantiate_with_all_fields(self):
        """Can instantiate with all fields"""
        attrs = ProductAttributes(
            product_id="1",
            ingredients=["cocoa", "sugar"],
            chocolate_type="dark",
            contains_nuts=True,
            fruit_types=["raspberry"],
            dietary_labels=["vegan"],
            category="chocolate_dipped",
        )
        assert attrs.ingredients == ["cocoa", "sugar"]
        assert attrs.chocolate_type == "dark"
        assert attrs.contains_nuts is True

    def test_validation_invalid_chocolate_type(self):
        """Validation fails for invalid chocolate_type"""
        with pytest.raises(ValidationError):
            ProductAttributes(
                product_id="1",
                chocolate_type="pink",  # type: ignore
            )

    def test_validation_invalid_category(self):
        """Validation fails for invalid category"""
        with pytest.raises(ValidationError):
            ProductAttributes(product_id="1", category="invalid")  # type: ignore

    def test_json_serialization(self):
        """Can serialize to JSON"""
        attrs = ProductAttributes(
            product_id="1",
            chocolate_type="dark",
            contains_nuts=True,
            dietary_labels=["vegan"],
        )
        json_str = attrs.model_dump_json()
        data = json.loads(json_str)
        assert data["product_id"] == "1"
        assert data["chocolate_type"] == "dark"
        assert data["contains_nuts"] is True

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = '{"product_id":"1","chocolate_type":"dark","contains_nuts":true,"category":"chocolate_dipped"}'
        attrs = ProductAttributes.model_validate_json(json_str)
        assert attrs.product_id == "1"
        assert attrs.chocolate_type == "dark"


class TestPersona:
    """Test Persona model"""

    def test_instantiate_minimal(self):
        """Can instantiate with minimal fields"""
        persona = Persona(user_id="user1", name="John")
        assert persona.user_id == "user1"
        assert persona.name == "John"

    def test_default_values(self):
        """Default values are correct"""
        persona = Persona(user_id="user1", name="John")
        assert persona.id is None
        assert persona.birthday is None
        assert persona.description is None
        assert persona.loves == []
        assert persona.hates == []
        assert persona.allergies == []
        assert persona.dietary_restrictions == []
        assert persona.email_reminders is True
        assert isinstance(persona.created_at, datetime)
        assert isinstance(persona.updated_at, datetime)

    def test_instantiate_with_all_fields(self):
        """Can instantiate with all fields"""
        now = datetime.now()
        persona = Persona(
            id="p1",
            user_id="user1",
            name="John",
            birthday=datetime(1990, 5, 15),
            loves=["chocolate", "fruit"],
            hates=["nuts"],
            allergies=["peanuts"],
            dietary_restrictions=["vegan"],
            description="Loves sweets",
            email_reminders=False,
            created_at=now,
            updated_at=now,
        )
        assert persona.id == "p1"
        assert persona.loves == ["chocolate", "fruit"]
        assert persona.email_reminders is False

    def test_validation_missing_required_field(self):
        """Validation fails for missing required fields"""
        with pytest.raises(ValidationError):
            Persona(name="John")  # type: ignore

    def test_json_serialization(self):
        """Can serialize to JSON"""
        persona = Persona(
            user_id="user1",
            name="John",
            loves=["chocolate"],
            allergies=["nuts"],
        )
        json_str = persona.model_dump_json()
        data = json.loads(json_str)
        assert data["user_id"] == "user1"
        assert data["loves"] == ["chocolate"]

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = '{"user_id":"user1","name":"John","loves":["chocolate"],"hates":[],"allergies":[],"dietary_restrictions":[],"email_reminders":true}'
        persona = Persona.model_validate_json(json_str)
        assert persona.user_id == "user1"
        assert persona.name == "John"


class TestGiftWizardState:
    """Test GiftWizardState model"""

    def test_instantiate_minimal(self):
        """Can instantiate with minimal fields"""
        state = GiftWizardState(
            occasion="birthday",
            delivery_date=datetime(2026, 3, 1),
        )
        assert state.occasion == "birthday"

    def test_default_values(self):
        """Default values are correct"""
        state = GiftWizardState(
            occasion="birthday",
            delivery_date=datetime(2026, 3, 1),
        )
        assert state.recipient_name is None
        assert state.budget is None
        assert state.recipient_loves == []
        assert state.recipient_hates == []
        assert state.recipient_allergies == []
        assert state.recipient_dietary == []
        assert state.unknown_preferences is False
        assert state.current_step == 1
        assert state.persona_id is None

    def test_instantiate_with_all_fields(self):
        """Can instantiate with all fields"""
        state = GiftWizardState(
            recipient_name="Alice",
            occasion="birthday",
            budget=100.0,
            delivery_date=datetime(2026, 3, 1),
            recipient_loves=["chocolate"],
            recipient_hates=["licorice"],
            recipient_allergies=["nuts"],
            recipient_dietary=["vegan"],
            unknown_preferences=True,
            recipient_description="Loves sweet things",
            current_step=3,
            persona_id="p1",
        )
        assert state.recipient_name == "Alice"
        assert state.budget == 100.0
        assert state.current_step == 3

    def test_validation_invalid_budget_type(self):
        """Validation fails for invalid budget type"""
        with pytest.raises(ValidationError):
            GiftWizardState(
                occasion="birthday",
                budget="not_a_number",  # type: ignore
                delivery_date=datetime(2026, 3, 1),
            )

    def test_json_serialization(self):
        """Can serialize to JSON"""
        state = GiftWizardState(
            occasion="birthday",
            budget=50.0,
            delivery_date=datetime(2026, 3, 1),
            recipient_loves=["fruit"],
        )
        json_str = state.model_dump_json()
        data = json.loads(json_str)
        assert data["occasion"] == "birthday"
        assert data["budget"] == 50.0
        assert data["recipient_loves"] == ["fruit"]

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = '{"occasion":"birthday","delivery_date":"2026-03-01T00:00:00","recipient_loves":["fruit"],"recipient_hates":[],"recipient_allergies":[],"recipient_dietary":[],"unknown_preferences":false}'
        state = GiftWizardState.model_validate_json(json_str)
        assert state.occasion == "birthday"
        assert state.recipient_loves == ["fruit"]


class TestProductScore:
    """Test ProductScore model"""

    def test_instantiate_minimal(self):
        """Can instantiate with minimal fields"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        score = ProductScore(product=product)
        assert score.product.id == "1"

    def test_default_values(self):
        """Default values are correct"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        score = ProductScore(product=product)
        assert score.best_match_score == 0
        assert score.safe_bet_score == 0
        assert score.unique_score == 0
        assert score.score_breakdown == []

    def test_instantiate_with_all_fields(self):
        """Can instantiate with all fields"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        score = ProductScore(
            product=product,
            best_match_score=0.9,
            safe_bet_score=0.7,
            unique_score=0.5,
            score_breakdown=["matches preferences", "in budget"],
        )
        assert score.best_match_score == 0.9
        assert score.score_breakdown == ["matches preferences", "in budget"]

    def test_json_serialization(self):
        """Can serialize to JSON"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        score = ProductScore(
            product=product,
            best_match_score=0.8,
            score_breakdown=["test1"],
        )
        json_str = score.model_dump_json()
        data = json.loads(json_str)
        assert data["product"]["id"] == "1"
        assert data["best_match_score"] == 0.8

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = '{"product":{"id":"1","name":"Box","description":"Desc","price":25.0,"image_url":null,"rating":null,"review_count":null,"category":null,"raw_data":null},"best_match_score":0.8,"safe_bet_score":0,"unique_score":0,"score_breakdown":[]}'
        score = ProductScore.model_validate_json(json_str)
        assert score.product.id == "1"
        assert score.best_match_score == 0.8


class TestRecommendation:
    """Test Recommendation model"""

    def test_instantiate_minimal(self):
        """Can instantiate with minimal fields"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        rec = Recommendation(
            product=product,
            score=0.9,
            category="best_match",
            explanation="Great match",
        )
        assert rec.product.id == "1"
        assert rec.score == 0.9

    def test_default_values(self):
        """Default values are correct"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        rec = Recommendation(
            product=product,
            score=0.9,
            category="best_match",
            explanation="Great",
        )
        assert rec.attributes is None
        assert rec.score_breakdown == []

    def test_instantiate_with_all_fields(self):
        """Can instantiate with all fields"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        attrs = ProductAttributes(product_id="1")
        rec = Recommendation(
            product=product,
            attributes=attrs,
            score=0.9,
            category="best_match",
            explanation="Perfect",
            score_breakdown=["reason1"],
        )
        assert rec.attributes is not None
        assert rec.score_breakdown == ["reason1"]

    def test_validation_invalid_category(self):
        """Validation fails for invalid category"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        with pytest.raises(ValidationError):
            Recommendation(
                product=product,
                score=0.9,
                category="invalid_category",  # type: ignore
                explanation="Test",
            )

    def test_json_serialization(self):
        """Can serialize to JSON"""
        product = Product(id="1", name="Box", description="Desc", price=25.0)
        rec = Recommendation(
            product=product,
            score=0.9,
            category="best_match",
            explanation="Great",
        )
        json_str = rec.model_dump_json()
        data = json.loads(json_str)
        assert data["score"] == 0.9
        assert data["category"] == "best_match"

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = '{"product":{"id":"1","name":"Box","description":"Desc","price":25.0,"image_url":null,"rating":null,"review_count":null,"category":null,"raw_data":null},"attributes":null,"score":0.9,"category":"best_match","explanation":"Great","score_breakdown":[]}'
        rec = Recommendation.model_validate_json(json_str)
        assert rec.score == 0.9
        assert rec.category == "best_match"


class TestThreePickRecommendations:
    """Test ThreePickRecommendations model"""

    def test_instantiate_with_required_fields(self):
        """Can instantiate with required fields"""
        product1 = Product(id="1", name="Box1", description="Desc", price=25.0)
        product2 = Product(id="2", name="Box2", description="Desc", price=30.0)
        rec1 = Recommendation(
            product=product1,
            score=0.9,
            category="best_match",
            explanation="Best",
        )
        rec2 = Recommendation(
            product=product2,
            score=0.7,
            category="safe_bet",
            explanation="Safe",
        )
        three_rec = ThreePickRecommendations(best_match=rec1, safe_bet=rec2)
        assert three_rec.best_match.product.id == "1"
        assert three_rec.safe_bet.product.id == "2"

    def test_unique_is_optional(self):
        """unique field is optional"""
        product1 = Product(id="1", name="Box1", description="Desc", price=25.0)
        product2 = Product(id="2", name="Box2", description="Desc", price=30.0)
        rec1 = Recommendation(
            product=product1,
            score=0.9,
            category="best_match",
            explanation="Best",
        )
        rec2 = Recommendation(
            product=product2,
            score=0.7,
            category="safe_bet",
            explanation="Safe",
        )
        three_rec = ThreePickRecommendations(best_match=rec1, safe_bet=rec2)
        assert three_rec.unique is None

    def test_instantiate_with_unique(self):
        """Can instantiate with unique field"""
        product1 = Product(id="1", name="Box1", description="Desc", price=25.0)
        product2 = Product(id="2", name="Box2", description="Desc", price=30.0)
        product3 = Product(id="3", name="Box3", description="Desc", price=35.0)
        rec1 = Recommendation(
            product=product1,
            score=0.9,
            category="best_match",
            explanation="Best",
        )
        rec2 = Recommendation(
            product=product2,
            score=0.7,
            category="safe_bet",
            explanation="Safe",
        )
        rec3 = Recommendation(
            product=product3,
            score=0.6,
            category="unique",
            explanation="Unique",
        )
        three_rec = ThreePickRecommendations(
            best_match=rec1, safe_bet=rec2, unique=rec3
        )
        assert three_rec.unique is not None
        assert three_rec.unique.product.id == "3"

    def test_json_serialization(self):
        """Can serialize to JSON"""
        product1 = Product(id="1", name="Box1", description="Desc", price=25.0)
        product2 = Product(id="2", name="Box2", description="Desc", price=30.0)
        rec1 = Recommendation(
            product=product1,
            score=0.9,
            category="best_match",
            explanation="Best",
        )
        rec2 = Recommendation(
            product=product2,
            score=0.7,
            category="safe_bet",
            explanation="Safe",
        )
        three_rec = ThreePickRecommendations(best_match=rec1, safe_bet=rec2)
        json_str = three_rec.model_dump_json()
        data = json.loads(json_str)
        assert data["best_match"]["product"]["id"] == "1"
        assert data["safe_bet"]["product"]["id"] == "2"

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = '{"best_match":{"product":{"id":"1","name":"Box1","description":"Desc","price":25.0,"image_url":null,"rating":null,"review_count":null,"category":null,"raw_data":null},"attributes":null,"score":0.9,"category":"best_match","explanation":"Best","score_breakdown":[]},"safe_bet":{"product":{"id":"2","name":"Box2","description":"Desc","price":30.0,"image_url":null,"rating":null,"review_count":null,"category":null,"raw_data":null},"attributes":null,"score":0.7,"category":"safe_bet","explanation":"Safe","score_breakdown":[]},"unique":null}'
        three_rec = ThreePickRecommendations.model_validate_json(json_str)
        assert three_rec.best_match.product.id == "1"
        assert three_rec.unique is None


class TestSafetyValidation:
    """Test SafetyValidation model"""

    def test_instantiate_with_reject_true(self):
        """Can instantiate with reject=True"""
        sv = SafetyValidation(product_id="1", reject=True, reason="Contains allergens")
        assert sv.product_id == "1"
        assert sv.reject is True
        assert sv.reason == "Contains allergens"

    def test_instantiate_with_reject_false(self):
        """Can instantiate with reject=False"""
        sv = SafetyValidation(product_id="1", reject=False)
        assert sv.product_id == "1"
        assert sv.reject is False

    def test_reason_is_optional(self):
        """reason field is optional"""
        sv = SafetyValidation(product_id="1", reject=True)
        assert sv.reason is None

    def test_json_serialization(self):
        """Can serialize to JSON"""
        sv = SafetyValidation(product_id="1", reject=True, reason="Allergen")
        json_str = sv.model_dump_json()
        data = json.loads(json_str)
        assert data["product_id"] == "1"
        assert data["reject"] is True

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = '{"product_id":"1","reject":true,"reason":"Allergen"}'
        sv = SafetyValidation.model_validate_json(json_str)
        assert sv.product_id == "1"
        assert sv.reject is True


class TestSafetyValidationResponse:
    """Test SafetyValidationResponse model"""

    def test_instantiate_empty_list(self):
        """Can instantiate with empty validations list"""
        svr = SafetyValidationResponse(validations=[])
        assert svr.validations == []

    def test_instantiate_with_validations(self):
        """Can instantiate with multiple validations"""
        sv1 = SafetyValidation(product_id="1", reject=False)
        sv2 = SafetyValidation(product_id="2", reject=True, reason="Allergen")
        svr = SafetyValidationResponse(validations=[sv1, sv2])
        assert len(svr.validations) == 2
        assert svr.validations[0].product_id == "1"
        assert svr.validations[1].reject is True

    def test_json_serialization(self):
        """Can serialize to JSON"""
        sv1 = SafetyValidation(product_id="1", reject=False)
        sv2 = SafetyValidation(product_id="2", reject=True)
        svr = SafetyValidationResponse(validations=[sv1, sv2])
        json_str = svr.model_dump_json()
        data = json.loads(json_str)
        assert len(data["validations"]) == 2
        assert data["validations"][0]["product_id"] == "1"

    def test_json_deserialization(self):
        """Can deserialize from JSON"""
        json_str = '{"validations":[{"product_id":"1","reject":false,"reason":null},{"product_id":"2","reject":true,"reason":"Allergen"}]}'
        svr = SafetyValidationResponse.model_validate_json(json_str)
        assert len(svr.validations) == 2
        assert svr.validations[1].reject is True


# Integration tests
class TestIntegration:
    """Integration tests across multiple models"""

    def test_complete_workflow(self):
        """Test a complete workflow with multiple models"""
        # Create a persona
        persona = Persona(
            user_id="user1",
            name="Alice",
            loves=["chocolate", "fruit"],
            allergies=["nuts"],
        )

        # Create wizard state
        state = GiftWizardState(
            recipient_name="Alice",
            occasion="birthday",
            delivery_date=datetime(2026, 3, 1),
            recipient_loves=persona.loves,
            recipient_allergies=persona.allergies,
        )
        assert state.occasion == "birthday"

        # Create products
        product1 = Product(
            id="1",
            name="Dark Chocolate Box",
            description="Premium dark chocolate",
            price=30.0,
        )
        product2 = Product(
            id="2",
            name="Fruit Dipped Chocolate",
            description="Fresh fruit with chocolate",
            price=35.0,
        )

        # Create attributes
        attrs1 = ProductAttributes(
            product_id="1",
            chocolate_type="dark",
            contains_nuts=False,
            dietary_labels=["vegan"],
        )
        attrs2 = ProductAttributes(
            product_id="2",
            fruit_types=["strawberry", "raspberry"],
            contains_nuts=False,
            dietary_labels=["vegan"],
        )

        # Create recommendations
        rec1 = Recommendation(
            product=product1,
            attributes=attrs1,
            score=0.95,
            category="best_match",
            explanation="Matches all preferences",
            score_breakdown=["chocolate lover", "vegan friendly"],
        )
        rec2 = Recommendation(
            product=product2,
            attributes=attrs2,
            score=0.85,
            category="safe_bet",
            explanation="Fruit and chocolate combination",
            score_breakdown=["loves fruit", "no allergens"],
        )

        # Create final recommendation set
        recommendations = ThreePickRecommendations(best_match=rec1, safe_bet=rec2)

        # Validate safety
        safety_check = SafetyValidationResponse(
            validations=[
                SafetyValidation(product_id="1", reject=False),
                SafetyValidation(product_id="2", reject=False),
            ]
        )

        # Serialize to JSON and back
        rec_json = recommendations.model_dump_json()
        rec_restored = ThreePickRecommendations.model_validate_json(rec_json)

        assert rec_restored.best_match.product.id == "1"
        assert rec_restored.safe_bet.product.id == "2"
        assert len(safety_check.validations) == 2

    def test_all_models_json_roundtrip(self):
        """Test that all models can do JSON roundtrip without data loss"""
        # Product
        p = Product(id="1", name="X", description="Y", price=10.0, rating=4.5)
        p_restored = Product.model_validate_json(p.model_dump_json())
        assert p_restored.rating == 4.5

        # ProductAttributes
        pa = ProductAttributes(
            product_id="1", chocolate_type="dark", contains_nuts=True
        )
        pa_restored = ProductAttributes.model_validate_json(pa.model_dump_json())
        assert pa_restored.chocolate_type == "dark"

        # Persona
        pers = Persona(user_id="u1", name="N", loves=["a", "b"])
        pers_restored = Persona.model_validate_json(pers.model_dump_json())
        assert pers_restored.loves == ["a", "b"]

        # GiftWizardState
        gws = GiftWizardState(occasion="birthday", delivery_date=datetime(2026, 3, 1))
        gws_restored = GiftWizardState.model_validate_json(gws.model_dump_json())
        assert gws_restored.occasion == "birthday"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
