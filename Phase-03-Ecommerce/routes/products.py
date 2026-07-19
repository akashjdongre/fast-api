from fastapi import APIRouter, Depends, HTTPException, File, Query, Request
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil, os, uuid
from response.response import RespAllPRoducts, RespSingleProducts, RespProductDelete
from core.redis import redis_client
from database import get_db
from models.product import Product
from core.dependencies import get_current_user, require_admin
from models.user import User
import json

router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# PUBLIC — list products with pagination & search
@router.get("/")
async def list_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    search: Optional[str] = Query(None)
):
    cache_key = f"products:{page}:{limit}"
    try:
        cached_data = await redis_client.get(cache_key)
    except Exception:
        cached_data = None

    if cached_data:
        cached_list = json.loads(cached_data)
        return {
            "total": len(cached_list),
            "results": cached_list
        }

    query = db.query(Product)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    product_list = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "image_url": p.image_url
        }
        for p in products
    ]

    try:
        await redis_client.set(cache_key, json.dumps(product_list), ex=60)
    except Exception as e:
        print(e)

    return {
        "total": total,
        "results": product_list
    }

# PUBLIC — get single product
@router.get("/{product_id}", response_model=RespSingleProducts)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# ADMIN ONLY — create product with image upload

@router.post("/", status_code=201, response_model=RespSingleProducts)
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
@router.delete("/{product_id}", status_code=200, response_model= RespProductDelete)
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

    return {"message": "Product deleted successfully", "product_info": product}

