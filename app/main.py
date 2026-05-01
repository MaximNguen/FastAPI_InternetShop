from fastapi import FastAPI

from app.routers import cart, categories, products, users
app = FastAPI()
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(cart.router) 

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API интернет-магазина!"}