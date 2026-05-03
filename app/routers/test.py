# app/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from app.db import get_async_db, AsyncSession
from sqlalchemy import Select, func, select
from app.models import Order as OrderModel
from app.schemas import Order as OrderSchema
from fastapi import Depends, APIRouter, HTTPException, Query, status


# Напишите в этот блок Pydantic модель OrderList в нужном для выводе формате.
class OrderList(BaseModel):
    items: list[OrderModel] = Field(description="Список заказов для текущей страницы")
    total: int = Field(description="Общее количество заказов", ge=0)
    page: int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)
# app/routers/orders.py
# Модернизируйте в этом блоке эндпоинт /orders/, принимающий GET запросы с именем функции get_all_orders, добавив в него пагинацию.

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.get("/", response_model = OrderList, status_code=status.HTTP_200_OK)
async def get_all_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, description="Статус заказа для фильтрации"),
    min_price: float | None = Query(None, ge=0, description="Минимальная цена заказа для фильтрации"),
    max_price: float | None = Query(None, ge=0, description="Максимальная цена заказа для фильтрации"),
    db: AsyncSession = Depends(get_async_db)
):
    total_stmt = select(func.count()).select_from(OrderModel).where(OrderModel.is_active == True)
    total = await db.scalar(total_stmt) or 0
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid price range")
    
    filters = [OrderModel.is_active == True]
    if status is not None:
        filters.append(OrderModel.status == status)
    if min_price is not None:
        filters.append(OrderModel.total_price >= min_price)
    if max_price is not None:
        filters.append(OrderModel.total_price <= max_price)
    
    orders_stmt = select(OrderModel).where(*filters).order_by(OrderModel.id).offset((page - 1) * page_size).limit(page_size)
    orders_result = await db.execute(orders_stmt)
    orders = orders_result.scalars().all()
    
    return {
        "items": orders,
        "total": total,
        "page": page,
        "page_size": page_size
    }