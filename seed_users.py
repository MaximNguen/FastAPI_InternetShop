import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.users import User
from app.auth import hash_password
from app.database import Base
import random

# Список имен для генерации email
first_names = ["john", "jane", "mike", "sarah", "david", "emma", "alex", "lisa", "tom", "anna"]
domains = ["example.com", "test.com", "email.com", "web.com"]

async def seed_users(count: int = 100):
    engine = create_async_engine("postgresql+asyncpg://ecommerce_user:12345678@localhost:5432/ecommerce_db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        users = []
        for i in range(count):
            name = random.choice(first_names)
            email = f"{name}.{i}@{random.choice(domains)}"
            role = random.choice(["buyer", "seller"])
            
            user = User(
                email=email,
                hashed_password=hash_password("password123"),  # Общий пароль для всех
                role=role,
                is_active=True
            )
            users.append(user)
        
        session.add_all(users)
        await session.commit()
        print(f"Добавлено {count} пользователей")

if __name__ == "__main__":
    asyncio.run(seed_users(500))