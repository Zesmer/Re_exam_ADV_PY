from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, security, database
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin API"])

def get_current_admin_user(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    return current_user

# --- USER CRUD ---
@router.get("/users", response_model=List[schemas.UserDisplay])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    return db.query(models.User).offset(skip).limit(limit).all()

@router.get("/users/{user_id}", response_model=schemas.UserDisplay)
def get_user(user_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=schemas.UserDisplay)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_pw, full_name=user.full_name, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}", response_model=schemas.UserDisplay)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

# --- CATEGORY CRUD ---
@router.get("/categories", response_model=List[schemas.CategoryDisplay])
def get_all_categories(db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    return db.query(models.Category).all()

@router.get("/categories/{category_id}", response_model=schemas.CategoryDisplay)
def get_category(category_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/categories", response_model=schemas.CategoryDisplay)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_category = models.Category(name=category.name, description=category.description, image=category.image)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=schemas.CategoryDisplay)
def update_category(category_id: int, category_update: schemas.CategoryUpdate, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    update_data = category_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}

# --- PRODUCT CRUD ---
@router.get("/products", response_model=List[schemas.ProductDisplay])
def get_all_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    return db.query(models.Product).offset(skip).limit(limit).all()

@router.get("/products/{product_id}", response_model=schemas.ProductDisplay)
def get_product(product_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=schemas.ProductDisplay)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=schemas.ProductDisplay)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

# --- ORDER MANAGEMENT ---
@router.get("/orders", response_model=List[schemas.OrderDisplay])
def get_all_orders(skip: int = 0, limit: int = 100, status_filter: str = None, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    query = db.query(models.Order)
    if status_filter:
        query = query.filter(models.Order.status == status_filter)
    return query.offset(skip).limit(limit).all()

@router.get("/orders/{order_id}", response_model=schemas.OrderDisplay)
def get_order(order_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/orders/{order_id}", response_model=schemas.OrderDisplay)
def update_order(order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    update_data = order_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted successfully"}

# --- REPORTS ---
@router.get("/reports/sale")
def get_sales_report(db: Session = Depends(database.get_db), admin: models.User = Depends(get_current_admin_user)):
    total_orders = db.query(models.Order).count()
    revenue = db.query(models.Order).sum(models.Order.total_amount)
    return {"total_orders": total_orders, "total_revenue": revenue[0] or 0}