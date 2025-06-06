from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy import Text, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)

    username = Column(String(32), unique=True, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    password = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_moderator = Column(Boolean, default=False)
    search_vector = Column(TSVECTOR, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    change_requests = relationship("ProfileChangeRequest", back_populates="user", cascade="all, delete")

    __table_args__ = (
        Index("ix_user_search_vector", search_vector, postgresql_using="gin"),
        Index("ix_user_username_trgm", "username", postgresql_using="gin", postgresql_ops={"username": "gin_trgm_ops"}),
        Index("ix_user_name_trgm", "first_name", "last_name", postgresql_using="gin", postgresql_ops={"first_name": "gin_trgm_ops", "last_name": "gin_trgm_ops"}),
    )
    
    def __repr__(self):
        return (
            f"<User("
            f"id={self.id}, "
            f"username='{self.username}', "
            f"email='{self.email}', "
            f"first_name='{self.first_name}', "
            f"last_name='{self.last_name}', "
            f"is_verified={self.is_verified}, "
            f"is_moderator={self.is_moderator}, "
            f"created_at='{self.created_at}'"
            f")>"
        )

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)

    avatar_url = Column(String(500), nullable=True)
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

class ProfileChangeRequest(Base):
    __tablename__ = "profile_change_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    new_username = Column(String, nullable=True)
    new_first_name = Column(String, nullable=True)
    new_last_name = Column(String, nullable=True)
    new_avatar_url = Column(String, nullable=True)

    search_vector = Column(TSVECTOR, index=True)
    created_at = Column(DateTime, server_default=func.now())
    is_approved = Column(Boolean, default=None)

    user = relationship("User", back_populates="change_requests")

    __table_args__ = (
        Index("ix_profile_change_requests_is_approved", "is_approved"),
        Index("ix_profile_change_requests_created_at", "created_at"),
    )

    def __repr__(self):
        return (
            f"<ProfileChangeRequest(user_id={self.user_id}, "
            f"username={self.new_username}, first_name={self.new_first_name}, "
            f"last_name={self.new_last_name}, approved={self.is_approved})>"
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