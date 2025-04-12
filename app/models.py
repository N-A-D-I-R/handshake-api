import re

from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy import Index, ForeignKey, Text, DateTime, Sequence
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TSVECTOR

Base = declarative_base()

user_id_seq = Sequence('shared_user_id_seq')

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, user_id_seq, primary_key=True, server_default=user_id_seq.next_value())
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")

    @validates("email")
    def validate_email(self, key, value):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, value):
            raise ValueError(f"Неверный формат E-mail")
        return value

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class SuperUser(Base):
    __tablename__ = "superusers"
    
    id = Column(Integer, user_id_seq, primary_key=True, server_default=user_id_seq.next_value())
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)

    def __repr__(self):
        return f"<SuperUser(id={self.id}, username='{self.username}')>"

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)

    need = Column(Text, nullable=False)
    offer = Column(Text, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_vector = Column(TSVECTOR, index=True)
    status = Column(Enum("pending", "approved", name="post_status"), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="posts")
    
    __table_args__ = (
        Index("ix_post_title_trgm", title, postgresql_using="gin", postgresql_ops={"title": "gin_trgm_ops"}),
        Index("ix_post_search_vector", search_vector, postgresql_using="gin")
    )

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user_agent = Column(Text)
    ip_address = Column(String(45))  # IPv4 и IPv6
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

class EmailConfirmation(Base):
    __tablename__ = "email_confirmations"

    email = Column(String, primary_key=True, index=True)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)