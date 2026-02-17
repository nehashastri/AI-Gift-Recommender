from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class PersonaDB(Base):
    """Database model for saved personas"""

    __tablename__ = "personas"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    birthday = Column(DateTime, nullable=True)
    loves = Column(JSON, default=[])
    hates = Column(JSON, default=[])
    allergies = Column(JSON, default=[])
    dietary_restrictions = Column(JSON, default=[])
    description = Column(String, nullable=True)
    email_reminders = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class Database:
    """Database manager"""

    def __init__(self, db_path: str = "data/gift_genius.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_persona(self, persona_data: dict) -> str:
        """Create new persona"""
        import uuid

        persona_id = str(uuid.uuid4())

        persona = PersonaDB(
            id=persona_id,
            user_id=persona_data.get("user_id", "default_user"),
            name=persona_data["name"],
            birthday=persona_data.get("birthday"),
            loves=persona_data.get("loves", []),
            hates=persona_data.get("hates", []),
            allergies=persona_data.get("allergies", []),
            dietary_restrictions=persona_data.get("dietary_restrictions", []),
            description=persona_data.get("description"),
            email_reminders=persona_data.get("email_reminders", True),
        )

        self.session.add(persona)
        self.session.commit()

        return persona_id

    def get_persona(self, persona_id: str) -> Optional[dict]:
        """Get persona by ID"""
        persona = self.session.query(PersonaDB).filter_by(id=persona_id).first()

        if not persona:
            return None

        return self._persona_to_dict(persona)

    def get_user_personas(self, user_id: str = "default_user") -> List[dict]:
        """Get all personas for a user"""
        personas = self.session.query(PersonaDB).filter_by(user_id=user_id).all()
        return [self._persona_to_dict(p) for p in personas]

    def update_persona(self, persona_id: str, updates: dict) -> bool:
        """Update existing persona"""
        persona = self.session.query(PersonaDB).filter_by(id=persona_id).first()

        if not persona:
            return False

        # Update fields
        for key, value in updates.items():
            if hasattr(persona, key):
                setattr(persona, key, value)

        setattr(persona, "updated_at", datetime.now())
        self.session.commit()

        return True

    def delete_persona(self, persona_id: str) -> bool:
        """Delete persona"""
        persona = self.session.query(PersonaDB).filter_by(id=persona_id).first()

        if not persona:
            return False

        self.session.delete(persona)
        self.session.commit()

        return True

    def _persona_to_dict(self, persona: PersonaDB) -> dict:
        """Convert database model to dict"""
        return {
            "id": persona.id,
            "user_id": persona.user_id,
            "name": persona.name,
            "birthday": persona.birthday,
            "loves": persona.loves or [],
            "hates": persona.hates or [],
            "allergies": persona.allergies or [],
            "dietary_restrictions": persona.dietary_restrictions or [],
            "description": persona.description,
            "email_reminders": persona.email_reminders,
            "created_at": persona.created_at,
            "updated_at": persona.updated_at,
        }
