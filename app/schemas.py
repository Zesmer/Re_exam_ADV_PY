from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    is_admin: bool = False
    phone: Optional[str] = None
    address: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserDisplay(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool
    phone: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# --- Category ---
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None

class CategoryDisplay(CategoryBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Product ---
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category_id: int
    image: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    image: Optional[str] = None

class ProductDisplay(ProductBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Cart ---
class CartItem(BaseModel):
    product_id: int
    quantity: int

class CartDisplay(BaseModel):
    id: int
    user_id: int
    items: list
    class Config:
        from_attributes = True

# --- Order ---
class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: str

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    tracking_number: Optional[str] = None

class OrderDisplay(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    tracking_number: Optional[str]
    shipping_address: str
    created_at: datetime
    class Config:
        from_attributes = True