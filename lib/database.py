from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from lib.types import Persona

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

    def create_persona(self, persona: Persona) -> str:
        """Create new persona from Pydantic model"""
        import uuid

        persona_id = persona.id or str(uuid.uuid4())

        persona_db = PersonaDB(
            id=persona_id,
            user_id=persona.user_id,
            name=persona.name,
            birthday=persona.birthday,
            loves=persona.loves,
            hates=persona.hates,
            allergies=persona.allergies,
            dietary_restrictions=persona.dietary_restrictions,
            description=persona.description,
            email_reminders=persona.email_reminders,
        )

        self.session.add(persona_db)
        self.session.commit()

        return persona_id

    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get persona by ID"""
        persona_db = self.session.query(PersonaDB).filter_by(id=persona_id).first()

        if not persona_db:
            return None

        return self._persona_to_model(persona_db)

    def get_user_personas(self, user_id: str = "default_user") -> List[Persona]:
        """Get all personas for a user"""
        personas_db = self.session.query(PersonaDB).filter_by(user_id=user_id).all()
        return [self._persona_to_model(p) for p in personas_db]

    def get_all_personas(self) -> List[Persona]:
        """Get all personas"""
        personas_db = self.session.query(PersonaDB).all()
        return [self._persona_to_model(p) for p in personas_db]

    def update_persona(self, persona_id: str, updates: dict) -> bool:
        """Update existing persona with dict of updates"""
        persona_db = self.session.query(PersonaDB).filter_by(id=persona_id).first()

        if not persona_db:
            return False

        # Update fields
        for key, value in updates.items():
            if hasattr(persona_db, key) and key not in ["id", "created_at"]:
                setattr(persona_db, key, value)

        setattr(persona_db, "updated_at", datetime.now())
        self.session.commit()

        return True

    def update_persona_from_model(self, persona: Persona) -> bool:
        """Update existing persona from Pydantic model"""
        if not persona.id:
            return False

        persona_db = self.session.query(PersonaDB).filter_by(id=persona.id).first()

        if not persona_db:
            return False

        # Update fields from Pydantic model
        persona_db.user_id = persona.user_id  # type: ignore
        persona_db.name = persona.name  # type: ignore
        persona_db.birthday = persona.birthday  # type: ignore
        persona_db.loves = persona.loves  # type: ignore
        persona_db.hates = persona.hates  # type: ignore
        persona_db.allergies = persona.allergies  # type: ignore
        persona_db.dietary_restrictions = persona.dietary_restrictions  # type: ignore
        persona_db.description = persona.description  # type: ignore
        persona_db.email_reminders = persona.email_reminders  # type: ignore

        setattr(persona_db, "updated_at", datetime.now())
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

    def _persona_to_model(self, persona_db: PersonaDB) -> Persona:
        """Convert database model to Pydantic model"""
        return Persona(
            id=persona_db.id,  # type: ignore
            user_id=persona_db.user_id,  # type: ignore
            name=persona_db.name,  # type: ignore
            birthday=persona_db.birthday,  # type: ignore
            loves=persona_db.loves or [],  # type: ignore
            hates=persona_db.hates or [],  # type: ignore
            allergies=persona_db.allergies or [],  # type: ignore
            dietary_restrictions=persona_db.dietary_restrictions or [],  # type: ignore
            description=persona_db.description,  # type: ignore
            email_reminders=persona_db.email_reminders,  # type: ignore
            created_at=persona_db.created_at,  # type: ignore
            updated_at=persona_db.updated_at,  # type: ignore
        )
