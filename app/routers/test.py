from db import session
from models import Book
from sqlalchemy import select

result = session.scalars(select(Book.title)).all()