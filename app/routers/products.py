from itertools import product

from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_async_db

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(select(ProductModel).where(ProductModel.is_active == True))
    products = result.all()
    return products

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate = Body(...), db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active == True))
    category = result.first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    category = result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    stmt_for_prouducts = select(ProductModel).where(ProductModel.is_active == True, ProductModel.category_id == category.id)
    result = await db.scalars(stmt_for_prouducts)
    products = result.all()

    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return products

@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int = Path(...), db: AsyncSession = Depends(get_async_db)):
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    result = await db.scalars(stmt)
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product

@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    stmt_check_existment = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    result = await db.scalars(stmt_check_existment)
    product_db = result.first()
    if not product_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db_update = product.model_dump(exclude_unset=True)
    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(**db_update)
    )
    await db.commit()
    return db_update

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(ProductModel).where(ProductModel.id == product_id)
    result = await db.scalars(stmt)
    product = result.first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(is_active=False)
    )
    await db.commit()
    return product