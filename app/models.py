from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for user roles and transaction types
class UserRole(str, Enum):
    ADMIN = "admin"
    CASHIER = "cashier"
    RESELLER = "reseller"
    AFFILIATE = "affiliate"
    CONSUMER = "consumer"


class TransactionType(str, Enum):
    POS = "pos"
    ONLINE = "online"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PromotionType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BUY_X_GET_Y = "buy_x_get_y"


# Base User model
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=100)
    email: str = Field(unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    full_name: str = Field(max_length=200)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.CONSUMER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    reseller_profile: Optional["ResellerProfile"] = Relationship(back_populates="user")
    affiliate_profile: Optional["AffiliateProfile"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    commissions: List["Commission"] = Relationship(back_populates="user")


# Reseller profile for multi-level structure
class ResellerProfile(SQLModel, table=True):
    __tablename__ = "reseller_profiles"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    level: int = Field(ge=1, le=10)  # Levels 1-10
    parent_reseller_id: Optional[int] = Field(default=None, foreign_key="reseller_profiles.id")
    referral_code: str = Field(unique=True, max_length=50)
    commission_rate: Decimal = Field(default=Decimal("0"), decimal_places=4, max_digits=8)
    total_sales: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=15)
    total_commission: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=15)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="reseller_profile")
    parent_reseller: Optional["ResellerProfile"] = Relationship(
        back_populates="child_resellers", sa_relationship_kwargs={"remote_side": "ResellerProfile.id"}
    )
    child_resellers: List["ResellerProfile"] = Relationship(back_populates="parent_reseller")
    product_prices: List["ProductResellerPrice"] = Relationship(back_populates="reseller_profile")


# Affiliate profile
class AffiliateProfile(SQLModel, table=True):
    __tablename__ = "affiliate_profiles"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    affiliate_code: str = Field(unique=True, max_length=50)
    commission_rate: Decimal = Field(default=Decimal("0"), decimal_places=4, max_digits=8)
    total_sales: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=15)
    total_commission: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=15)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="affiliate_profile")
    affiliate_links: List["AffiliateLink"] = Relationship(back_populates="affiliate_profile")


# Category for products
class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    parent_category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    parent_category: Optional["Category"] = Relationship(
        back_populates="subcategories", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    subcategories: List["Category"] = Relationship(back_populates="parent_category")
    products: List["Product"] = Relationship(back_populates="category")


# Product model
class Product(SQLModel, table=True):
    __tablename__ = "products"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    sku: str = Field(unique=True, max_length=100)
    barcode: Optional[str] = Field(default=None, max_length=100)
    category_id: int = Field(foreign_key="categories.id")
    base_price: Decimal = Field(decimal_places=2, max_digits=10)
    cost_price: Decimal = Field(decimal_places=2, max_digits=10)
    stock_quantity: int = Field(default=0)
    min_stock_level: int = Field(default=0)
    is_active: bool = Field(default=True)
    image_url: Optional[str] = Field(default=None, max_length=500)
    weight: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)
    dimensions: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Category = Relationship(back_populates="products")
    reseller_prices: List["ProductResellerPrice"] = Relationship(back_populates="product")
    transaction_items: List["TransactionItem"] = Relationship(back_populates="product")
    stock_movements: List["StockMovement"] = Relationship(back_populates="product")
    promotions: List["PromotionProduct"] = Relationship(back_populates="product")


# Product pricing for different reseller levels
class ProductResellerPrice(SQLModel, table=True):
    __tablename__ = "product_reseller_prices"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    reseller_profile_id: Optional[int] = Field(default=None, foreign_key="reseller_profiles.id")
    reseller_level: Optional[int] = Field(default=None, ge=1, le=10)
    price: Decimal = Field(decimal_places=2, max_digits=10)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    product: Product = Relationship(back_populates="reseller_prices")
    reseller_profile: Optional[ResellerProfile] = Relationship(back_populates="product_prices")


# Transaction model
class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_number: str = Field(unique=True, max_length=50)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    cashier_id: Optional[int] = Field(default=None, foreign_key="users.id")
    reseller_id: Optional[int] = Field(default=None, foreign_key="users.id")
    affiliate_id: Optional[int] = Field(default=None, foreign_key="users.id")
    transaction_type: TransactionType = Field(default=TransactionType.POS)
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    subtotal: Decimal = Field(decimal_places=2, max_digits=15)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=15)
    tax_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=15)
    total_amount: Decimal = Field(decimal_places=2, max_digits=15)
    payment_method: str = Field(max_length=50)
    notes: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional[User] = Relationship(back_populates="transactions")
    items: List["TransactionItem"] = Relationship(back_populates="transaction")
    commissions: List["Commission"] = Relationship(back_populates="transaction")
    promotions: List["TransactionPromotion"] = Relationship(back_populates="transaction")


# Transaction items
class TransactionItem(SQLModel, table=True):
    __tablename__ = "transaction_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(decimal_places=2, max_digits=10)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=10)
    total_price: Decimal = Field(decimal_places=2, max_digits=15)

    # Relationships
    transaction: Transaction = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="transaction_items")


# Commission tracking
class Commission(SQLModel, table=True):
    __tablename__ = "commissions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    transaction_id: int = Field(foreign_key="transactions.id")
    commission_type: str = Field(max_length=50)  # 'reseller' or 'affiliate'
    level: Optional[int] = Field(default=None)  # For multi-level commissions
    base_amount: Decimal = Field(decimal_places=2, max_digits=15)
    commission_rate: Decimal = Field(decimal_places=4, max_digits=8)
    commission_amount: Decimal = Field(decimal_places=2, max_digits=15)
    is_paid: bool = Field(default=False)
    paid_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="commissions")
    transaction: Transaction = Relationship(back_populates="commissions")


# Stock movement tracking
class StockMovement(SQLModel, table=True):
    __tablename__ = "stock_movements"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    movement_type: str = Field(max_length=50)  # 'in', 'out', 'adjustment'
    quantity: int
    previous_quantity: int
    new_quantity: int
    reference_number: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_by: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    product: Product = Relationship(back_populates="stock_movements")


# Promotions and discounts
class Promotion(SQLModel, table=True):
    __tablename__ = "promotions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    promotion_type: PromotionType
    discount_value: Decimal = Field(decimal_places=2, max_digits=10)
    min_purchase_amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    max_discount_amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    start_date: datetime
    end_date: datetime
    is_active: bool = Field(default=True)
    usage_limit: Optional[int] = Field(default=None)
    usage_count: int = Field(default=0)
    applicable_roles: List[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    products: List["PromotionProduct"] = Relationship(back_populates="promotion")
    transactions: List["TransactionPromotion"] = Relationship(back_populates="promotion")


# Many-to-many relationship for promotions and products
class PromotionProduct(SQLModel, table=True):
    __tablename__ = "promotion_products"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    promotion_id: int = Field(foreign_key="promotions.id")
    product_id: int = Field(foreign_key="products.id")

    # Relationships
    promotion: Promotion = Relationship(back_populates="products")
    product: Product = Relationship(back_populates="promotions")


# Track which promotions were applied to transactions
class TransactionPromotion(SQLModel, table=True):
    __tablename__ = "transaction_promotions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id")
    promotion_id: int = Field(foreign_key="promotions.id")
    discount_amount: Decimal = Field(decimal_places=2, max_digits=10)

    # Relationships
    transaction: Transaction = Relationship(back_populates="promotions")
    promotion: Promotion = Relationship(back_populates="transactions")


# Affiliate links for tracking
class AffiliateLink(SQLModel, table=True):
    __tablename__ = "affiliate_links"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    affiliate_profile_id: int = Field(foreign_key="affiliate_profiles.id")
    product_id: Optional[int] = Field(default=None, foreign_key="products.id")
    link_code: str = Field(unique=True, max_length=100)
    clicks: int = Field(default=0)
    conversions: int = Field(default=0)
    total_sales: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=15)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    affiliate_profile: AffiliateProfile = Relationship(back_populates="affiliate_links")


# Receipt/Invoice model
class Receipt(SQLModel, table=True):
    __tablename__ = "receipts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id", unique=True)
    receipt_number: str = Field(unique=True, max_length=50)
    printed: bool = Field(default=False)
    printed_at: Optional[datetime] = Field(default=None)
    email_sent: bool = Field(default=False)
    email_sent_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# System settings
class Setting(SQLModel, table=True):
    __tablename__ = "settings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, max_length=100)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas for validation and API requests/responses


class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6)
    full_name: str = Field(max_length=200)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.CONSUMER)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: Optional[UserRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class ProductCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    sku: str = Field(max_length=100)
    barcode: Optional[str] = Field(default=None, max_length=100)
    category_id: int
    base_price: Decimal = Field(decimal_places=2, max_digits=10)
    cost_price: Decimal = Field(decimal_places=2, max_digits=10)
    stock_quantity: int = Field(default=0)
    min_stock_level: int = Field(default=0)
    image_url: Optional[str] = Field(default=None, max_length=500)
    weight: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)
    dimensions: Optional[Dict[str, Any]] = Field(default=None)


class ProductUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    base_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    cost_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    stock_quantity: Optional[int] = Field(default=None)
    min_stock_level: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    image_url: Optional[str] = Field(default=None, max_length=500)
    weight: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)
    dimensions: Optional[Dict[str, Any]] = Field(default=None)


class TransactionCreate(SQLModel, table=False):
    user_id: Optional[int] = Field(default=None)
    cashier_id: Optional[int] = Field(default=None)
    reseller_id: Optional[int] = Field(default=None)
    affiliate_id: Optional[int] = Field(default=None)
    transaction_type: TransactionType = Field(default=TransactionType.POS)
    payment_method: str = Field(max_length=50)
    notes: Optional[str] = Field(default=None, max_length=1000)
    items: List[Dict[str, Any]] = Field(default=[])


class TransactionItemCreate(SQLModel, table=False):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    parent_category_id: Optional[int] = Field(default=None)


class ResellerProfileCreate(SQLModel, table=False):
    user_id: int
    level: int = Field(ge=1, le=10)
    parent_reseller_id: Optional[int] = Field(default=None)
    commission_rate: Decimal = Field(decimal_places=4, max_digits=8)


class AffiliateProfileCreate(SQLModel, table=False):
    user_id: int
    commission_rate: Decimal = Field(decimal_places=4, max_digits=8)


class PromotionCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    promotion_type: PromotionType
    discount_value: Decimal = Field(decimal_places=2, max_digits=10)
    min_purchase_amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    max_discount_amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    start_date: datetime
    end_date: datetime
    usage_limit: Optional[int] = Field(default=None)
    applicable_roles: List[str] = Field(default=[])
    product_ids: List[int] = Field(default=[])
