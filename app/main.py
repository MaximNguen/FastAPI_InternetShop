from fastapi import FastAPI, BackgroundTasks
import time
from celery import Celery
from app.task import call_background_task

from app.routers import cart, categories, orders, products, users
from fastapi.staticfiles import StaticFiles

celery = Celery(__name__, broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/0', broker_connection_retry_on_startup=True)

app = FastAPI()
app.mount("/media", StaticFiles(directory="media"), name="media")
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(cart.router) 
app.include_router(orders.router) 

@app.get("/")
async def hello_world(message: str):
    call_background_task.apply_async(args=[message], countdown=10)
    return {'message': 'Hello World!'}