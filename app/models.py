from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import Index

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    auth_key = Column(String(16), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=False)
    
    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_vector = Column(TSVECTOR, index=True)
    
    owner = relationship("User", back_populates="posts")
    
    __table_args__ = (
        Index("ix_post_title_trgm", title, postgresql_using="gin", postgresql_ops={"title": "gin_trgm_ops"}),
        Index("ix_post_search_vector", search_vector, postgresql_using="gin")
    )
