from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, security, database
from typing import List

router = APIRouter(prefix="/front", tags=["Customer API"])


@router.get("/category-list", response_model=List[schemas.CategoryDisplay])
def get_categories(db: Session = Depends(database.get_db)):
    categories = db.query(models.Category).all()
    return categories  # Returns [] if empty (NOT a dict)


# ✅ FIXED: Returns empty list [] instead of dict
@router.get("/product-list", response_model=List[schemas.ProductDisplay])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products  # Returns [] if empty


# ✅ FIXED: Returns empty list [] or raise 404 for invalid category
@router.get("/product-by-category-list/{category_id}", response_model=List[schemas.ProductDisplay])
def get_products_by_category(category_id: int, db: Session = Depends(database.get_db)):
    # Optional: Check if category exists
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    products = db.query(models.Product).filter(models.Product.category_id == category_id).all()
    return products  # Returns [] if no products in category

@router.post("/add-to-cart")
def add_to_cart(
        item: schemas.CartItem,
        current_user: models.User = Depends(security.get_current_user),
        db: Session = Depends(database.get_db)
):
    if not current_user.cart:
        current_user.cart = models.Cart(user_id=current_user.id, items=[])

    current_user.cart.items.append({"product_id": item.product_id, "quantity": item.quantity})
    db.commit()
    return {"message": "Added to cart", "cart_id": current_user.cart.id}


@router.get("/cart")
def get_cart(
        current_user: models.User = Depends(security.get_current_user),
        db: Session = Depends(database.get_db)
):
    if not current_user.cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return current_user.cart


@router.post("/checkout")
def checkout(
        order: schemas.OrderCreate,
        current_user: models.User = Depends(security.get_current_user),
        db: Session = Depends(database.get_db)
):
    if not current_user.cart or len(current_user.cart.items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0
    for item in current_user.cart.items:
        product = db.query(models.Product).filter(models.Product.id == item["product_id"]).first()
        if product:
            total += product.price * item["quantity"]

    new_order = models.Order(
        user_id=current_user.id,
        total_amount=total,
        status="pending",
        shipping_address=order.shipping_address,
        payment_method=order.payment_method
    )
    db.add(new_order)
    current_user.cart.items = []
    db.commit()
    db.refresh(new_order)

    return {"message": "Checkout successful", "order_id": new_order.id, "total": total}


@router.get("/tracking-order", response_model=List[schemas.OrderDisplay])
def track_orders(
        current_user: models.User = Depends(security.get_current_user),
        db: Session = Depends(database.get_db)
):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()


@router.get("/tracking-order/{order_id}", response_model=schemas.OrderDisplay)
def track_order(
        order_id: int,
        current_user: models.User = Depends(security.get_current_user),
        db: Session = Depends(database.get_db)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order