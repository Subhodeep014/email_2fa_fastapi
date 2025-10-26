from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'recipe_users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, index=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    is_verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    code_expiry = Column(DateTime(timezone=True), nullable=True)

    recipes = relationship("Recipe", back_populates="owner")
 

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    ingredients = Column(String)
    instructions = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id = Column(UUID(as_uuid=True), ForeignKey("recipe_users.id"), nullable=False)
    owner = relationship("User", back_populates="recipes")