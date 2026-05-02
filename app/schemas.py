from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from decimal import Decimal
from typing import Annotated


class CategoryCreate(BaseModel):
    name: Annotated[
        str,
        Field(min_length=3, max_length=50,
                      description="Название категории (3-50 символов)"),
    ]
    parent_id: Annotated[
        int | None,
        Field(None, description="ID родительской категории, если есть"),
    ]

class Category(BaseModel):
    id: Annotated[
        int,
        Field(description="Уникальный идентификатор категории")
    ]
    name: Annotated[
        str,
        Field(description="Название категории"),
    ]
    parent_id: Annotated[
        int | None,
        Field(None, description="ID родительской категории, если есть")
    ]
    is_active: Annotated[
        bool,
        Field(description="Активность категории")
    ]

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: str = Field(min_length=3, max_length=100,
                      description="Название товара (3-100 символов)")
    description: str | None = Field(None, max_length=500,
                                       description="Описание товара (до 500 символов)")
    price: Decimal = Field(gt=0, description="Цена товара (больше 0)", decimal_places=2)
    image_url: str | None = Field(None, max_length=200, description="URL изображения товара")
    stock: int = Field(ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(description="ID категории, к которой относится товар")


class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор товара")
    name: str = Field(description="Название товара")
    description: str | None = Field(None, description="Описание товара")
    price: Decimal = Field(description="Цена товара в рублях", gt=0, decimal_places=2)
    image_url: str | None = Field(None, description="URL изображения товара")
    stock: int = Field(description="Количество товара на складе")
    category_id: int = Field(description="ID категории")
    is_active: bool = Field(description="Активность товара")

    model_config = ConfigDict(from_attributes=True)
    
class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Пароль (минимум 6 символов)")
    role: str = Field(default="buyer", description="Роль пользователя (по умолчанию 'buyer')")
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
class ProductList(BaseModel):
    items: list[Product] = Field(description="Список товаров для текущей страницы")
    total: int = Field(description="Общее количество товаров", ge=0)
    page: int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")
    
    model_config = ConfigDict(from_attributes=True)  # Для чтения из ORM-объектов
    
    
class CartItemBase(BaseModel):
    product_id: int = Field(description="ID товара, который добавляется в корзину")
    quantity: int = Field(ge=1, description="Количество товара (минимум 1)")
    
class CartItemCreate(CartItemBase):
    """Модель для добавления нового товара в корзину."""
    pass

class CartItemUpdate(BaseModel):
    """Модель для обновления количества товара в корзине."""
    quantity: int = Field(ge=1, description="Новое количество товара (минимум 1)")
    
class CartItem(BaseModel):
    id: int = Field(description="Уникальный идентификатор позиции в корзине")
    user_id: int = Field(description="ID пользователя, которому принадлежит корзина")
    product_id: int = Field(description="ID товара в корзине")
    quantity: int = Field(description="Количество товара в корзине")
    
    model_config = ConfigDict(from_attributes=True)
    
class Cart(BaseModel):
    """Полная информация о корзине пользователя."""
    user_id: int = Field(..., description="ID пользователя")
    items: list[CartItem] = Field(default_factory=list, description="Содержимое корзины")
    total_quantity: int = Field(..., ge=0, description="Общее количество товаров")
    total_price: Decimal = Field(..., ge=0, description="Общая стоимость товаров")

    model_config = ConfigDict(from_attributes=True)

class OrderItem(BaseModel):
    id: int = Field(..., description="ID позиции заказа")
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., ge=1, description="Количество")
    unit_price: Decimal = Field(..., ge=0, description="Цена за единицу на момент покупки")
    total_price: Decimal = Field(..., ge=0, description="Сумма по позиции")
    product: Product | None = Field(None, description="Полная информация о товаре")

    model_config = ConfigDict(from_attributes=True)
    
class Order(BaseModel):
    id: int = Field(..., description="ID заказа")
    user_id: int = Field(..., description="ID пользователя")
    status: str = Field(..., description="Текущий статус заказа")
    total_amount: Decimal = Field(..., ge=0, description="Общая стоимость")
    created_at: datetime = Field(..., description="Когда заказ был создан")
    updated_at: datetime = Field(..., description="Когда последний раз обновлялся")
    items: list[OrderItem] = Field(default_factory=list, description="Список позиций")

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    items: list[Order] = Field(description="Список заказов для текущей страницы")
    total: int = Field(description="Общее количество заказов", ge=0)
    page: int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)