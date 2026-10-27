from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base
class Employee(Base):

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    department = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    salary = Column(Float, nullable=False)
