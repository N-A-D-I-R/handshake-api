from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy import Text, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_moderator = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<User("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"email='{self.email}', "
            f"is_verified={self.is_verified}, "
            f"is_moderator={self.is_moderator}, "
            f"created_at='{self.created_at}'"
            f")>"
        )

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    need = Column(Text, nullable=False)
    offer = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_vector = Column(TSVECTOR, index=True)
    status = Column(Enum("pending", "approved", name="post_status"), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="posts")

    __table_args__ = (
        Index("ix_post_title_trgm", title, postgresql_using="gin", postgresql_ops={"title": "gin_trgm_ops"}),
        Index("ix_post_search_vector", search_vector, postgresql_using="gin"),
    )

    def __repr__(self):
        return (
            f"<Post("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"offer='{self.offer}', "
            f"description={self.description}, "
            f"user_id={self.user_id}, "
            f"status={self.status}, "
            f"created_at='{self.created_at}'"
            f")>"
        )

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return (
            f"<RefreshToken("
            f"id={self.id}, "
            f"user_id='{self.user_id}', "
            f"user_agent='{self.user_agent}', "
            f"ip_address={self.ip_address}, "
            f"created_at={self.created_at}, "
            f"expires_at={self.expires_at}, "
            f"is_active='{self.is_active}'"
            f")>"
        )

class EmailConfirmation(Base):
    __tablename__ = "email_confirmations"

    email = Column(String, primary_key=True, index=True)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return (
            f"<EmailConfirmation("
            f"email={self.email}, "
            f"expires_at={self.expires_at}, "
            f")>"
        )

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return (
            f"<Notification("
            f"id={self.id}, "
            f"user_id='{self.user_id}', "
            f"title='{self.title}', "
            f"message={self.message}, "
            f"is_read={self.is_read}, "
            f"created_at='{self.created_at}'"
            f")>"
        )