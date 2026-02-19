from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    Numeric,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum  # ← используем SQLEnum для явного задания имени
import enum


class Base(DeclarativeBase):
    pass


# ────────────────────────────────────────────────
# ENUMS (все строковые значения)
# ────────────────────────────────────────────────

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    BUYER = "BUYER"
    SUPPLIER = "SUPPLIER"


class OrderStatus(enum.Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class DocumentType(enum.Enum):
    INVOICE = "INVOICE"
    CONTRACT = "CONTRACT"
    ACT = "ACT"


# ────────────────────────────────────────────────
# TABLES
# ────────────────────────────────────────────────

class Enterprise(Base):
    __tablename__ = "enterprises"

    id = Column(BigInteger, primary_key=True)
    short_name = Column(Text, nullable=False)
    inn = Column(Text, nullable=False)
    region = Column(Text, nullable=False)
    phone = Column(Text)
    email = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="enterprise")
    reviews_as_author = relationship(
        "EnterpriseReview",
        foreign_keys="EnterpriseReview.author_enterprise_id",
        back_populates="author_enterprise",
    )
    reviews_as_target = relationship(
        "EnterpriseReview",
        foreign_keys="EnterpriseReview.target_enterprise_id",
        back_populates="target_enterprise",
    )
    product_reviews = relationship("ProductReview", back_populates="author_enterprise")


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)

    role = Column(
        SQLEnum(
            UserRole,
            name="user_role",                        # ← ЯВНО указываем имя типа в БД
            values_callable=lambda en: [e.value for e in en],
            create_type=False,
        ),
        nullable=False,
    )

    enterprise_id = Column(BigInteger, ForeignKey("enterprises.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    enterprise = relationship("Enterprise", back_populates="users")
    carts = relationship("Cart", back_populates="user")
    messages_sent = relationship("Message", back_populates="sender")
    order_history = relationship("OrderHistory", back_populates="changed_by_user")
    favorites = relationship("Favorite", back_populates="user")
    chats_as_user1 = relationship("Chat", foreign_keys="Chat.user1_id", back_populates="user1")
    chats_as_user2 = relationship("Chat", foreign_keys="Chat.user2_id", back_populates="user2")


class Category(Base):
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    price = Column(Numeric(12, 2), nullable=False)
    min_order_qty = Column(Integer)
    quantity_in_stock = Column(Integer)
    enterprise_id = Column(BigInteger, ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    enterprise = relationship("Enterprise")
    category = relationship("Category")
    favorites = relationship("Favorite", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True)

    status = Column(
        SQLEnum(
            OrderStatus,
            name="order_status",
            values_callable=lambda en: [e.value for e in en],
            create_type=False,
        ),
        nullable=False,
    )

    total_amount = Column(Numeric(14, 2))
    buyer_enterprise_id = Column(BigInteger, ForeignKey("enterprises.id"), nullable=False)
    seller_enterprise_id = Column(BigInteger, ForeignKey("enterprises.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    buyer_enterprise = relationship("Enterprise", foreign_keys=[buyer_enterprise_id])
    seller_enterprise = relationship("Enterprise", foreign_keys=[seller_enterprise_id])
    items = relationship("OrderItem", back_populates="order")
    history = relationship("OrderHistory", back_populates="order")
    payment = relationship("Payment", back_populates="order", uselist=False)
    documents = relationship("Document", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class OrderHistory(Base):
    __tablename__ = "order_history"

    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    status = Column(
        SQLEnum(
            OrderStatus,
            name="order_status",
            values_callable=lambda en: [e.value for e in en],
            create_type=False,
        ),
        nullable=False,
    )

    changed_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="history")
    changed_by_user = relationship("User", back_populates="order_history")


class Cart(Base):
    __tablename__ = "carts"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(BigInteger, primary_key=True)
    cart_id = Column(BigInteger, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_favorite", "user_id", "product_id", unique=True),
    )

    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)

    status = Column(
        SQLEnum(
            PaymentStatus,
            name="payment_status",
            values_callable=lambda en: [e.value for e in en],
            create_type=False,
        ),
        nullable=False,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="payment")


class Document(Base):
    __tablename__ = "documents"

    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    type = Column(
        SQLEnum(
            DocumentType,
            name="document_type",
            values_callable=lambda en: [e.value for e in en],
            create_type=False,
        ),
        nullable=False,
    )

    file_url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="documents")


class EnterpriseReview(Base):
    __tablename__ = "enterprise_reviews"

    id = Column(BigInteger, primary_key=True)
    author_enterprise_id = Column(BigInteger, ForeignKey("enterprises.id"), nullable=False)
    target_enterprise_id = Column(BigInteger, ForeignKey("enterprises.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5"),
    )

    author_enterprise = relationship("Enterprise", foreign_keys=[author_enterprise_id], back_populates="reviews_as_author")
    target_enterprise = relationship("Enterprise", foreign_keys=[target_enterprise_id], back_populates="reviews_as_target")


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(BigInteger, primary_key=True)
    author_enterprise_id = Column(BigInteger, ForeignKey("enterprises.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5"),
    )

    author_enterprise = relationship("Enterprise", back_populates="product_reviews")
    product = relationship("Product", back_populates="reviews")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(BigInteger, primary_key=True)
    user1_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_min = Column(BigInteger, nullable=False)
    user_max = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_chats_user1", "user1_id"),
        Index("idx_chats_user2", "user2_id"),
        Index("uq_chats_users", "user_min", "user_max", unique=True),
    )

    user1 = relationship("User", foreign_keys=[user1_id], back_populates="chats_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="chats_as_user2")
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages_sent")