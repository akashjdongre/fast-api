from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil, os, uuid
from response.response import RespAllPRoducts

from database import get_db
from models.product import Product
from core.dependencies import get_current_user, require_admin
from models.user import User

router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# PUBLIC — list products with pagination & search
@router.get("/", response_model=RespAllPRoducts)
def list_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    search: Optional[str] = Query(None)
):
    query = db.query(Product)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total   = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "results": products
    }

# PUBLIC — get single product
@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# ADMIN ONLY — create product with image upload
@router.post("/", status_code=201)
def create_product(
    name: str,
    description: str,
    price: float,
    stock: int,
    image: UploadFile = File(None),          # optional image
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)     # 🔒 admin only
):
    image_url = None
    if image:
        # Validate file type
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(status_code=400, detail="Only JPEG/PNG/WebP allowed")

        # Save with unique filename to avoid collisions
        ext      = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_url = f"/static/uploads/{filename}"

    product = Product(
        name=name, description=description,
        price=price, stock=stock, image_url=image_url
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ADMIN ONLY — delete product
@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()