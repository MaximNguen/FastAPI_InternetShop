import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.categories import Category

async def seed_categories():
    engine = create_async_engine("postgresql+asyncpg://ecommerce_user:12345678@localhost:5432/ecommerce_db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Основные категории
        main_categories = [
            {"name": "Электроника", "is_active": True},
            {"name": "Одежда", "is_active": True},
            {"name": "Дом и сад", "is_active": True},
            {"name": "Спорт", "is_active": True},
            {"name": "Книги", "is_active": True},
            {"name": "Игрушки", "is_active": True},
            {"name": "Автотовары", "is_active": True},
            {"name": "Красота", "is_active": True},
        ]
        
        categories = []
        for cat in main_categories:
            category = Category(**cat)
            categories.append(category)
            session.add(category)
        
        await session.flush()  # Получаем ID основных категорий
        
        # Подкатегории для Электроники
        electronics = categories[0]
        sub_categories = [
            {"name": "Смартфоны", "parent_id": electronics.id},
            {"name": "Ноутбуки", "parent_id": electronics.id},
            {"name": "Планшеты", "parent_id": electronics.id},
            {"name": "Телевизоры", "parent_id": electronics.id},
            {"name": "Наушники", "parent_id": electronics.id},
        ]
        
        # Подкатегории для Одежды
        clothing = categories[1]
        sub_categories.extend([
            {"name": "Мужская одежда", "parent_id": clothing.id},
            {"name": "Женская одежда", "parent_id": clothing.id},
            {"name": "Детская одежда", "parent_id": clothing.id},
            {"name": "Обувь", "parent_id": clothing.id},
            {"name": "Аксессуары", "parent_id": clothing.id},
        ])
        
        # Добавляем подкатегории
        for sub_cat in sub_categories:
            session.add(Category(**sub_cat))
        
        # Генерация дополнительных подкатегорий для других разделов
        for _ in range(100):  # Добавляем 100 случайных подкатегорий
            random_main = random.choice(categories)
            category = Category(
                name=f"Подкатегория {random.randint(1, 1000)}",
                parent_id=random_main.id,
                is_active=True
            )
            session.add(category)
        
        await session.commit()
        print(f"Добавлены категории: {len(main_categories)} основных и подкатегории")

if __name__ == "__main__":
    import random
    asyncio.run(seed_categories())