from itertools import product

from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Depends = Depends(get_db)) -> list[ProductSchema]:
    try:
        stmt = select(ProductModel).where(ProductModel.is_active == True)
        products = db.scalars(stmt).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate = Body(...), db: Session = Depends(get_db)):
    try:
        stmt_for_category = select(CategoryModel).where(CategoryModel.id == product.category_id and CategoryModel.is_active == True)
        category = db.execute(stmt_for_category).scalar()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found, pick other one"
            )

        db_product = ProductModel(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        raise e

@router.get("/category/{category_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int = Path(...), db: Session = Depends(get_db)):
    try:
        stmt_for_category = select(CategoryModel).where(CategoryModel.id == category_id and CategoryModel.is_active == True)
        category = db.execute(stmt_for_category).scalar()

        if not category:
            return {"message": "Category not found, pick other one"}

        stmt = select(ProductModel).where(ProductModel.category_id == category_id)
        products = db.scalars(stmt).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int = Path(...), db: Session = Depends(get_db)):
    try:
        stmt = select(CategoryModel).where(CategoryModel.id == product_id)
        products = db.scalars(stmt).all()

        if not products:
            raise HTTPException(status_code=status.HTTP_204_NOT_FOUND, detail="Product not found")

        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    try:
        stmt_check = select(ProductModel).where(ProductModel.id == product_id)
        exist_product = db.execute(stmt_check).scalar()

        if not exist_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump()))
        db.commit()
        db.refresh(exist_product)
        return exist_product
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    try:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        product = db.execute(stmt).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        db.execute(delete(ProductModel).where(ProductModel.id == product_id))
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
